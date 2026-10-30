"""Assignment 2 — compare model families for the sector classifier on the same HumSet test set.

Approaches (all multi-label, 10 sectors, evaluated on the official HumSet test split):
  1. keyword rules                    — no learning (baseline)
  2. TF-IDF + Complement Naive Bayes  — simplest learned model
  3. TF-IDF + linear SVM              — strong linear model
  4. TF-IDF + logistic regression     — the model used in the prototype
  5. multilingual sentence embeddings (frozen transformer) + logistic regression
  6. fine-tuned multilingual transformer (MiniLM, CPU, training subset)
  7. LLM zero-shot (DeepSeek via OpenRouter, 200 test excerpts)

Every learned model gets per-class thresholds tuned on the validation split (same rule for all).

Usage:  python -m src.compare_models classic | embed | finetune | llm | report
Results accumulate in reports/model_comparison.json.
"""
import json
import re
import sys
import time

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.multiclass import OneVsRestClassifier
from sklearn.naive_bayes import ComplementNB
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.svm import LinearSVC

from src.config import FIGURES, LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, PROCESSED, ROOT, SECTORS, USER_AGENT
from src.sector_model import LABELS, build_pipeline, keyword_predict, load_split, tune_thresholds

OUT = ROOT / "reports" / "model_comparison.json"
EMB_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
FT_MODEL = "microsoft/Multilingual-MiniLM-L12-H384"
SEED = 42


def _data():
    mlb = MultiLabelBinarizer(classes=LABELS)
    tr, va, te = load_split("train"), load_split("validation"), load_split("test")
    ytr, yva, yte = (mlb.fit_transform(d["labels"]) for d in (tr, va, te))
    return tr, va, te, ytr, yva, yte


def _scores(name, yte, yhat, te, seconds, notes="", n_test=None):
    r = {"model": name,
         "micro_f1": round(float(f1_score(yte, yhat, average="micro", zero_division=0)), 4),
         "macro_f1": round(float(f1_score(yte, yhat, average="macro", zero_division=0)), 4),
         "per_class_f1": dict(zip(LABELS, np.round(f1_score(yte, yhat, average=None, zero_division=0), 3).tolist())),
         "by_language_macro_f1": {l: round(float(f1_score(yte[(te["lang"] == l).values], yhat[(te["lang"] == l).values],
                                                           average="macro", zero_division=0)), 4)
                                  for l in sorted(te["lang"].unique())},
         "n_test": int(n_test or len(yte)), "train_seconds": round(seconds, 1), "notes": notes}
    print(f"{name:45s} micro={r['micro_f1']:.3f} macro={r['macro_f1']:.3f}  {r['by_language_macro_f1']}  ({seconds:.0f}s)")
    return r


def _save(rows):
    old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else []
    names = {r["model"] for r in rows}
    OUT.write_text(json.dumps([r for r in old if r["model"] not in names] + rows, indent=1), encoding="utf-8")


def _tuned(score_va, yva, score_te):
    thr = tune_thresholds(yva, score_va)
    return (score_te >= thr).astype(int)


def classic():
    tr, va, te, ytr, yva, yte = _data()
    rows = [_scores("1. Keyword rules (baseline)", yte, keyword_predict(te["text"]), te, 0,
                    "hand-written EN/FR/ES keyword patterns, no learning")]
    vec, lr = build_pipeline()
    t0 = time.time()
    Xtr = vec.fit_transform(tr["text"]); Xva, Xte = vec.transform(va["text"]), vec.transform(te["text"])
    tvec = time.time() - t0

    t0 = time.time()
    nb = OneVsRestClassifier(ComplementNB(alpha=0.3)).fit(Xtr, ytr)
    rows.append(_scores("2. TF-IDF + Complement Naive Bayes", yte,
                        _tuned(nb.predict_proba(Xva), yva, nb.predict_proba(Xte)), te, tvec + time.time() - t0))

    t0 = time.time()
    svm = OneVsRestClassifier(LinearSVC(C=0.5, class_weight="balanced")).fit(Xtr, ytr)
    sig = lambda z: 1 / (1 + np.exp(-z))  # map margins to (0,1) so the same threshold grid applies
    rows.append(_scores("3. TF-IDF + linear SVM", yte,
                        _tuned(sig(svm.decision_function(Xva)), yva, sig(svm.decision_function(Xte))), te,
                        tvec + time.time() - t0))

    t0 = time.time()
    lr.fit(Xtr, ytr)
    rows.append(_scores("4. TF-IDF + logistic regression (prototype)", yte,
                        _tuned(lr.predict_proba(Xva), yva, lr.predict_proba(Xte)), te, tvec + time.time() - t0,
                        "used in the app: interpretable, retrains in minutes, self-training loop"))
    _save(rows)


