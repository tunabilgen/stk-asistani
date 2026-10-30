"""Humanitarian sector classifier (multi-label) trained on HumSet.

Usage:  python -m src.sector_model train      # train + evaluate, writes models/
        python -m src.sector_model train-multilingual
        python -m src.sector_model predict "Cholera cases rise in displacement camps"
"""
import json
import re
import sys
import time

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score, precision_recall_fscore_support
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer

from src.config import HUMSET, HUMSET_TO_KEY, MODELS, PROCESSED, SECTORS

LABELS = list(SECTORS)  # fixed label order
MODEL_PATH = MODELS / "sector_clf.joblib"
METRICS_PATH = MODELS / "sector_metrics.json"

# Hand-written keyword baseline (EN/FR/ES stems) — the "no learning" reference point.
KEYWORDS = {
    "food": r"food|hunger|famine|ipc|ration|aliment|faim|hambre|seguridad alimentaria",
    "health": r"health|hospital|cholera|disease|outbreak|medical|clinic|vaccin|santé|salud|malaria|measles",
    "wash": r"water|sanitation|hygiene|latrine|wash\b|eau|agua|saneamiento|toilet",
    "shelter": r"shelter|tent|housing|camp|nfi|abri|logement|albergue|vivienda|refugio",
    "education": r"school|education|teacher|student|learning|école|éducation|escuela|educación",
    "protection": r"protection|violence|gbv|child|trafficking|abuse|detention|protección|violencia|enfant",
    "nutrition": r"malnutrition|nutrition|wasting|stunting|sam\b|mam\b|rutf|desnutrición",
    "livelihoods": r"livelihood|income|job|employment|cash|market|wage|emploi|empleo|ingreso",
    "agriculture": r"agricultur|crop|harvest|livestock|seed|farm|agricole|cosecha|ganado",
    "logistics": r"logistic|transport|road|airport|port\b|supply chain|fuel|convoy|carretera",
}


def _parse_labels(s) -> list[str]:
    vals = s if isinstance(s, list) else eval(s) if isinstance(s, str) else []
    return [HUMSET_TO_KEY[v] for v in vals if v in HUMSET_TO_KEY]


def load_split(name: str) -> pd.DataFrame:
    df = pd.read_json(HUMSET / f"{name}.jsonl", lines=True, dtype=False)
    df["labels"] = df["sectors"].map(_parse_labels)
    # keep excerpts annotated with at least one sector; empty = not sector-tagged by annotators
    raw = df["sectors"].map(lambda s: eval(s) if isinstance(s, str) else s)
    df = df[raw.map(len) > 0].copy()
    df["text"] = df["excerpt"].fillna("").str.strip()
    return df[df["text"].str.len() > 20][["entry_id", "lang", "text", "labels"]]


def keyword_predict(texts) -> np.ndarray:
    pats = [re.compile(KEYWORDS[k], re.I) for k in LABELS]
    return np.array([[1 if p.search(t) else 0 for p in pats] for t in texts])


def build_pipeline():
    vec = TfidfVectorizer(ngram_range=(1, 2), min_df=3, max_df=0.5, max_features=300_000,
                          sublinear_tf=True, strip_accents="unicode", lowercase=True)
    clf = OneVsRestClassifier(
        LogisticRegression(C=4.0, solver="liblinear", class_weight="balanced", max_iter=1000))
    return vec, clf


def tune_thresholds(y_true, proba) -> np.ndarray:
    """Pick the per-class probability threshold that maximises F1 on validation."""
    grid = np.arange(0.2, 0.91, 0.05)
    best = []
    for j in range(y_true.shape[1]):
        f1s = [f1_score(y_true[:, j], proba[:, j] >= t, zero_division=0) for t in grid]
        best.append(grid[int(np.argmax(f1s))])
    return np.array(best)


