"""Exploratory Data Analysis for Assignment 1.

Writes figures to reports/figures/ and a summary to reports/eda_summary.md.
Usage:  python -m src.eda
"""
import ast
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src import features
from src.config import FIGURES, HUMSET, LIVE, PROCESSED, ROOT, SECTORS, WEB_DATA

plt.rcParams.update({"figure.dpi": 130, "font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.titleweight": "bold"})
ACCENT, GREY = "#e8673a", "#8d9ab5"
lines = ["# EDA summary (auto-generated)\n"]


def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIGURES / name, bbox_inches="tight")
    plt.close(fig)
    lines.append(f"![{name}](figures/{name})\n")


def humset():
    lines.append("## 1. HumSet (training data for the sector classifier)\n")
    frames = []
    for split in ("train", "validation", "test"):
        d = pd.read_json(HUMSET / f"{split}.jsonl", lines=True, dtype=False)
        d["split"] = split
        frames.append(d)
    df = pd.concat(frames, ignore_index=True)
    df["sectors"] = df["sectors"].map(lambda s: ast.literal_eval(s) if isinstance(s, str) else s)
    df["n_sec"] = df["sectors"].map(len)
    df["len"] = df["excerpt"].fillna("").str.split().map(len)
    n = len(df)
    lines.extend([f"- Rows: **{n:,}** excerpts from {df['lead_id'].nunique():,} documents, "
              f"{df['project_id'].nunique()} humanitarian response projects.",
              f"- Languages: {df['lang'].value_counts().to_dict()}",
              f"- Missing/empty excerpt: {(df['excerpt'].fillna('').str.len() == 0).sum()}; "
              f"duplicated excerpts: {df['excerpt'].duplicated().sum():,}",
              f"- Excerpts **without any sector label**: {(df['n_sec'] == 0).mean():.1%} "
              "(dropped for training — annotators tagged only pillars there).",
              f"- Labels per labelled excerpt: mean {df.loc[df.n_sec > 0, 'n_sec'].mean():.2f}, "
              f"max {df['n_sec'].max()} → genuinely multi-label.",
              f"- Excerpt length (words): median {df['len'].median():.0f}, "
              f"95th pct {df['len'].quantile(.95):.0f}\n"])

    lab = df[df.n_sec > 0].explode("sectors")["sectors"].value_counts()
    fig, ax = plt.subplots(figsize=(6.5, 3.4))
    ax.barh(lab.index[::-1], lab.values[::-1], color=[ACCENT if x != "Cross" else GREY for x in lab.index[::-1]])
    ax.set_title("HumSet: excerpts per sector (class imbalance)")
    ax.set_xlabel("excerpts")
    save(fig, "humset_sectors.png")
    lines.append(f"Imbalance ratio largest/smallest sector: **{lab.max() / lab.min():.0f}×** "
                 f"({lab.idxmax()} vs {lab.idxmin()}) → class weighting + per-class thresholds.\n")

    keys = [v[2] for v in SECTORS.values()]
    m = np.zeros((len(keys), len(keys)))
    for secs in df["sectors"]:
        s = [keys.index(x) for x in secs if x in keys]
        for i in s:
            for j in s:
                m[i, j] += 1
    norm = m / np.maximum(m.diagonal()[:, None], 1)
    fig, ax = plt.subplots(figsize=(5.6, 4.6))
    im = ax.imshow(norm, cmap="OrRd", vmin=0, vmax=0.6)
    ax.set_xticks(range(len(keys)), keys, rotation=60, ha="right")
    ax.set_yticks(range(len(keys)), keys)
    ax.set_title("Sector co-occurrence P(col | row)")
    fig.colorbar(im, ax=ax, shrink=0.8)
    save(fig, "humset_cooccurrence.png")
    off = [(keys[i], keys[j], norm[i, j]) for i in range(len(keys)) for j in range(len(keys)) if i != j]
    top = sorted(off, key=lambda x: -x[2])[:3]
    lines.append("Strongest co-occurrences: " + "; ".join(f"{a}→{b} {p:.0%}" for a, b, p in top) + "\n")

    fig, axs = plt.subplots(1, 2, figsize=(8, 2.8))
    axs[0].hist(df["len"].clip(upper=300), bins=50, color=ACCENT)
    axs[0].set_title("Excerpt length (words, clipped at 300)")
    df["lang"].value_counts().plot.bar(ax=axs[1], color=[ACCENT, GREY, GREY])
    axs[1].set_title("Language")
    axs[1].tick_params(axis="x", rotation=0)
    save(fig, "humset_length_lang.png")
    df["year"] = df["created_at"].str[:4]
    lines.append(f"- Annotation years: {df['year'].value_counts().sort_index().to_dict()} "
                 "→ older crises dominate; live news may drift (motivates self-training).\n")


