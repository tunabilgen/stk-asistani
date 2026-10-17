"""Assemble everything into web/data/dashboard.json for the interactive map.

Sources: UCDP, Global Hunger Index, Tech for Palestine, IFRC GO,
USGS, NASA EONET and independent news — no UN data.

Usage:  python -m src.build_dashboard
"""
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from src import features, partners
from src.config import DATA, MODELS, PROCESSED, SECTORS, WEB_DATA


def _num(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating, float)):
        return round(float(v), 4)
    return v


def _wmean(parts):
    parts = [(v, w) for v, w in parts if v is not None and not pd.isna(v)]
    if not parts:
        return None
    return sum(v * w for v, w in parts) / sum(w for _, w in parts)


def build():
    gj = json.loads((WEB_DATA / "countries.geojson").read_text(encoding="utf-8"))
    countries = pd.read_parquet(PROCESSED / "countries.parquet").set_index("iso3")
    st = features.structural()
    events = features.live_events(gj)
    news = features.news()
    att = features.attention(news)
    gz = features.gaza()
    soc = partners.societies()

    unmatched = st.attrs.get("unmatched")
    df = countries.join(st, how="left")
    ds = features.disaster_scores(events)
    df["acute_conflict_news"] = features.conflict_news_scores(news)
    df["news_independent"] = att.get("independent", pd.Series(dtype=float))
    df["news_western"] = att.get("western", pd.Series(dtype=float))
    df[["news_independent", "news_western"]] = df[["news_independent", "news_western"]].fillna(0)
    if gz:
        df.loc["PSE", "gaza_killed_30d"] = gz["killed_30d"]

    n = pd.DataFrame(index=df.index)
    # conflict intensity = deaths per 100,000 people, LINEAR scale (a log scale hid a 100x gap
    # between Palestine and Israel). 500 per 100k over 3 years = maximum.
    pop = df["pop_est"].where(df["pop_est"] > 0)
    # UCDP is global: a country without recorded events had zero recorded conflict deaths
    df["ucdp_deaths_3y"] = df["ucdp_deaths_3y"].fillna(0)
    df["ucdp_deaths_90d"] = df["ucdp_deaths_90d"].fillna(0)
    # Palestine: the Gaza Ministry of Health (via Tech for Palestine) is the primary source —
    # it registers deaths by name and ID; UCDP only counts deaths it can verify through media
    # reports, which undercounts a place where journalists are killed and access is blocked.
    # Total = killed in Gaza + starvation deaths (reported separately) + killed in the West Bank.
    df["deaths_source"] = "UCDP"
    if gz:
        total = gz["killed_total"] + (gz.get("famine_deaths") or 0) + (gz.get("wb_killed") or 0)
        df.loc["PSE", "ucdp_deaths_3y"] = total
        # MoH does not split civilians/combatants; children + women (+ West Bank children) is the
        # only published breakdown, so it is a strict LOWER bound — men and older people are not
        # assumed to be combatants, they are simply not broken down in the source.
        df.loc["PSE", "ucdp_civilian_3y"] = (gz["children_killed"] + gz.get("women_killed", 0)
                                             + (gz.get("wb_children_killed") or 0))
        df.loc["PSE", "deaths_source"] = "Gaza MoH + West Bank (Tech for Palestine)"
    df["deaths_per100k_3y"] = df["ucdp_deaths_3y"] / pop * 1e5
    n["conflict"] = (df["deaths_per100k_3y"] / 500).clip(upper=1)
    # civilian harm = civilians killed per 100k (UCDP), linear; 200 per 100k over 3 years = max.
    # Separates wars fought mainly between armed forces from violence that falls on civilians.
    df["ucdp_civilian_3y"] = df["ucdp_civilian_3y"].fillna(0)
    df["civilian_per100k_3y"] = df["ucdp_civilian_3y"] / pop * 1e5
    n["civilian_harm"] = (df["civilian_per100k_3y"] / 200).clip(upper=1)
    tr = features.trends(df["pop_est"])
    df = df.join(tr, how="left")
    n["hunger"] = (df["ghi_2026"] / 50).clip(upper=1)
    if gz.get("famine_deaths"):  # starvation deaths documented by Gaza MoH: GHI does not cover PSE
        n.loc["PSE", "hunger"] = min(1.0, 0.7 + gz["famine_deaths"] / 1000)

    # vulnerability (lack of capacity to cope without outside help), no index of "state
    # fragility" needed: hunger level (GHI does not score high-income countries at all, as they
    # have no hunger problem) or ongoing violence, whichever is higher.
    # USA / Japan / Germany -> 0 ; Somalia, Sudan, Palestine -> ~1
    df["vulnerability"] = pd.concat([((df["ghi_2026"] - 10) / 25).clip(0, 1),
                                     n["civilian_harm"] * 2, n["conflict"] * 2],
                                    axis=1).max(axis=1).clip(upper=1).fillna(0)
    # humanitarian disaster need = hazard x vulnerability (standard risk logic);
    # an IFRC appeal already signals that national capacity was exceeded
    df["acute_disaster"] = pd.concat([ds["hazard"].reindex(df.index) * df["vulnerability"],
                                      ds["ifrc"].reindex(df.index)], axis=1).max(axis=1)

    # recent armed violence (per capita): UCDP last 90 days (50 per 100k = max),
    # Gaza MoH last 30 days scaled to 90, and the live news signal
    gaza90 = df.get("gaza_killed_30d", pd.Series(dtype=float)) * 3
    n["conflict_recent"] = pd.concat([
        (df["ucdp_deaths_90d"] / pop * 1e5 / 50).clip(upper=1),
        (gaza90 / pop * 1e5 / 50).clip(upper=1),
        # news alone (not corroborated by UCDP / Gaza MoH data) can add at most 0.5 and is
        # multiplied by vulnerability: a shooting in New York is handled by the state,
        # a village massacre in Sudan is not
        (df["acute_conflict_news"] * df["vulnerability"]).clip(upper=0.5)], axis=1).max(axis=1)
    n["neglect"] = (1 - df["ifrc_funded_pct"] / 100).clip(0, 1)
    n["att_western"] = features._logrange(df["news_western"] + 1, 1, 60)
    n["att_indep"] = features._logrange(df["news_independent"] + 1, 1, 120)

    gaps = json.loads((DATA / "known_gaps.json").read_text(encoding="utf-8"))
    for iso, comps in gaps.items():
        for comp in comps:
            if iso in n.index and comp in n.columns:
                n.loc[iso, comp] = np.nan

    n["acute"] = pd.concat([df["acute_disaster"], n["conflict_recent"]], axis=1).max(axis=1).fillna(0)
    # protracted suffering: half the worst civilian dimension (being killed or starving),
    # half the weighted mean — so a hunger crisis (Somalia) is not diluted by low conflict,
    # and combatant-heavy wars do not outrank crises that fall on civilians
    def _prot(r):
        m = _wmean([(r["civilian_harm"], 2.0), (r["conflict"], 1.0), (r["hunger"], 1.5)])
        worst = np.nanmax([r["civilian_harm"], r["hunger"], np.nan, -1])
        return None if m is None else 0.5 * max(worst, 0) + 0.5 * m
    n["prot"] = [_prot(r) for _, r in n.iterrows()]

    # ---- aid presence relative to need (OECD humanitarian aid, all reporting donors) ----
    oe = pd.read_parquet(PROCESSED / "oecd_humanitarian.parquet")
    last2 = oe[oe["TIME_PERIOD"] >= oe["TIME_PERIOD"].max() - 1]
    aid = last2[last2["donor"] == "ALLD"].groupby("RECIPIENT")["usd"].mean()
    # Türkiye reports the cost of hosting Syrian refugees in Türkiye as aid to Syria: a real and
    # very large burden, but not aid present inside Syria -> excluded from this measure only
    tur_syr = last2[(last2["donor"] == "TUR") & (last2["RECIPIENT"] == "SYR")]["usd"].mean()
    if pd.notna(tur_syr) and "SYR" in aid.index:
        aid.loc["SYR"] = max(aid.loc["SYR"] - tur_syr, 0)
    df["aid_usd"] = aid.reindex(df.index).fillna(0)
    # people in severe need ≈ population × the part of protracted suffering above a 0.3 baseline
    # (keeps large states with moderate hunger, which rely on their own systems, from dominating)
    sev = ((n["prot"].astype(float) - 0.3) / 0.7).clip(lower=0)
    df["need_people"] = (pop * sev).where(sev > 0)
    # only where an international humanitarian response is plausible: a recognised crisis
    # (protracted >= 0.45) or an active Red Cross / Red Crescent Emergency Appeal (not small DREFs). Large states with their own
    # systems and moderate hunger (e.g. India) are not counted as "aid gaps".
    has_ea = df["ifrc_appeals"].map(lambda xs: isinstance(xs, list)
                                    and any(x.get("type") == "Emergency Appeal" for x in xs))
    crisis = (n["prot"].astype(float) >= 0.45) | has_ea
    df["aid_per_person"] = (df["aid_usd"] / df["need_people"]).where((df["need_people"] >= 1e5) & crisis)
    # gap: $5 or less per person in need -> 1 (almost no aid), $300 or more -> 0
    n["aid_gap"] = (1 - (np.log10(df["aid_per_person"].clip(lower=5)) - np.log10(5))
                    / (np.log10(300) - np.log10(5))).clip(0, 1)
    # money disbursed is not aid delivered: documented starvation deaths are direct evidence that
    # aid is not reaching people (blockade) -> override (same rule for any country with such data)
    if gz.get("famine_deaths"):
        n.loc["PSE", "aid_gap"] = max(n.at["PSE", "aid_gap"] if pd.notna(n.at["PSE", "aid_gap"]) else 0, 0.9)
        gaps.setdefault("PSE", {})["aid_blocked"] = {
            "tr": "Kâğıt üzerinde ayrılan yardım yüksek görünse de abluka nedeniyle ulaşmıyor: "
                  f"{int(gz['famine_deaths'])} açlık ölümü ve yardım beklerken öldürülen "
                  f"{int(gz.get('aid_seekers_killed') or 0):,} kişi kayıtlı.".replace(",", ".") + " Yardım açığı buna göre yüksek sayıldı.",
            "en": "Aid budgets look high on paper but aid is not getting in because of the blockade: "
                  f"{int(gz['famine_deaths'])} starvation deaths and {int(gz.get('aid_seekers_killed') or 0)} people "
                  "killed while seeking aid are recorded. The aid gap is scored as high accordingly."}

    # "ignored crisis": high need, but in the bottom 40% of Western media attention among
    # comparable crises, and (if known) under-funded
    pool = n[n["prot"].fillna(0) >= 0.5]
    cut = pool["att_western"].quantile(0.40)
    ignored = set(pool[(pool["att_western"] <= cut) & ~(pool["neglect"] < 0.5)].index)

    sector_news = {}
    for _, r in news.explode("iso3s").dropna(subset=["iso3s"]).iterrows():
        d = sector_news.setdefault(r["iso3s"], {k: 0 for k in SECTORS})
        for s in r["sectors"]:
            d[s] += 1

    out_c = []
    for iso, r in df.iterrows():
        nr = n.loc[iso]
        prot = nr["prot"]
        prot = None if pd.isna(prot) else float(prot)
        coverage = int(sum(pd.notna(nr[c]) for c in ("conflict", "hunger", "neglect")))
        # sector need from sector-relevant indicators (no people-in-need counts without UN data)
        proxies = {
            "food": _wmean([(nr["hunger"], 2), (prot, 1)]),
            "nutrition": _wmean([(nr["hunger"], 1)]),
            "health": _wmean([(nr["civilian_harm"], 1), (nr["conflict"], 1), (nr["hunger"], 1)]),
            "wash": _wmean([(nr["hunger"], 1), (nr["conflict"], 1)]),
            "shelter": _wmean([(nr["conflict"], 1), (nr["civilian_harm"], 1), (df.at[iso, "acute_disaster"], 1)]),
            "education": _wmean([(nr["conflict"], 1), (nr["hunger"], 1)]),
            "protection": _wmean([(nr["civilian_harm"], 2), (nr["conflict"], 1)]),
            "livelihoods": _wmean([(nr["hunger"], 1), (nr["conflict"], 1)]),
            "agriculture": _wmean([(nr["hunger"], 1)]),
            "logistics": None if prot is None else prot * 0.8,
        }
        sn = sector_news.get(iso, {})
        # news mix must never LOWER a measured need (Gaza news is mostly tagged "protection",
        # which used to cut its food need by 20% despite documented starvation deaths)
        sec = {k: _num(None if v is None or pd.isna(v) else float(v)) for k, v in proxies.items()}

        c_news = []
        if not news.empty:
            d = news[news["iso3s"].map(lambda xs: iso in xs)].sort_values("date", ascending=False)
            c_news = [{"title": x["title"], "url": x["url"], "date": str(x["date"])[:10],
                       "publisher": x["source"], "group": x["group"], "sectors": x["sectors"]}
                      for _, x in d.head(10).iterrows()]
        out_c.append({
            "iso3": iso, "name": r["name"], "name_tr": r["name_tr"], "lat": r["lat"],
            "lon": r["lon"], "region": r["region"],
            "ind": {k: _num(r.get(k)) for k in (
                "ucdp_deaths_3y", "deaths_per100k_3y", "ucdp_deaths_90d", "ucdp_civilian_3y",
                "civilian_per100k_3y", "deaths_source", "aid_usd", "need_people", "aid_per_person", "ghi_2026", "ghi_provisional",
                "vulnerability",
                "ifrc_requested", "ifrc_funded_pct", "news_independent", "news_western")},
            "gaza": gz if iso == "PSE" else None,
            "trend": {"status": r.get("status") if isinstance(r.get("status"), str) else "stable",
                      "recent_monthly": _num(r.get("recent_monthly")),
                      "base_monthly": _num(r.get("base_monthly")),
                      "ratio": _num(r.get("trend_ratio")),
                      "heavy_months_12": _num(r.get("heavy_months_12")),
                      "monthly": r.get("monthly") if isinstance(r.get("monthly"), dict) else {},
                      "ghi_2018": _num(r.get("ghi_2018")), "ghi_2026": _num(r.get("ghi_2026"))},
            "conflict_history": r["ucdp_history"] if isinstance(r.get("ucdp_history"), dict) else {},
            "ifrc_appeals": r["ifrc_appeals"] if isinstance(r.get("ifrc_appeals"), list) else [],
            # silence index: how much need exists that Western mainstream media do not report
            "silence": _num(None if prot is None else max(prot, nr["conflict_recent"] if pd.notna(nr["conflict_recent"]) else 0)
                            * (1 - (0 if pd.isna(nr["att_western"]) else nr["att_western"]))),
            "score": {"protracted": _num(prot), "acute": _num(nr["acute"]) or 0,
                      "acute_disaster": _num(r["acute_disaster"]) or 0,
                      "acute_conflict": _num(nr["conflict_recent"]) or 0,
                      "escalation": _num(r.get("escalation")) or 0,
                      "aid_gap": _num(nr["aid_gap"]),
                      "civilian_harm": _num(nr["civilian_harm"]),
                      "neglect": _num(nr["neglect"]), "att_western": _num(nr["att_western"]),
                      "att_indep": _num(nr["att_indep"]), "sector": sec},
            "data_coverage": coverage, "known_gaps": gaps.get(iso, {}),
            "forgotten": iso in ignored, "sector_news": sn, "news": c_news,
            "partners": partners.candidates(soc, news, iso),
        })

    sm = json.loads((MODELS / "sector_metrics.json").read_text())
    pm = json.loads((MODELS / "pillar_metrics.json").read_text())
    st_log = MODELS / "self_train_log.jsonl"
    dash = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="minutes"),
        "sectors": {k: {"tr": v[0], "en": v[1]} for k, v in SECTORS.items()},
        "model": {"micro_f1": sm["results"][-1]["micro_f1"], "macro_f1": sm["results"][-1]["macro_f1"],
                  "baseline_micro_f1": sm["results"][0]["micro_f1"], "n_train": sm["n_train"],
                  "pillar_macro_f1": pm["macro_f1"], "casualties_f1": pm["per_class"]["Casualties"],
                  "self_train": [json.loads(x) for x in st_log.read_text().splitlines()]
                  if st_log.exists() else []},
        "sources": {"ucdp_data_end": st.attrs.get("data_end"), "gaza_last_update": gz.get("last_update"),
                    "trend_months": tr.attrs.get("months")},
        "countries": out_c,
        # only disasters that can overwhelm the affected country are shown (no open-ocean storms,
        # no quakes in states that cope on their own)
        "events": [{k: e.get(k) for k in ("id", "source", "type", "title", "alert", "iso3",
                                          "lat", "lon", "date", "age_days", "url", "mag")}
                   for e in events
                   if e.get("iso3") in df.index and df.at[e["iso3"], "vulnerability"] >= 0.25
                   and e.get("alert") != "Green"],  # USGS PAGER green = little expected impact
        "news": [] if news.empty else [
            {"title": x["title"], "url": x["url"], "date": str(x["date"])[:16], "iso3s": x["iso3s"],
             "sectors": x["sectors"], "publisher": x["source"], "group": x["group"]}
            for _, x in news[news["group"] == "independent"].sort_values("date", ascending=False)
            .head(80).iterrows()],
    }
    export_dataset(df, n, out_c, news)
    (WEB_DATA / "dashboard.json").write_text(json.dumps(dash, ensure_ascii=False, default=_num),
                                             encoding="utf-8")
    print("unmatched names:", unmatched)
    print("events:", len(events), "| news:", len(news), "| ignored:", sorted(ignored))
    top = sorted(out_c, key=lambda c: -((c["score"]["protracted"] or 0) + c["score"]["acute"]))[:12]
    print("top:", [(c["iso3"], round(c["score"]["protracted"] or 0, 2), round(c["score"]["acute"], 2)) for c in top])


