"""Assignment 2 — media attention vs need vs funding (instructor feedback on Assignment 1).

Questions
  Q1  Does media attention follow humanitarian need?  Western vs Turkish vs all GDELT media.
  Q2  Does the large GDELT sample confirm the small RSS sample used in Assignment 1?
  Q3  Does humanitarian funding (OCHA FTS, UN — benchmark only, never in the ranking) reach
      the crises the media ignore?  Funding per person vs Western attention, controlling for need.
  Q4  Where does GDELT locate stories about Gaza / Palestine?
  Q5  Does the humanitarian system (ReliefWeb reports, UN OCHA — benchmark only) see the crises the media ignore?

Inputs : data/processed/gdelt_articles.parquet, data/processed/fts_funding.parquet,
         data/processed/reliefweb_counts.parquet,
         data/final/country_crisis_dataset.csv
Outputs: reports/attention_analysis.json, reports/attention_analysis.md,
         reports/figures/attention_tr_vs_west.png, reports/figures/attention_vs_funding.png,
         reports/figures/media_vs_reliefweb.png,
         data/final/media_attention_gdelt.csv

Usage:  python -m src.attention_analysis
"""
import json

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from src.config import FIGURES, PROCESSED, ROOT

HOME = {"western": {"USA", "GBR"}, "turkish": {"TUR"}, "all": set()}
NEED_MIN = 0.30  # crises = countries with protracted-need component >= 0.30


def shares(art: pd.DataFrame) -> pd.DataFrame:
    out = {}
    for g in ["western", "turkish", "all"]:
        a = art if g == "all" else art[art["group"] == g]
        a = a[~a["iso3"].isin(HOME[g])]  # foreign coverage only
        out[f"share_{g}"] = a.groupby("iso3")["url"].nunique() / a["url"].nunique()
        out[f"n_{g}"] = a.groupby("iso3")["url"].nunique()
    return pd.DataFrame(out).fillna(0)


