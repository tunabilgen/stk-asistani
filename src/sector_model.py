"""Humanitarian sector classifier (multi-label) trained on HumSet.

Usage:  python -m src.sector_model train      # train + evaluate, writes models/
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


def load():
    if "m" not in _cache:
        _cache["m"] = joblib.load(MODEL_PATH)
    return _cache["m"]


def predict(texts: list[str]) -> list[dict]:
    """Return {sector: probability} and the list of sectors above threshold, per text."""
    m = load()
    proba = m["clf"].predict_proba(m["vec"].transform(texts))
    out = []
    for row in proba:
        out.append({"proba": {k: round(float(p), 3) for k, p in zip(m["labels"], row)},
                    "sectors": [k for k, p, t in zip(m["labels"], row, m["thresholds"]) if p >= t]})
    return out


if __name__ == "__main__":
    if sys.argv[1:2] == ["train"]:
        train()
    elif sys.argv[1:2] == ["predict"]:
        for t, r in zip(sys.argv[2:], predict(sys.argv[2:])):
            top = sorted(r["proba"].items(), key=lambda x: -x[1])[:3]
            print(t, "->", r["sectors"], top)
