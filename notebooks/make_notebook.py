"""Generates notebooks/01_dataset_and_preprocessing.ipynb (run: python notebooks/make_notebook.py).

The notebook is then executed with nbconvert so that every output is stored in the file.
"""
from pathlib import Path

import nbformat as nbf

nb = nbf.v4.new_notebook()
C = []


def md(s):
    C.append(nbf.v4.new_markdown_cell(s.strip()))


def code(s):
    C.append(nbf.v4.new_code_cell(s.strip()))


md("""
# STK Asistanı — Dataset and preprocessing

This notebook documents **every data source, every cleaning step and every transformation** that turns raw
downloads into the project's final dataset, `data/final/country_crisis_dataset.csv` (one row per country),
and the training data of the classifiers.

| # | Source | Publisher (type) | Used for |
|---|---|---|---|
| 1 | HumSet | DEEP / Data Friendly Space (Apache-2.0) | training text for the sector and casualty classifiers |
| 2 | UCDP GED 26.1 + candidate 2026 | Uppsala University (academic) | conflict and civilian deaths, monthly trends |
| 3 | Tech for Palestine | Gaza Ministry of Health data (open, volunteer-maintained) | Palestine casualties, starvation deaths |
| 4 | Global Hunger Index 2026 | Concern Worldwide & Welthungerhilfe (NGOs) | hunger |
| 5 | IFRC GO | Red Cross / Red Crescent movement | active appeals, national societies |
| 6 | OECD DAC2A | OECD (donor-reported statistics) | humanitarian aid per recipient |
| 7 | USGS, NASA EONET | science agencies | natural-hazard alerts |
| 8 | 18 RSS feeds | 15 independent outlets + BBC/Guardian/NYT (comparison only) | live news |
| 9 | Natural Earth | public domain | country shapes, population |

No UN data is used.
""")

code("""
import sys, json, ast
from pathlib import Path
ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(ROOT))
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from src import features
from src.config import HUMSET, PROCESSED, LIVE, SECTORS
pd.set_option("display.width", 160); pd.set_option("display.max_columns", 30)
plt.rcParams.update({"figure.dpi": 110, "axes.spines.top": False, "axes.spines.right": False})
""")

# ---------------- A. HumSet
md("""
## A. Training data — HumSet

**Raw:** 148,621 text excerpts from humanitarian reports (EN/FR/ES), annotated by experts with sectors and
analytical "pillars". **Goal:** a multi-label classifier that tags live news with humanitarian sectors.
""")
code("""
raw = pd.concat([pd.read_json(HUMSET / f"{s}.jsonl", lines=True, dtype=False).assign(split=s)
                 for s in ("train", "validation", "test")], ignore_index=True)
raw["sectors"] = raw["sectors"].map(lambda s: ast.literal_eval(s) if isinstance(s, str) else s)
print("rows:", len(raw)); print(raw["split"].value_counts().to_dict()); print(raw["lang"].value_counts().to_dict())
raw[["lang", "excerpt", "sectors"]].head(3)
""")
md("### A.1 Cleaning")
code("""
steps = []
steps.append(("raw excerpts", len(raw)))
no_sector = raw["sectors"].map(len) == 0
steps.append(("drop: no sector label (annotators tagged only pillars)", int(no_sector.sum())))
short = raw["excerpt"].fillna("").str.strip().str.len() <= 20
steps.append(("drop: excerpt <= 20 characters", int((short & ~no_sector).sum())))
dups = raw["excerpt"].duplicated()
steps.append(("info: duplicated excerpts (kept, official split preserved)", int(dups.sum())))
clean = raw[~no_sector & ~short].copy()
steps.append(("clean excerpts", len(clean)))
pd.DataFrame(steps, columns=["step", "rows"])
""")
md("""
### A.2 Label mapping

HumSet's 11 sectors are mapped to the project's 10-sector taxonomy. *Cross* (cross-sectoral) is dropped,
because it is not an area of work an NGO can choose. Labels are then binarised (multi-label).
""")
code("""
mapping = {v[2]: k for k, v in SECTORS.items()}
clean["labels"] = clean["sectors"].map(lambda xs: [mapping[x] for x in xs if x in mapping])
print("mapping:", mapping)
print("labels per excerpt (mean):", round(clean["labels"].map(len).mean(), 2))
counts = clean.explode("labels")["labels"].value_counts()
ax = counts.sort_values().plot.barh(figsize=(6, 3.2), color="#a3271f", title="Excerpts per sector after cleaning")
print("imbalance largest/smallest:", round(counts.max() / counts.min(), 1), "x  -> class weights + per-class thresholds")
""")

