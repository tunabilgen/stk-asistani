"""Crisis-dynamics classifier trained on HumSet "pillars" (multi-label).

Detects whether a report describes casualties, displacement, a shock/event or access
constraints. Used to measure *conflict* acuteness from live news, which disaster-alert
feeds (USGS/NASA EONET) do not cover.

Usage:  python -m src.pillar_model train
"""
import ast
import json
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score
from sklearn.preprocessing import MultiLabelBinarizer

from src.config import HUMSET, MODELS
from src.sector_model import build_pipeline, tune_thresholds

LABELS = ["Casualties", "Displacement", "Shock/Event", "Humanitarian Access"]
MODEL_PATH = MODELS / "pillar_clf.joblib"
METRICS_PATH = MODELS / "pillar_metrics.json"


def load_split(name):
    df = pd.read_json(HUMSET / f"{name}.jsonl", lines=True, dtype=False)
    raw = df["pillars_1d"].map(lambda s: ast.literal_eval(s) if isinstance(s, str) else s)
    df["labels"] = raw.map(lambda xs: [x for x in xs if x in LABELS])
    df["text"] = df["excerpt"].fillna("").str.strip()
    # keep only excerpts annotated on the 1D-pillar axis, so "no label" is a true negative
    return df[(raw.map(len) > 0) & (df["text"].str.len() > 20)]


def train():
    mlb = MultiLabelBinarizer(classes=LABELS)
    tr, va, te = load_split("train"), load_split("validation"), load_split("test")
    ytr, yva, yte = (mlb.fit_transform(d["labels"]) for d in (tr, va, te))
    vec, clf = build_pipeline()
    clf.fit(vec.fit_transform(tr["text"]), ytr)
    thr = tune_thresholds(yva, clf.predict_proba(vec.transform(va["text"])))
    yhat = (clf.predict_proba(vec.transform(te["text"])) >= thr).astype(int)
    per = f1_score(yte, yhat, average=None, zero_division=0)
    rep = {"micro_f1": round(f1_score(yte, yhat, average="micro"), 4),
           "macro_f1": round(f1_score(yte, yhat, average="macro"), 4),
           "per_class": dict(zip(LABELS, np.round(per, 3).tolist())),
           "thresholds": dict(zip(LABELS, thr.round(2).tolist())), "n_train": len(tr)}
    print(rep)
    joblib.dump({"vec": vec, "clf": clf, "thresholds": thr, "labels": LABELS}, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(rep, indent=1), encoding="utf-8")


_cache = {}


def predict_proba(texts: list[str]) -> list[dict]:
    if "m" not in _cache:
        _cache["m"] = joblib.load(MODEL_PATH)
    m = _cache["m"]
    proba = m["clf"].predict_proba(m["vec"].transform(texts))
    return [{k: float(p) for k, p in zip(m["labels"], row)} for row in proba]


if __name__ == "__main__" and sys.argv[1:2] == ["train"]:
    train()
