"""Assignment 2 — does the sector classifier work on Turkish and Arabic text? (instructor feedback)

HumSet has no Turkish or Arabic excerpts, so we build a labelled test set by machine-translating
English HumSet *test* excerpts (labels carry over, the excerpts were never seen in training)
with open MarianMT models (Helsinki-NLP OPUS-MT, run locally). Then every model is scored on
the same excerpts in English, Turkish and Arabic.

Usage:  python -m src.multilingual_eval translate   -> data/final/humset_test_tr_ar.csv
        python -m src.multilingual_eval evaluate    -> reports/multilingual_eval.json
"""
import json
import sys
import time

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer

from src.config import PROCESSED, ROOT
from src.sector_model import LABELS, keyword_predict, load_split, predict, tune_thresholds

N, SEED = 300, 7
OUT_CSV = ROOT / "data/final/humset_test_tr_ar.csv"
OUT_JSON = ROOT / "reports/multilingual_eval.json"
MT = {"tr": "Helsinki-NLP/opus-mt-tc-big-en-tr", "ar": "Helsinki-NLP/opus-mt-tc-big-en-ar"}


def translate():
    from transformers import MarianMTModel, MarianTokenizer
    te = load_split("test")
    te = te[(te["lang"] == "en") & te["text"].str.len().between(80, 1200)]
    sub = te.sample(N, random_state=SEED).reset_index(drop=True)
    for lang, name in MT.items():
        tok, model = MarianTokenizer.from_pretrained(name), MarianMTModel.from_pretrained(name)
        t0, out = time.time(), []
        for i in range(0, N, 8):
            batch = sub["text"].iloc[i:i + 8].tolist()
            if lang == "ar":  # multi-target OPUS-MT models need the target-language token
                batch = [">>ara<< " + b for b in batch]
            enc = tok(batch, return_tensors="pt", padding=True, truncation=True, max_length=256)
            out += tok.batch_decode(model.generate(**enc, max_new_tokens=320, num_beams=2), skip_special_tokens=True)
            print(lang, i + 8, f"{time.time() - t0:.0f}s", flush=True)
        sub[f"text_{lang}"] = out
    sub["labels"] = sub["labels"].map(json.dumps)
    sub.rename(columns={"text": "text_en"})[["entry_id", "labels", "text_en", "text_tr", "text_ar"]].to_csv(
        OUT_CSV, index=False, encoding="utf-8")
    print("saved", OUT_CSV)


def _embedding_clf():
    """Re-fit the frozen-embedding classifier from the cached HumSet embeddings (src.compare_models embed)."""
    from sentence_transformers import SentenceTransformer
    from src.compare_models import EMB_MODEL
    mlb = MultiLabelBinarizer(classes=LABELS)
    tr, va = load_split("train"), load_split("validation")
    Etr, Eva = np.load(PROCESSED / "emb_train.npy"), np.load(PROCESSED / "emb_val.npy")
    clf = OneVsRestClassifier(LogisticRegression(C=2.0, class_weight="balanced", max_iter=2000))
    clf.fit(Etr, mlb.fit_transform(tr["labels"]))
    thr = tune_thresholds(mlb.transform(va["labels"]), clf.predict_proba(Eva))
    enc = SentenceTransformer(EMB_MODEL, device="cpu"); enc.max_seq_length = 128
    return lambda texts: (clf.predict_proba(enc.encode(list(texts), batch_size=64, normalize_embeddings=True)) >= thr).astype(int)


def _tfidf_only(texts):
    from src.sector_model import load
    m = load()
    return (m["clf"].predict_proba(m["vec"].transform(list(texts))) >= m["thresholds"]).astype(int)


def evaluate():
    df = pd.read_csv(OUT_CSV)
    y = MultiLabelBinarizer(classes=LABELS).fit_transform(df["labels"].map(json.loads))
    models = {
        "Keyword rules": keyword_predict,
        "TF-IDF + LogReg": _tfidf_only,
        "Multilingual embeddings + LogReg": _embedding_clf(),
        "App: language router (TF-IDF for EN/FR/ES, multilingual otherwise)":
            lambda t: np.array([[1 if s in p["sectors"] else 0 for s in LABELS] for p in predict(list(t))]),
    }
    res = {"n": len(df), "source": "English HumSet test excerpts, machine-translated with OPUS-MT", "scores": {}}
    for name, f in models.items():
        res["scores"][name] = {}
        for lang in ["en", "tr", "ar"]:
            yhat = f(df[f"text_{lang}"])
            res["scores"][name][lang] = {"micro_f1": round(float(f1_score(y, yhat, average="micro", zero_division=0)), 3),
                                         "macro_f1": round(float(f1_score(y, yhat, average="macro", zero_division=0)), 3)}
        print(f"{name:35s}", {l: v["micro_f1"] for l, v in res["scores"][name].items()})
    OUT_JSON.write_text(json.dumps(res, indent=1), encoding="utf-8")


if __name__ == "__main__":
    {"translate": translate, "evaluate": evaluate}[sys.argv[1]]()