# ---------------- B. crisis indicators
md("## B. Crisis indicators (one row per country)")
md("""
### B.1 Countries and population — Natural Earth

177 countries with ISO-3 codes and a population estimate, used as the **spine** of the dataset and for all per-capita rates.
""")
code("""
countries = pd.read_parquet(PROCESSED / "countries.parquet").set_index("iso3")
print(len(countries), "countries; population missing:", int(countries["pop_est"].isna().sum()))
countries[["name", "region", "pop_est"]].head()
""")

md("""
### B.2 Conflict deaths — UCDP

Event-level data (one row per violent event). Cleaning steps:
1. merge the final release (to 2025) with the 2026 monthly *candidate* releases, de-duplicate on event id;
2. harmonise country names to ISO-3;
3. **re-assign Gaza and West Bank events to Palestine** — UCDP codes them under Israel;
4. aggregate to country: deaths and civilian deaths in the last 36 months, monthly series for trends.
""")
code("""
u = pd.read_parquet(PROCESSED / "ucdp_events.parquet")
print("events:", len(u), "| period:", u["date_start"].min(), "->", u["date_start"].max())
u["iso3"] = features.to_iso(u["country"], features.name_lookup())
print("unmatched country names:", sorted(set(u.loc[u["iso3"].isna(), "country"])))
moved = u["adm_1"].fillna("").str.contains("Gaza|West Bank", case=False)
print(f"events re-assigned from Israel to Palestine: {moved.sum():,} ({u.loc[moved, 'best'].sum():,} deaths)")
u.loc[moved, "iso3"] = "PSE"
u[["date_start", "country", "adm_1", "side_a", "side_b", "best", "deaths_civilians"]].sample(4, random_state=1)
""")

md("""
### B.3 Palestine — Gaza Ministry of Health (via Tech for Palestine)

UCDP verifies deaths case by case through media reports and undercounts where journalists are killed and access
is blocked. For Palestine the Ministry of Health is the **primary source**. Comparison:
""")
code("""
s = json.loads((LIVE / "t4p_summary.json").read_text(encoding="utf-8"))
daily = pd.read_parquet(PROCESSED / "t4p_daily.parquet")
wb = pd.read_parquet(PROCESSED / "t4p_west_bank.parquet").ffill().iloc[-1]
ucdp_pse = u[u["iso3"] == "PSE"]
pd.DataFrame({
  "UCDP (verified events)": [ucdp_pse["best"].sum(), ucdp_pse["deaths_civilians"].sum()],
  "Gaza MoH + West Bank": [s["killed"]["total"] + daily["famine_cum"].max() + wb["killed_cum"],
                           s["killed"]["children"] + s["killed"]["women"] + wb["killed_children_cum"]],
}, index=["deaths", "civilians (MoH: children + women only = lower bound)"])
""")

md("""
### B.4 Hunger — Global Hunger Index 2026

The Excel release is parsed from the ranking sheet. Cleaning: `"<5"` → 2.5; countries with incomplete data
receive GHI's **provisional category**, used at the range midpoint (e.g. Sudan, South Sudan, Yemen: *alarming*
35–49.9 → 42.45); combined rows (*"Burundi, South Sudan and Yemen"*) are split; names are harmonised.
""")
code("""
ghi = pd.read_parquet(PROCESSED / "ghi.parquet")
ghi["iso3"] = features.to_iso(ghi["country"], features.name_lookup())
print(len(ghi), "countries | provisional:", ghi.loc[ghi["ghi_provisional"], "country"].tolist())
print("unmatched names:", ghi.loc[ghi["iso3"].isna(), "country"].tolist())
ghi.sort_values("ghi_2026", ascending=False).head(10)
""")