def evaluate(name, y_true, y_pred, extra=None) -> dict:
    p, r, f, s = precision_recall_fscore_support(y_true, y_pred, zero_division=0)
    out = {
        "model": name,
        "micro_f1": round(f1_score(y_true, y_pred, average="micro", zero_division=0), 4),
        "macro_f1": round(f1_score(y_true, y_pred, average="macro", zero_division=0), 4),
        "per_class": {LABELS[i]: {"precision": round(p[i], 3), "recall": round(r[i], 3),
                                  "f1": round(f[i], 3), "support": int(s[i])}
                      for i in range(len(LABELS))},
    }
    if extra:
        out.update(extra)
    print(f"{name:28s} micro-F1={out['micro_f1']:.3f}  macro-F1={out['macro_f1']:.3f}")
    return out


def train(extra_train: pd.DataFrame | None = None, model_path=MODEL_PATH,
          metrics_path=METRICS_PATH) -> dict:
    t0 = time.time()
    mlb = MultiLabelBinarizer(classes=LABELS)
    tr, va, te = load_split("train"), load_split("validation"), load_split("test")
    if extra_train is not None and len(extra_train):
        tr = pd.concat([tr, extra_train[["text", "labels"]]], ignore_index=True)
    print(f"train={len(tr)} val={len(va)} test={len(te)}")
    ytr, yva, yte = (mlb.fit_transform(d["labels"]) for d in (tr, va, te))

    results = [evaluate("keyword baseline", yte, keyword_predict(te["text"]))]

    vec, clf = build_pipeline()
    Xtr = vec.fit_transform(tr["text"])
    clf.fit(Xtr, ytr)
    pva = clf.predict_proba(vec.transform(va["text"]))
    pte = clf.predict_proba(vec.transform(te["text"]))
    results.append(evaluate("tfidf+logreg (t=0.5)", yte, (pte >= 0.5).astype(int)))
    thr = tune_thresholds(yva, pva)
    yhat = (pte >= thr).astype(int)
    final = evaluate("tfidf+logreg (tuned t)", yte, yhat,
                     {"thresholds": dict(zip(LABELS, thr.round(2).tolist()))})
    results.append(final)

    # Per-language breakdown: a fairness check (EN dominates training data).
    by_lang = {}
    for lang in sorted(te["lang"].unique()):
        m = (te["lang"] == lang).values
        by_lang[lang] = {"n": int(m.sum()),
                         "micro_f1": round(f1_score(yte[m], yhat[m], average="micro"), 4),
                         "macro_f1": round(f1_score(yte[m], yhat[m], average="macro"), 4)}
    print("by language:", by_lang)
    print(classification_report(yte, yhat, target_names=LABELS, zero_division=0))

    report = {"trained_at": pd.Timestamp.now("UTC").isoformat(), "n_train": len(tr),
              "n_extra": 0 if extra_train is None else len(extra_train),
              "n_test": len(te), "results": results, "by_language": by_lang,
              "seconds": round(time.time() - t0, 1)}
    joblib.dump({"vec": vec, "clf": clf, "thresholds": thr, "labels": LABELS}, model_path)
    metrics_path.write_text(json.dumps(report, indent=1), encoding="utf-8")
    _cache.clear()
    return report


_cache = {}
ML_MODEL_PATH = MODELS / "sector_clf_multilingual.joblib"
EMB_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
_TR = re.compile(r"[ğşıİĞŞ]|\b(?i:ve|bir|için|ile|olarak|değil|göre)\b")  # no global re.I: "İ" would match "i"
_AR = re.compile(r"[؀-ۿ]")


def detect_lang(text: str) -> str:
    """Coarse script/word check: 'ar', 'tr' or 'latin' (EN/FR/ES, the languages HumSet covers)."""
    if len(_AR.findall(text)) > 10:
        return "ar"
    return "tr" if len(_TR.findall(text)) >= 3 else "latin"