FINAL_COLS = {
    # identity
    "name": "country name (Natural Earth)", "region": "UN M49 region label from Natural Earth",
    "pop_est": "population estimate (Natural Earth, 2019)",
    # raw indicators
    "ucdp_deaths_3y": "conflict deaths, last 36 months of data (UCDP; Palestine: Gaza MoH + West Bank)",
    "ucdp_civilian_3y": "civilian deaths, last 36 months (UCDP; Palestine: children + women, lower bound)",
    "ucdp_deaths_90d": "conflict deaths, last 90 days of data (UCDP)",
    "deaths_per100k_3y": "conflict deaths per 100,000 people", "civilian_per100k_3y": "civilian deaths per 100,000 people",
    "deaths_source": "source of the death counts",
    "ghi_2026": "Global Hunger Index 2026 score (provisional categories at range midpoint)",
    "ghi_2018": "Global Hunger Index 2018 score", "ghi_provisional": "GHI value is a provisional category",
    "ifrc_requested": "active IFRC appeals: amount requested (CHF)", "ifrc_funded_pct": "active IFRC appeals: % funded",
    "aid_usd": "humanitarian aid per year, all OECD-reporting donors, 2023-2024 mean (USD)",
    "need_people": "people in severe need (estimate) = population x protracted suffering above 0.3",
    "aid_per_person": "humanitarian aid per person in severe need (USD/year), recognised crises only",
    "news_independent": "news items, last 30 days, 15 independent outlets", "news_western": "news items, last 30 days, BBC/Guardian/NYT",
    "recent_monthly": "mean conflict deaths per month, last 3 months", "base_monthly": "median conflict deaths per month, 12 months before",
    "trend_ratio": "(recent+5)/(base+5)", "heavy_months_12": "months with heavy violence in the last 12", "status": "trajectory label",
    "vulnerability": "0-1, max(hunger level, ongoing violence)",
    # normalised components (0-1)
    "n_civilian_harm": "civilian deaths per 100k / 200, capped at 1", "n_conflict": "deaths per 100k / 500, capped at 1",
    "n_hunger": "GHI / 50, capped at 1 (Palestine: documented starvation deaths)", "n_conflict_recent": "recent violence 0-1",
    "n_acute": "max(natural hazard x vulnerability, new IFRC appeal, recent violence)", "n_aid_gap": "0-1, $5/person -> 1, $300 -> 0",
    "n_neglect": "1 - IFRC funded share", "n_att_western": "Western media attention 0-1", "n_att_indep": "independent media attention 0-1",
    "n_prot": "protracted suffering 0-1", "escalation": "worsening bonus 0-1",
    # outputs
    "ignored_by_western_media": "flag", "silence": "silence index 0-1",
}