md("""
### B.5 Red Cross / Red Crescent appeals — IFRC GO

Active appeals (end date after today); appeals without a requested amount are dropped; per country:
requested CHF, % funded, and whether there is a large *Emergency Appeal* (used to recognise a crisis).
""")
code("""
app = pd.read_parquet(PROCESSED / "ifrc_appeals.parquet")
print(len(app), "active appeals,", (app["requested"] <= 0).sum(), "without requested amount (dropped)")
app = app[app["requested"] > 0]
app.groupby("type").agg(n=("name", "size"), requested_chf=("requested", "sum"), funded_chf=("funded", "sum"))
""")

md("""
### B.6 Humanitarian aid — OECD DAC2A

Humanitarian aid disbursed per recipient (measure 216, all reporting donors, constant USD), mean of the last two
years. **Correction:** Türkiye reports the cost of hosting Syrian refugees *in Türkiye* as humanitarian aid to
Syria. This is a real and very large burden, but it is not aid present inside Syria, so it is excluded
from this measure only.
""")
code("""
oe = pd.read_parquet(PROCESSED / "oecd_humanitarian.parquet")
syr = oe[oe["RECIPIENT"] == "SYR"].pivot_table(index="donor", columns="TIME_PERIOD", values="usd") / 1e6
syr.round(0).rename(index={"ALLD": "all donors (USD m)", "TUR": "of which reported by Türkiye (USD m)"})
""")

md("""
### B.7 Live news — 18 RSS feeds

Cleaning: HTML stripped, duplicates removed (same URL), date parsed. **Country tagging** uses a gazetteer of
country and crisis place names (e.g. Rafah, El Fasher, Goma). Demonyms are used only if no place is named, so a
report is attributed to the place where people are affected, not to the attacking state.
""")
code("""
from src.sources.news import tag_countries
nw = pd.DataFrame(json.loads((LIVE / "news.json").read_text(encoding="utf-8"))).drop_duplicates("id")
print(len(nw), "unique items |", f"{(nw['iso3s'].map(len) > 0).mean():.0%} tagged with a country")
display(nw.groupby(["group", "source"]).size().rename("items").to_frame().T)
for s_ in ["Israeli strikes kill 20 in Gaza", "RSF attack El Fasher, Sudan", "South Sudan floods displace thousands"]:
    print(f"{s_!r:45} -> {tag_countries(s_)}")
""")

# ---------------- C. missing values
md("""
## C. Missing values — how they are handled

Rule: **missing data is never treated as "no need".** Each component is either computed, set to a documented
neutral value, or excluded from the weighted mean for that country.
""")
code("""
final = pd.read_csv(ROOT / "data/final/country_crisis_dataset.csv").set_index("iso3")
miss = final[["ucdp_deaths_3y", "ghi_2026", "ifrc_funded_pct", "aid_per_person", "news_independent"]].isna().mean().mul(100).round(0)
rule = {"ucdp_deaths_3y": "UCDP is global: no event = 0 recorded deaths",
        "ghi_2026": "high-income countries are not scored by GHI (no hunger problem); excluded from the mean",
        "ifrc_funded_pct": "no active appeal: funding gap = neutral 0.5 in the UI",
        "aid_per_person": "computed only for recognised crises; elsewhere aid gap = 0",
        "news_independent": "no news = 0 (attention)"}
pd.DataFrame({"% missing": miss, "handling": pd.Series(rule)})
""")