def partial_spearman(x, y, z):
    """Spearman correlation of x and y after removing the (rank-linear) effect of z."""
    rx, ry, rz = (pd.Series(v).rank().values for v in (x, y, z))
    res = lambda a: a - np.polyval(np.polyfit(rz, a, 1), rz)
    return spearmanr(res(rx), res(ry))


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    art = pd.read_parquet(PROCESSED / "gdelt_articles.parquet")
    ds = pd.read_csv(ROOT / "data/final/country_crisis_dataset.csv")
    fts = pd.read_parquet(PROCESSED / "fts_funding.parquet").groupby("iso3")["funding_usd"].sum()
    sh = shares(art)
    df = ds.set_index("iso3").join(sh, how="left").fillna({c: 0 for c in sh.columns})
    df["fts_usd_2025_26"] = fts.reindex(df.index).fillna(0)
    df["fts_per_capita"] = df["fts_usd_2025_26"] / df["pop_est"]
    crises = df[df["n_prot"] >= NEED_MIN].copy()
    res = {"articles": int(art["url"].nunique()), "article_country_rows": len(art),
           "domains": int(art["domain"].nunique()),
           "articles_by_group": art.groupby("group")["url"].nunique().to_dict(),
           "period": "30 days of GDELT 2.0 event files (one every 30 min) up to " + str(art["date"].max().date()),
           "n_crises": len(crises), "need_threshold": NEED_MIN}

    # Q1 — attention follows need?
    res["q1_spearman_need_vs_attention"] = {
        g: dict(zip(["rho", "p"], np.round(spearmanr(crises["n_prot"], crises[f"share_{g}"]), 3).tolist()))
        for g in ["western", "turkish", "all"]}
    # share of foreign coverage that goes to ALL crisis countries together
    res["q1_share_of_coverage_on_crises"] = {g: round(float(crises[f"share_{g}"].sum()), 3)
                                              for g in ["western", "turkish", "all"]}
    top = crises.sort_values("n_prot", ascending=False).head(15)
    res["q1_top15"] = [{"iso3": i, "name": r["name"], "need": round(r["n_prot"], 2),
                        "west_pct": round(100 * r["share_western"], 2),
                        "turkish_pct": round(100 * r["share_turkish"], 2),
                        "all_pct": round(100 * r["share_all"], 2)} for i, r in top.iterrows()]

    # Q2 — GDELT vs Assignment-1 RSS sample (Western attention)
    both = crises[crises["news_western"].notna()]
    res["q2_rss_vs_gdelt_western_rho"] = round(float(spearmanr(both["news_western"], both["share_western"])[0]), 3)
    # silence index with each sample, same rule as the app: need x (1 - coverage relative to need's fair share)
    need_share = df["n_prot"].fillna(0) / df["n_prot"].fillna(0).sum()
    for name, col in [("rss", "news_western"), ("gdelt", "n_western")]:
        cov = df[col].where(~df.index.isin(HOME["western"])).fillna(0)
        ratio = (cov / cov.sum()) / need_share
        crises[f"silence_{name}"] = crises["n_prot"] * (1 - ratio.reindex(crises.index).clip(upper=1).fillna(1))
    res["q2_silence_rank_rho"] = round(float(spearmanr(crises["silence_rss"], crises["silence_gdelt"])[0]), 3)
    old10 = set(crises["silence_rss"].nlargest(10).index); new10 = set(crises["silence_gdelt"].nlargest(10).index)
    res["q2_silence_top10_overlap"] = len(old10 & new10)
    res["q2_silence_top10_gdelt"] = crises.loc[crises["silence_gdelt"].nlargest(10).index, "name"].tolist()

    # Q3 — funding vs attention, controlling for need
    c = crises[crises["fts_usd_2025_26"] > 0]
    res["q3_n"] = len(c)
    res["q3_spearman_funding_pc_vs_need"] = round(float(spearmanr(c["n_prot"], c["fts_per_capita"])[0]), 3)
    res["q3_spearman_funding_pc_vs_western_attention"] = round(float(spearmanr(c["share_western"], c["fts_per_capita"])[0]), 3)
    pr = partial_spearman(c["share_western"], c["fts_per_capita"], c["n_prot"])
    res["q3_partial_rho_attention_funding_given_need"] = {"rho": round(float(pr[0]), 3), "p": round(float(pr[1]), 3)}
    # silent vs visible crises with comparable need: split at the median Western attention
    med = c["share_western"].median()
    quiet, loud = c[c["share_western"] <= med], c[c["share_western"] > med]
    res["q3_quiet_vs_visible"] = {
        "quiet": {"n": len(quiet), "median_need": round(float(quiet["n_prot"].median()), 2),
                  "median_usd_per_person": round(float(quiet["fts_per_capita"].median()), 1)},
        "visible": {"n": len(loud), "median_need": round(float(loud["n_prot"].median()), 2),
                    "median_usd_per_person": round(float(loud["fts_per_capita"].median()), 1)}}

    # Q4 — framing signal: stories whose URL names Gaza / the West Bank / Palestine, but whose
    # main event GDELT located only in Israel (the acting state) and not in Palestine (the place
    # where people are affected). Compared across media groups on the same kind of stories.
    gaz = art[(art["geo"] == "url") & (art["iso3"] == "PSE")]["url"].unique()
    geo = art[(art["geo"] == "gdelt") & art["url"].isin(gaz)]
    per = geo.groupby("url").agg(group=("group", "first"), isr=("iso3", lambda s: "ISR" in set(s)),
                                 pse=("iso3", lambda s: "PSE" in set(s)))
    per["israel_only"] = per["isr"] & ~per["pse"]
    res["q4_palestine_stories_located_in_israel_only"] = {
        g: {"stories": int(len(x)), "israel_only_pct": round(100 * float(x["israel_only"].mean()), 1)}
        for g, x in per.groupby("group")}

    # Q5 — humanitarian-system attention (ReliefWeb reports, same 30 days) vs media attention.
    # Both are turned into coverage ratios inside the crisis set: share of attention / share of need.
    rw = pd.read_parquet(PROCESSED / "reliefweb_counts.parquet").set_index("iso3")["reports"]
    crises["rw_reports"] = rw.reindex(crises.index).fillna(0)
    ns = crises["n_prot"] / crises["n_prot"].sum()
    crises["ratio_media"] = (crises["n_western"] / crises["n_western"].sum()) / ns
    crises["ratio_rw"] = (crises["rw_reports"] / crises["rw_reports"].sum()) / ns
    silent10 = crises["silence_gdelt"].nlargest(10).index
    seen = crises.loc[silent10]
    res["q5_reliefweb"] = {
        "reports_30d": int(crises["rw_reports"].sum()),
        "spearman_need_vs_reliefweb": dict(zip(["rho", "p"], np.round(spearmanr(crises["n_prot"], crises["rw_reports"]), 3).tolist())),
        "spearman_need_vs_western_media": res["q1_spearman_need_vs_attention"]["western"],
        "spearman_reliefweb_vs_western_media": round(float(spearmanr(crises["rw_reports"], crises["n_western"])[0]), 3),
        "media_silent_top10": [{"iso3": i, "name": r["name"], "reliefweb_reports": int(r["rw_reports"]),
                                "media_ratio": round(float(r["ratio_media"]), 2), "reliefweb_ratio": round(float(r["ratio_rw"]), 2)}
                               for i, r in seen.iterrows()],
        "media_silent_top10_seen_by_reliefweb": int((seen["ratio_rw"] >= 0.5).sum()),
        "median_reliefweb_ratio_silent10_vs_others": [round(float(seen["ratio_rw"].median()), 2),
                                                       round(float(crises.drop(silent10)["ratio_rw"].median()), 2)]}

    fig, ax = plt.subplots(figsize=(8, 6))
    x, y = crises["ratio_media"].clip(lower=0.005), crises["ratio_rw"].clip(lower=0.005)
    ax.scatter(x, y, s=40 + 300 * crises["n_prot"], color="#b23a2e", alpha=0.55, edgecolor="white")
    for i, r in crises.iterrows():
        if i in silent10 or r["ratio_media"] > 2 or r["ratio_rw"] > 2:
            ax.annotate(r["name"], (x[i], y[i]), fontsize=7, xytext=(3, 3), textcoords="offset points")
    ax.axhline(1, color="#999", lw=0.8, ls="--"); ax.axvline(1, color="#999", lw=0.8, ls="--")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Western media: share of coverage ÷ share of need (GDELT, 30 days)")
    ax.set_ylabel("Humanitarian system: share of ReliefWeb reports ÷ share of need")
    ax.text(0.02, 0.98, "top left: the aid system reports, the media are silent", transform=ax.transAxes, va="top", fontsize=8, color="#555")
    ax.set_title("Bubble size = need. 1 = attention in line with need. ReliefWeb is a benchmark only", loc="left", fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(FIGURES / "media_vs_reliefweb.png", dpi=160); plt.close(fig)

    (ROOT / "reports/attention_analysis.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    df[["name", "n_prot", "share_western", "share_turkish", "share_all", "n_western", "n_turkish", "n_all",
        "fts_usd_2025_26", "fts_per_capita"]].round(6).to_csv(ROOT / "data/final/media_attention_gdelt.csv")

    # Figure 1 — Turkish vs Western coverage of the 15 highest-need crises
    t = top.iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 6))
    y = np.arange(len(t))
    ax.barh(y + 0.2, 100 * t["share_turkish"], 0.4, color="#b23a2e", label="Turkish media")
    ax.barh(y - 0.2, 100 * t["share_western"], 0.4, color="#9a9a9a", label="Western mainstream media")
    ax.set_yticks(y, t["name"]); ax.set_xlabel("% of the group's foreign-news articles (GDELT, 30 days)")
    ax.set_title("Coverage of the 15 highest-need crises", loc="left", fontsize=11)
    ax.legend(frameon=False, loc="lower right"); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(FIGURES / "attention_tr_vs_west.png", dpi=160); plt.close(fig)

    # Figure 2 — Western attention vs funding per person
    fig, ax = plt.subplots(figsize=(8, 5.5))
    x = 100 * c["share_western"] + 1e-3
    ax.scatter(x, c["fts_per_capita"] + 0.01, s=40 + 300 * c["n_prot"], color="#b23a2e", alpha=0.55, edgecolor="white")
    for i, r in c.iterrows():
        if r["n_prot"] >= 0.5 or r["share_western"] > 0.01:
            ax.annotate(r["name"], (100 * r["share_western"] + 1e-3, r["fts_per_capita"] + 0.01), fontsize=7,
                        xytext=(3, 3), textcoords="offset points")
    ax.set_xscale("symlog", linthresh=0.05); ax.set_yscale("log")
    ax.set_xlabel("Western media attention (% of foreign articles, GDELT)")
    ax.set_ylabel("Humanitarian funding 2025–26, USD per person (OCHA FTS)")
    ax.set_title("Bubble size = need. Benchmark only — FTS is not used in the ranking", loc="left", fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(FIGURES / "attention_vs_funding.png", dpi=160); plt.close(fig)
    print(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