def independent():
    lines.append("## 2. Independent (non-UN) crisis data\n")
    ucdp = pd.read_parquet(PROCESSED / "ucdp_events.parquet")
    ghi = pd.read_parquet(PROCESSED / "ghi.parquet")
    app = pd.read_parquet(PROCESSED / "ifrc_appeals.parquet")
    soc = pd.read_parquet(PROCESSED / "ifrc_societies.parquet")
    t4p = pd.read_parquet(PROCESSED / "t4p_daily.parquet")
    cov = pd.DataFrame({
        "source": ["UCDP GED 26.1 + candidate 2026 (Uppsala Univ.)", "Global Hunger Index 2026",
                   "IFRC GO active appeals", "IFRC national societies",
                   "Tech for Palestine (Gaza MoH daily)"],
        "rows": [len(ucdp), len(ghi), len(app), len(soc), len(t4p)],
        "countries": [ucdp["country"].nunique(), len(ghi), app["iso3"].nunique(),
                      soc["iso3"].nunique(), 1],
        "period": [f"2016 – {ucdp['date_start'].max()}", "2021–2026 data",
                   "active today", "current", f"{t4p['report_date'].min()} – {t4p['report_date'].max()}"],
    })
    lines.append(cov.to_markdown(index=False) + "\n")
    lines.append("→ **Coverage gaps**: GHI gives only provisional categories for Sudan, South Sudan, Yemen, Burundi (used at range midpoint) "
                 "and does not cover Palestine (starvation deaths from Gaza MoH data used instead); "
                 "GHI does not score every country (e.g. Palestine); UCDP codes Gaza events under "
                 "Israel (we re-assign them by admin-1). Gaps are recorded in `data/known_gaps.json` and shown "
                 "in the UI; missing data is never scored as 'no need'.\n")

    lk = features.name_lookup()
    ucdp["iso3"] = features.to_iso(ucdp["country"], lk)
    ucdp.loc[ucdp["adm_1"].fillna("").str.contains("Gaza|West Bank", case=False), "iso3"] = "PSE"
    ucdp["d"] = pd.to_datetime(ucdp["date_start"])
    recent = ucdp[ucdp["d"] > ucdp["d"].max() - pd.Timedelta(days=3 * 365)]
    top = recent.groupby("iso3")["best"].sum().sort_values().tail(15)
    names = pd.read_parquet(PROCESSED / "countries.parquet").set_index("iso3")["name"]
    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.barh([names.get(i, i) for i in top.index], top.values / 1e3, color=ACCENT)
    ax.set_title("Conflict deaths, last 3 years (UCDP best estimate, thousands)")
    save(fig, "ucdp_top15.png")
    lines.append("- Top conflict-death countries (3 y): " + ", ".join(
        f"{names.get(i, i)} {v:,.0f}" for i, v in top.sort_values(ascending=False).head(6).items()) + "\n")

    yr = ucdp.groupby([ucdp["d"].dt.year, "type_of_violence"])["best"].sum().unstack(fill_value=0)
    yr.columns = ["state-based", "non-state", "one-sided (vs civilians)"][:len(yr.columns)]
    fig, ax = plt.subplots(figsize=(7, 3))
    yr.plot.bar(stacked=True, ax=ax, color=[ACCENT, GREY, "#c2185b"], width=0.8)
    ax.set_xlabel("")
    ax.set_title("Organised-violence deaths per year (UCDP; current year partial)")
    ax.legend(frameon=False, fontsize=8)
    save(fig, "ucdp_trend.png")

    fig, ax = plt.subplots(figsize=(6, 2.8))
    ax.hist(ghi["ghi_2026"], bins=25, color=ACCENT)
    for x, lab in [(20, "serious"), (35, "alarming")]:
        ax.axvline(x, color="k", ls="--", lw=0.8)
        ax.text(x + 0.5, ax.get_ylim()[1] * 0.85, lab, fontsize=7)
    ax.set_title("Global Hunger Index 2026 (scored countries)")
    save(fig, "ghi_hist.png")
    lines.append(f"- GHI ≥ 20 (serious or worse): **{(ghi.ghi_2026 >= 20).sum()}** countries; "
                 f"≥ 35 (alarming): {(ghi.ghi_2026 >= 35).sum()}\n")
    ea = app[app["requested"] > 0]
    lines.append(f"- IFRC active appeals: {len(app)} ({(app.type == 'Emergency Appeal').sum()} emergency appeals), "
                 f"requested CHF {ea.requested.sum() / 1e6:,.0f}M, funded **{ea.funded.sum() / ea.requested.sum():.0%}**\n")