def train_multilingual():
    """Frozen multilingual sentence embeddings + logistic regression (Assignment 2 model comparison).

    Slightly below TF-IDF on EN/FR/ES (macro-F1 0.70 vs 0.74) but works on languages missing from
    HumSet: micro-F1 0.70 on Turkish and Arabic vs 0.34 / 0.20 for TF-IDF (src/multilingual_eval.py).
    """
    from sentence_transformers import SentenceTransformer
    mlb = MultiLabelBinarizer(classes=LABELS)
    tr, va = load_split("train"), load_split("validation")
    enc = SentenceTransformer(EMB_MODEL, device="cpu")
    enc.max_seq_length = 128
    emb = {}
    for name, d in (("train", tr), ("val", va)):  # reuse embeddings cached by src.compare_models
        p = PROCESSED / f"emb_{name}.npy"
        emb[name] = np.load(p) if p.exists() else enc.encode(d["text"].tolist(), batch_size=128,
                                                              normalize_embeddings=True, show_progress_bar=True)
    clf = OneVsRestClassifier(LogisticRegression(C=2.0, class_weight="balanced", max_iter=2000))
    clf.fit(emb["train"], mlb.fit_transform(tr["labels"]))
    thr = tune_thresholds(mlb.transform(va["labels"]), clf.predict_proba(emb["val"]))
    joblib.dump({"clf": clf, "thresholds": thr, "labels": LABELS, "encoder": EMB_MODEL}, ML_MODEL_PATH)
    print("saved", ML_MODEL_PATH)


def load():
    if "m" not in _cache:
        _cache["m"] = joblib.load(MODEL_PATH)
    return _cache["m"]


def _proba_multilingual(texts: list[str]):
    if "ml" not in _cache:
        from sentence_transformers import SentenceTransformer
        m = joblib.load(ML_MODEL_PATH)
        enc = SentenceTransformer(m["encoder"], device="cpu")
        enc.max_seq_length = 128
        _cache["ml"] = (m, enc)
    m, enc = _cache["ml"]
    return m, m["clf"].predict_proba(enc.encode(texts, batch_size=64, normalize_embeddings=True))


def predict(texts: list[str]) -> list[dict]:
    """Return {sector: probability}, the sectors above threshold and the model used, per text.

    Language router: TF-IDF + logistic regression for EN/FR/ES (best there); the multilingual
    embedding model for Turkish and Arabic, which TF-IDF cannot read (if that model is trained).
    """
    m = load()
    langs = [detect_lang(t) for t in texts]
    out = [None] * len(texts)
    ml_idx = [i for i, l in enumerate(langs) if l != "latin"] if ML_MODEL_PATH.exists() else []
    groups = [(m, [i for i in range(len(texts)) if i not in set(ml_idx)], "tfidf")]
    if ml_idx:
        mm, pr = _proba_multilingual([texts[i] for i in ml_idx])
        groups.append((mm, ml_idx, "multilingual", pr))
    for g in groups:
        model, idx, name = g[0], g[1], g[2]
        if not idx:
            continue
        proba = g[3] if len(g) > 3 else model["clf"].predict_proba(model["vec"].transform([texts[i] for i in idx]))
        for i, row in zip(idx, proba):
            out[i] = {"proba": {k: round(float(p), 3) for k, p in zip(model["labels"], row)},
                      "sectors": [k for k, p, t in zip(model["labels"], row, model["thresholds"]) if p >= t],
                      "model": name, "lang": langs[i]}
    return out


if __name__ == "__main__":
    if sys.argv[1:2] == ["train"]:
        train()
    elif sys.argv[1:2] == ["train-multilingual"]:
        train_multilingual()
    elif sys.argv[1:2] == ["predict"]:
        for t, r in zip(sys.argv[2:], predict(sys.argv[2:])):
            top = sorted(r["proba"].items(), key=lambda x: -x[1])[:3]
            print(t, "->", r["sectors"], top)
