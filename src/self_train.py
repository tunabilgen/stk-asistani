"""Self-training loop: the model learns from the news it reads.

Each run:
 1. classifies the accumulated independent news with the current model,
 2. keeps only very confident predictions as pseudo-labels (+ any human-corrected
    labels from data/feedback/labels.jsonl, which always win),
 3. retrains on HumSet + pseudo/human labels,
 4. accepts the new model ONLY if test macro-F1 on the expert-labelled HumSet test
    set does not drop by more than TOLERANCE — a guard against drift / confirmation bias.

Usage:  python -m src.self_train
"""
import json
import shutil

import pandas as pd

from src import sector_model
from src.config import DATA, LIVE, MODELS

CONFIDENCE = 0.90   # min probability for a pseudo-label
MAX_PSEUDO = 3000   # cap so pseudo-labels never dominate expert labels
TOLERANCE = 0.005   # max allowed macro-F1 drop on the expert test set
LOG = MODELS / "self_train_log.jsonl"
FEEDBACK = DATA / "feedback" / "labels.jsonl"


def pseudo_labels() -> pd.DataFrame:
    path = LIVE / "news.json"
    if not path.exists():
        return pd.DataFrame(columns=["text", "labels", "origin"])
    news = pd.DataFrame(json.loads(path.read_text(encoding="utf-8"))).drop_duplicates("id")
    news = news[news["group"] == "independent"]
    news["text"] = (news["title"] + ". " + news["text"].fillna("")).str.strip()
    news = news[news["text"].str.len() > 80]
    preds = sector_model.predict(news["text"].tolist())
    rows = []
    for text, p in zip(news["text"], preds):
        conf = [k for k, v in p["proba"].items() if v >= CONFIDENCE]
        if conf:
            rows.append({"text": text, "labels": conf, "origin": "pseudo"})
    df = pd.DataFrame(rows).head(MAX_PSEUDO)
    if FEEDBACK.exists():  # human corrections from the UI
        fb = pd.read_json(FEEDBACK, lines=True)
        fb["origin"] = "human"
        df = pd.concat([df[~df["text"].isin(fb["text"])], fb[["text", "labels", "origin"]]])
    return df


def run():
    before = json.loads(sector_model.METRICS_PATH.read_text())
    old_f1 = before["results"][-1]["macro_f1"]
    extra = pseudo_labels()
    print(f"pseudo/human labelled examples: {len(extra)} "
          f"({(extra['origin'] == 'human').sum() if len(extra) else 0} human)")
    if extra.empty:
        print("nothing new to learn from")
        return

    cand_model, cand_metrics = MODELS / "candidate.joblib", MODELS / "candidate_metrics.json"
    report = sector_model.train(extra_train=extra, model_path=cand_model,
                                metrics_path=cand_metrics)
    new_f1 = report["results"][-1]["macro_f1"]
    accepted = new_f1 >= old_f1 - TOLERANCE
    if accepted:
        shutil.copy(sector_model.MODEL_PATH, MODELS / "sector_clf.prev.joblib")
        shutil.move(cand_model, sector_model.MODEL_PATH)
        shutil.move(cand_metrics, sector_model.METRICS_PATH)
    else:
        cand_model.unlink()
        cand_metrics.unlink()
    entry = {"at": report["trained_at"], "n_extra": len(extra), "old_macro_f1": old_f1,
             "new_macro_f1": new_f1, "accepted": accepted}
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    print(("ACCEPTED" if accepted else "REJECTED (kept previous model)"), entry)


if __name__ == "__main__":
    run()