def export_dataset(df: pd.DataFrame, n: pd.DataFrame, out_c: list, news: pd.DataFrame):
    """The project's final, documented dataset (one row per country) + labelled news items."""
    final = DATA / "final"
    final.mkdir(exist_ok=True)
    x = df.join(n.add_prefix("n_"), how="left")
    by_iso = {c["iso3"]: c for c in out_c}
    x["ignored_by_western_media"] = [by_iso[i]["forgotten"] for i in x.index]
    x["silence"] = [by_iso[i]["silence"] for i in x.index]
    x["status"] = x["status"].fillna("no_recorded_violence")
    cols = [c for c in FINAL_COLS if c in x.columns]
    x[cols].rename_axis("iso3").to_csv(final / "country_crisis_dataset.csv", float_format="%.4f")
    lines = ["# Data dictionary — `country_crisis_dataset.csv`", "",
             f"One row per country ({len(x)} rows), built by `src/build_dashboard.py` on "
             f"{datetime.now(timezone.utc).date()}. See `notebooks/01_dataset_and_preprocessing.ipynb` for every step.", "",
             "| column | description |", "|---|---|", "| iso3 | ISO 3166-1 alpha-3 code (index) |"]
    lines += [f"| {c} | {FINAL_COLS[c]} |" for c in cols]
    (final / "DATA_DICTIONARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if not news.empty:
        nw = news[["source", "group", "date", "title", "url", "iso3s", "sectors", "p_casualties"]].copy()
        nw["iso3s"] = nw["iso3s"].map(";".join)
        nw["sectors"] = nw["sectors"].map(";".join)
        nw.to_csv(final / "news_labelled.csv", index=False, float_format="%.3f")


if __name__ == "__main__":
    build()