def live_and_scores():
    lines.append("## 3. News: independent vs Western coverage, and resulting scores\n")
    nw = pd.DataFrame(json.loads((LIVE / "news.json").read_text(encoding="utf-8"))).drop_duplicates("id")
    lines.append(f"- News items collected: **{len(nw):,}** from {nw['source'].nunique()} outlets "
                 f"({(nw.group == 'independent').sum()} independent, {(nw.group == 'western').sum()} Western); "
                 f"{(nw.iso3s.map(len) > 0).mean():.0%} tagged with ≥1 country by the gazetteer.\n")

    dash = json.loads((WEB_DATA / "dashboard.json").read_text(encoding="utf-8"))
    c = pd.DataFrame([{"iso3": x["iso3"], "name": x["name"], "prot": x["score"]["protracted"],
                       "att_w": x["score"]["att_western"], "indep": x["ind"]["news_independent"],
                       "west": x["ind"]["news_western"], "ignored": x["forgotten"]} for x in dash["countries"]])
    hi = c.dropna(subset=["prot"]).sort_values("prot", ascending=False).head(15)
    tot_i, tot_w = c["indep"].sum() or 1, c["west"].sum() or 1
    hi = hi.assign(sh_i=hi["indep"] / tot_i * 100, sh_w=hi["west"] / tot_w * 100)
    fig, ax = plt.subplots(figsize=(7, 4))
    y = np.arange(len(hi))
    ax.barh(y + 0.2, hi["sh_i"], 0.4, color="#2e9e6b", label="independent outlets")
    ax.barh(y - 0.2, hi["sh_w"], 0.4, color=GREY, label="BBC / Guardian / NYT")
    ax.set_yticks(y, hi["name"])
    ax.invert_yaxis()
    ax.set_xlabel("% of each group's country-tagged news (last 30 days)")
    ax.set_title("Who covers the 15 highest-need crises?")
    ax.legend(frameon=False)
    save(fig, "attention_gap.png")
    lines.append(f"- The 15 highest-need countries receive **{hi.sh_i.sum():.0f}%** of independent coverage "
                 f"but **{hi.sh_w.sum():.0f}%** of Western coverage.\n")

    d = c.dropna(subset=["prot", "att_w"])
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ax.scatter(d["att_w"], d["prot"], s=12, color=GREY)
    f = d[d.ignored]
    ax.scatter(f["att_w"], f["prot"], s=30, color=ACCENT, label="flagged 'ignored by Western media'")
    for _, r in d.sort_values("prot", ascending=False).head(16).iterrows():
        ax.annotate(r["iso3"], (r["att_w"], r["prot"]), fontsize=7, xytext=(3, 2), textcoords="offset points")
    ax.set_xlabel("Western media attention (log-scaled items, 30 days)")
    ax.set_ylabel("protracted need score")
    ax.set_title("Need vs Western attention")
    ax.legend(frameon=False, loc="lower right")
    save(fig, "need_vs_attention.png")
    lines.append("Flagged as ignored by Western media: " + ", ".join(f["name"]) + "\n")