def _embed(texts, name):
    from sentence_transformers import SentenceTransformer
    path = PROCESSED / f"emb_{name}.npy"
    if path.exists():
        return np.load(path)
    m = SentenceTransformer(EMB_MODEL, device="cpu")
    m.max_seq_length = 128
    E = m.encode(list(texts), batch_size=128, show_progress_bar=True, normalize_embeddings=True)
    np.save(path, E)
    return E


def embed():
    tr, va, te, ytr, yva, yte = _data()
    t0 = time.time()
    Etr, Eva, Ete = _embed(tr["text"], "train"), _embed(va["text"], "val"), _embed(te["text"], "test")
    clf = OneVsRestClassifier(LogisticRegression(C=2.0, class_weight="balanced", max_iter=2000), n_jobs=1)
    clf.fit(Etr, ytr)
    _save([_scores("5. Multilingual MiniLM embeddings (frozen) + LogReg", yte,
                   _tuned(clf.predict_proba(Eva), yva, clf.predict_proba(Ete)), te, time.time() - t0,
                   f"{EMB_MODEL}, 384-d sentence vectors, max 128 tokens")])


def finetune(n_train=12000, epochs=2):
    import torch
    from torch.utils.data import DataLoader
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, XLMRobertaTokenizer

    torch.manual_seed(SEED)
    torch.set_num_threads(max(1, torch.get_num_threads()))
    tr, va, te, ytr, yva, yte = _data()
    idx = np.random.default_rng(SEED).choice(len(tr), size=min(n_train, len(tr)), replace=False)
    try:
        tok = AutoTokenizer.from_pretrained(FT_MODEL)
    except Exception:  # this checkpoint ships the XLM-R sentencepiece vocabulary
        tok = XLMRobertaTokenizer.from_pretrained("xlm-roberta-base")
    model = AutoModelForSequenceClassification.from_pretrained(
        FT_MODEL, num_labels=len(LABELS), problem_type="multi_label_classification")

    def batches(texts, y=None, bs=32, shuffle=False):
        order = np.random.default_rng(SEED).permutation(len(texts)) if shuffle else np.arange(len(texts))
        for i in range(0, len(texts), bs):
            j = order[i:i + bs]
            enc = tok([texts[k] for k in j], truncation=True, max_length=128, padding=True, return_tensors="pt")
            yield enc, (None if y is None else torch.tensor(y[j], dtype=torch.float32))

    xtr, ysub = tr["text"].iloc[idx].tolist(), ytr[idx]
    pos = ysub.mean(0).clip(1e-3)
    loss_fn = torch.nn.BCEWithLogitsLoss(pos_weight=torch.tensor((1 - pos) / pos, dtype=torch.float32).sqrt())
    opt = torch.optim.AdamW(model.parameters(), lr=5e-5, weight_decay=0.01)
    steps = epochs * int(np.ceil(len(xtr) / 32))
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=5e-5, total_steps=steps, pct_start=0.1)
    t0 = time.time(); step = 0
    model.train()
    for ep in range(epochs):
        for enc, yb in batches(xtr, ysub, shuffle=True):
            loss = loss_fn(model(**enc).logits, yb)
            loss.backward(); opt.step(); sched.step(); opt.zero_grad(); step += 1
            if step % 50 == 0:
                print(f"epoch {ep + 1} step {step}/{steps} loss {loss.item():.3f} ({time.time() - t0:.0f}s)", flush=True)
    model.eval()

    def proba(texts):
        out = []
        with torch.no_grad():
            for enc, _ in batches(texts, bs=64):
                out.append(torch.sigmoid(model(**enc).logits).numpy())
        return np.vstack(out)

    pva, pte = proba(va["text"].tolist()), proba(te["text"].tolist())
    _save([_scores("6. Fine-tuned multilingual MiniLM (transformer)", yte, _tuned(pva, yva, pte), te,
                   time.time() - t0, f"{FT_MODEL}, {len(xtr):,} training excerpts (CPU budget), {epochs} epochs")])