# ---------------- C2. descriptive statistics & correlations
md("""
## C2. Descriptive statistics, skewness and correlations

Deaths are extremely right-skewed (a few countries hold most deaths). A log scale would tame the skew, but it compressed
a 100-fold gap between Palestine and Israel into 100 vs 43. We therefore use a **linear per-capita scale with a cap**,
which keeps real proportions and limits the influence of extreme values.
""")
code("""
cols = {"deaths_per100k_3y": "deaths /100k", "civilian_per100k_3y": "civilian deaths /100k", "ghi_2026": "GHI 2026",
        "aid_per_person": "aid $/person in need", "news_independent": "news indep.", "news_western": "news Western"}
x = final[list(cols)].rename(columns=cols)
desc = x.describe().T[["count", "mean", "50%", "std", "max"]].rename(columns={"50%": "median"})
desc["skew"] = x.skew()
desc.round(1)
""")
code("""
comp = ["n_civilian_harm", "n_conflict", "n_hunger", "n_acute", "n_aid_gap", "n_att_indep", "n_att_western"]
corr = final[comp].corr(method="spearman")
fig, ax = plt.subplots(figsize=(5.6, 4.6))
im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
ax.set_xticks(range(len(comp)), [c[2:] for c in comp], rotation=45, ha="right"); ax.set_yticks(range(len(comp)), [c[2:] for c in comp])
for i in range(len(comp)):
    for j in range(len(comp)):
        ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=7)
fig.colorbar(im, shrink=0.8); ax.set_title("Spearman correlation of score components")
high = [(a, b, round(corr.loc[a, b], 2)) for i, a in enumerate(comp) for b in comp[i + 1:] if abs(corr.loc[a, b]) >= 0.85]
print("pairs with |rho| >= 0.85:", high)
""")
md("""
**Multicollinearity check.** Only civilian harm and conflict intensity exceed |ρ| ≥ 0.85. Both are kept on purpose: they
answer different questions (*who* is killed vs *how many*). This difference separates combatant-heavy wars (Ukraine: 3% of
recorded deaths are civilians) from violence that falls on civilians (Palestine, Sudan).
""")

# ---------------- D. normalisation & final dataset
md("""
## D. Normalisation and the final dataset

| component | formula (0–1) |
|---|---|
| civilian harm | civilian deaths per 100k (3 years) / 200, capped |
| conflict intensity | deaths per 100k (3 years) / 500, capped — **linear**: a log scale hid a 100× gap between Palestine and Israel |
| hunger | GHI / 50, capped; Palestine (not in GHI): documented starvation deaths |
| protracted suffering | ½ × worst civilian dimension (killed or starving) + ½ × weighted mean |
| vulnerability | max(hunger level, ongoing violence) — a hazard in a state that copes alone counts 0 |
| acute | max(natural hazard × vulnerability, new IFRC appeal, recent violence) |
| aid gap | aid per person in severe need: $5 → 1, $300 → 0 (log); starvation deaths override budgets |
| worsening | last 3 months vs median of previous 12 and previous quarter; bonus only |
""")
code("""
cols = ["name", "ucdp_deaths_3y", "civilian_per100k_3y", "ghi_2026", "aid_per_person", "status",
        "n_civilian_harm", "n_hunger", "n_prot", "n_acute", "n_aid_gap", "silence"]
print(final.shape)
final.sort_values("n_prot", ascending=False)[cols].head(15).round(2)
""")

# ---------------- E. sanity checks
md("## E. Sanity checks against domain knowledge")
code("""
chk = final.loc[["PSE", "SDN", "YEM", "UKR", "ISR", "USA", "MDG"],
                ["name", "deaths_per100k_3y", "civilian_per100k_3y", "ghi_2026", "n_acute", "n_prot", "n_aid_gap", "status"]]
chk.round(2)
""")
md("""
* **Palestine vs Israel:** 1,622 vs 16 deaths per 100k people; civilian harm 1.0 vs 0.04.
* **Ukraine:** the deadliest war in absolute terms, but 97% of recorded deaths are combatants, so civilian harm is low.
* **USA:** hazards occur but vulnerability is 0, so acute need is 0.
* **Madagascar:** no conflict and no news, but GHI 36.5 (*alarming*), an underfunded cyclone appeal and about $30 of aid per
  person in severe need. This is a *silent* crisis, exactly what the tool is meant to surface.
""")

# ---------------- F. models
md("## F. Model results (from `models/*.json`)")
code("""
m = json.loads((ROOT / "models/sector_metrics.json").read_text())
p = json.loads((ROOT / "models/pillar_metrics.json").read_text())
display(pd.DataFrame([{"model": r["model"], "micro-F1": r["micro_f1"], "macro-F1": r["macro_f1"]} for r in m["results"]]))
print("macro-F1 by language:", {k: v["macro_f1"] for k, v in m["by_language"].items()})
print("casualty / displacement model:", p["per_class"])
""")

nb["cells"] = C
nb["metadata"]["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
out = Path(__file__).parent / "01_dataset_and_preprocessing.ipynb"
nbf.write(nb, out)
print("written", out)