def descriptive():
    """Descriptive statistics, skewness and correlations of the final country dataset."""
    lines.append("## 3b. Descriptive statistics and correlations (final dataset)\n")
    d = pd.read_csv(ROOT / "data/final/country_crisis_dataset.csv").set_index("iso3")
    cols = {"deaths_per100k_3y": "deaths /100k", "civilian_per100k_3y": "civilian deaths /100k",
            "ghi_2026": "GHI 2026", "aid_per_person": "aid $/person in need", "news_independent": "news indep.",
            "news_western": "news Western", "ifrc_funded_pct": "IFRC funded %"}
    x = d[list(cols)].rename(columns=cols)
    desc = x.describe().T[["count", "mean", "50%", "std", "max"]].rename(columns={"50%": "median"})
    desc["skew"] = x.skew()
    lines.append(desc.round(1).to_markdown() + "\n")
    lines.append("→ Death counts are extremely right-skewed (skew > 5: a few countries hold most deaths). "
                 "We still use a **linear per-capita** scale with a cap, because a log scale compressed a 100× gap "
                 "between Palestine and Israel; the cap limits the influence of extreme values.\n")
    corr = d[[c for c in ["n_civilian_harm", "n_conflict", "n_hunger", "n_acute", "n_aid_gap", "n_att_indep",
                          "n_att_western", "n_prot"] if c in d.columns]].corr(method="spearman")
    fig, ax = plt.subplots(figsize=(6.2, 5))
    im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    lab = [c.replace("n_", "") for c in corr.columns]
    ax.set_xticks(range(len(lab)), lab, rotation=45, ha="right")
    ax.set_yticks(range(len(lab)), lab)
    for i in range(len(lab)):
        for j in range(len(lab)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=7,
                    color="white" if abs(corr.iloc[i, j]) > 0.6 else "black")
    ax.set_title("Spearman correlation of score components")
    fig.colorbar(im, ax=ax, shrink=0.8)
    save(fig, "component_correlation.png")
    high = [(a, b, corr.loc[a, b]) for i, a in enumerate(corr.columns) for b in corr.columns[i + 1:]
            if abs(corr.loc[a, b]) >= 0.85 and "prot" not in (a + b)]
    lines.append("Pairs with |ρ| ≥ 0.85 (excluding the composite): "
                 + (", ".join(f"{a}–{b} {r:.2f}" for a, b, r in high) or "none") + ". "
                 "Components carry distinct information, so all are kept; civilian harm and conflict are related "
                 "by construction but answer different questions (who is killed vs how many).\n")


def model():
    lines.append("## 4. Models\n")
    m = json.loads((ROOT / "models" / "sector_metrics.json").read_text())
    rows = [{"model": r["model"], "micro-F1": r["micro_f1"], "macro-F1": r["macro_f1"]}
            for r in m["results"]]
    lines.append(pd.DataFrame(rows).to_markdown(index=False) + "\n")
    pc = m["results"][-1]["per_class"]
    fig, ax = plt.subplots(figsize=(6.5, 3))
    ks = list(pc)
    base = m["results"][0]["per_class"]
    x = np.arange(len(ks))
    ax.bar(x - 0.2, [base[k]["f1"] for k in ks], 0.4, color=GREY, label="keyword baseline")
    ax.bar(x + 0.2, [pc[k]["f1"] for k in ks], 0.4, color=ACCENT, label="TF-IDF + LogReg")
    ax.set_xticks(x, ks, rotation=40, ha="right")
    ax.set_ylabel("F1 (test)")
    ax.set_ylim(0, 1)
    ax.legend(frameon=False, ncols=2)
    ax.set_title("Per-sector F1 on HumSet test set")
    save(fig, "model_f1_per_sector.png")
    lines.append(f"By language (fairness check): {m['by_language']}\n")
    pm = json.loads((ROOT / "models" / "pillar_metrics.json").read_text())
    lines.append(f"Crisis-dynamics (pillar) model: macro-F1 {pm['macro_f1']}, per class {pm['per_class']}\n")


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    humset()
    independent()
    live_and_scores()
    descriptive()
    model()
    (ROOT / "reports" / "eda_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