LLM_PROMPT = """You label humanitarian report excerpts with sectors.
Sectors (use these exact keys): {keys}.
Definitions: food = food security, access to food, prices, famine; health = disease, health services;
wash = water, sanitation, hygiene; shelter = housing, shelter, non-food items; education = schools, learning;
protection = violence against civilians, GBV, child protection, legal rights, detention;
nutrition = malnutrition, feeding of children/mothers; livelihoods = income, jobs, cash, markets;
agriculture = crops, livestock, farming inputs; logistics = transport, supply chains, fuel, access routes.
An excerpt can have several sectors. Answer ONLY with a JSON list of keys, e.g. ["food","health"].

Excerpt:
\"\"\"{text}\"\"\""""


def llm(n=200):
    import requests
    if not LLM_API_KEY:
        sys.exit("No LLM_API_KEY in .env — add your OpenRouter key first.")
    tr, va, te, ytr, yva, yte = _data()
    idx = np.random.default_rng(SEED).choice(len(te), size=n, replace=False)
    sub, ysub = te.iloc[idx].reset_index(drop=True), yte[idx]
    keys = ", ".join(LABELS)
    cache_p = PROCESSED / "llm_zero_shot_cache.json"
    cache = json.loads(cache_p.read_text(encoding="utf-8")) if cache_p.exists() else {}
    t0, fails = time.time(), 0
    for i, row in sub.iterrows():
        k = str(row["entry_id"])
        if k in cache:
            continue
        try:
            r = requests.post(LLM_BASE_URL.rstrip("/") + "/chat/completions", timeout=90,
                              headers={"Authorization": f"Bearer {LLM_API_KEY}", "User-Agent": USER_AGENT},
                              json={"model": LLM_MODEL, "temperature": 0,
                                    "messages": [{"role": "user", "content": LLM_PROMPT.format(keys=keys, text=row["text"][:2000])}]})
            r.raise_for_status()
            cache[k] = r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            fails += 1; print("fail", i, str(e)[:120])
            continue
        if i % 20 == 0:
            print(i, cache[k][:80], flush=True)
            cache_p.write_text(json.dumps(cache), encoding="utf-8")
    cache_p.write_text(json.dumps(cache), encoding="utf-8")

    def parse(s):
        found = re.findall(r'"?([a-z]+)"?', (s or "").lower())
        return [1 if k in found else 0 for k in LABELS]
    keep = [i for i in range(n) if str(sub.loc[i, "entry_id"]) in cache]
    yhat = np.array([parse(cache[str(sub.loc[i, "entry_id"])]) for i in keep])
    # the same 200 excerpts scored with the prototype model, for a fair side-by-side
    from src.sector_model import predict
    ylr = np.array([[1 if s in p["sectors"] else 0 for s in LABELS] for p in predict(sub.loc[keep, "text"].tolist())])
    _save([_scores(f"7. LLM zero-shot ({LLM_MODEL})", ysub[keep], yhat, sub.loc[keep], time.time() - t0,
                   f"no training; {len(keep)} random test excerpts; prompt in src/compare_models.py", len(keep)),
           _scores("4b. TF-IDF + LogReg on the same LLM sample", ysub[keep], ylr, sub.loc[keep], 0,
                   "same excerpts as the LLM row, for a like-for-like comparison", len(keep))])


def report():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = sorted(json.loads(OUT.read_text(encoding="utf-8")), key=lambda r: r["model"])
    for r in rows:
        print(f"{r['model']:55s} {r['micro_f1']:.3f} {r['macro_f1']:.3f} n={r['n_test']}")
    full = [r for r in rows if r["n_test"] > 1000]
    fig, ax = plt.subplots(figsize=(9, 0.55 * len(full) + 1.2))
    y = np.arange(len(full))[::-1]
    ax.barh(y + 0.2, [r["micro_f1"] for r in full], 0.4, color="#b23a2e", label="micro-F1")
    ax.barh(y - 0.2, [r["macro_f1"] for r in full], 0.4, color="#9a9a9a", label="macro-F1")
    for yy, r in zip(y, full):
        ax.text(r["micro_f1"] + 0.005, yy + 0.2, f"{r['micro_f1']:.3f}", va="center", fontsize=8)
        ax.text(r["macro_f1"] + 0.005, yy - 0.2, f"{r['macro_f1']:.3f}", va="center", fontsize=8)
    ax.set_yticks(y, [r["model"] for r in full], fontsize=9)
    ax.set_xlim(0, 1); ax.set_xlabel(f"F1 on the HumSet test set ({full[0]['n_test']:,} excerpts)")
    ax.legend(loc="lower right", frameon=False); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(FIGURES / "model_comparison.png", dpi=160)
    print("saved", FIGURES / "model_comparison.png")


if __name__ == "__main__":
    {"classic": classic, "embed": embed, "finetune": finetune, "llm": llm, "report": report}[sys.argv[1]]()
