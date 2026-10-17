"""Country-level crisis features built ONLY from non-UN sources.

Every indicator is normalised to 0..1 so the UI can re-weight them interactively.
Missing data stays NaN (unknown) — it is never treated as "no need".
"""
import json
import math
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from src import pillar_model, sector_model
from src.config import LIVE, PROCESSED

NOW = datetime.now(timezone.utc)


def _read(name):
    p = PROCESSED / f"{name}.parquet"
    return pd.read_parquet(p) if p.exists() else pd.DataFrame()


def _logrange(s: pd.Series, lo: float, hi: float) -> pd.Series:
    """log10 scale mapped so lo -> 0 and hi -> 1 (clipped); keeps NaN."""
    return ((np.log10(s.clip(lower=1)) - np.log10(lo)) / (np.log10(hi) - np.log10(lo))).clip(0, 1)


def _age_days(iso: str) -> float:
    try:
        d = pd.Timestamp(iso)
        d = d.tz_localize("UTC") if d.tzinfo is None else d
        return max(0.0, (NOW - d.to_pydatetime()).total_seconds() / 86400)
    except Exception:
        return 999.0


# ---------- names -> ISO3 ----------
NAME_FIX = {  # source spellings that differ from Natural Earth
    "dr congo (zaire)": "COD", "congo": "COG", "myanmar (burma)": "MMR", "yemen (north yemen)": "YEM",
    "russia (soviet union)": "RUS", "cambodia (kampuchea)": "KHM", "zimbabwe (rhodesia)": "ZWE",
    "madagascar (malagasy)": "MDG", "kingdom of eswatini (swaziland)": "SWZ", "ivory coast": "CIV",
    "united states of america": "USA", "serbia (yugoslavia)": "SRB", "bosnia-herzegovina": "BIH",
    "congo democratic republic": "COD", "congo republic": "COG", "dem. rep. of the congo": "COD",
    "democratic republic of the congo": "COD", "republic of congo": "COG", "congo, rep.": "COG",
    "côte d'ivoire": "CIV", "cote d'ivoire": "CIV", "guinea bissau": "GNB", "guinea-bissau": "GNB",
    "kyrgyz republic": "KGZ", "slovak republic": "SVK", "türkiye": "TUR", "turkey": "TUR",
    "lao pdr": "LAO", "laos": "LAO", "north korea": "PRK", "korea, dem. people's rep.": "PRK",
    "syria": "SYR", "syrian arab republic": "SYR", "iran": "IRN", "russia": "RUS",
    "tanzania": "TZA", "united republic of tanzania": "TZA", "viet nam": "VNM", "vietnam": "VNM",
    "eswatini": "SWZ", "timor-leste": "TLS", "gambia": "GMB", "the gambia": "GMB",
    "central african rep.": "CAF", "palestine": "PSE", "west bank and gaza": "PSE",
    "israel and west bank": "ISR", "bolivia": "BOL", "venezuela": "VEN", "moldova": "MDA",
    "north macedonia": "MKD", "czechia": "CZE", "micronesia": "FSM", "cabo verde": "CPV",
    "south sudan": "SSD", "somalia": "SOM", "sudan": "SDN",
    "bolivia (plurinat. state of)": "BOL", "bosnia & herzegovina": "BIH", "congo (republic of)": "COG",
    "iran (islamic republic of)": "IRN", "moldova (rep. of)": "MDA", "tanzania (united rep. of)": "TZA",
    "trinidad & tobago": "TTO", "venezuela (boliv. rep. of)": "VEN", "macedonia": "MKD",
    "swaziland": "SWZ", "cape verde": "CPV", "korea (dpr)": "PRK", "dem. rep. of the congo": "COD",
}


def name_lookup() -> dict:
    m = {}
    c = _read("countries")
    for col in ("name", "name_long"):
        m.update({str(n).lower(): i for n, i in zip(c[col], c["iso3"])})
    m.update(NAME_FIX)
    return m


def to_iso(series: pd.Series, lookup: dict) -> pd.Series:
    return series.astype(str).str.strip().str.lower().map(lookup)


# ---------- structural / protracted ----------

def ucdp_by_country() -> pd.DataFrame:
    """Conflict deaths (UCDP best estimate). Gaza/West Bank events are coded under Israel by
    UCDP — we re-assign them to Palestine (PSE) using the admin-1 field."""
    u = _read("ucdp_events")
    lk = name_lookup()
    u["iso3"] = to_iso(u["country"], lk)
    u.loc[u["adm_1"].fillna("").str.contains("Gaza|West Bank", case=False), "iso3"] = "PSE"
    u["date"] = pd.to_datetime(u["date_start"], errors="coerce")
    end = u["date"].max()
    out = pd.DataFrame({
        "ucdp_deaths_3y": u[u["date"] > end - pd.Timedelta(days=3 * 365)].groupby("iso3")["best"].sum(),
        "ucdp_deaths_90d": u[u["date"] > end - pd.Timedelta(days=90)].groupby("iso3")["best"].sum(),
        "ucdp_civilian_3y": u[u["date"] > end - pd.Timedelta(days=3 * 365)].groupby("iso3")["deaths_civilians"].sum(),
    })
    yearly = u.groupby(["iso3", u["date"].dt.year])["best"].sum()
    hist = {}
    for (iso, y), v in yearly.items():
        if y >= end.year - 9:
            hist.setdefault(iso, {})[int(y)] = int(v)
    out["ucdp_history"] = pd.Series(hist, dtype=object)
    out.attrs["data_end"] = str(end.date())
    return out


def gaza() -> dict:
    """Tech for Palestine (Gaza Ministry of Health) — killed in last 30 days + famine deaths."""
    d = _read("t4p_daily")
    if d.empty:
        return {}
    d["report_date"] = pd.to_datetime(d["report_date"])
    last = d["report_date"].max()
    recent = d[d["report_date"] > last - pd.Timedelta(days=30)]
    s = json.loads((LIVE / "t4p_summary.json").read_text(encoding="utf-8"))
    return {"killed_30d": float(recent["killed"].fillna(0).sum()),
            "killed_total": s["killed"]["total"], "children_killed": s["killed"]["children"],
            "women_killed": s["killed"].get("women", 0),
            "injured_total": s["injured"]["total"],
            "famine_deaths": float(d["famine_cum"].dropna().max()) if "famine_cum" in d else None,
            "child_famine_deaths": float(d["child_famine_cum"].dropna().max()) if "child_famine_cum" in d else None,
            "aid_seekers_killed": float(d["aid_seeker_killed_cum"].dropna().max()) if "aid_seeker_killed_cum" in d else None,
            "last_update": s.get("lastDailyUpdate"), **_west_bank()}


def _west_bank() -> dict:
    w = _read("t4p_west_bank")
    if w.empty:
        return {}
    last = w.ffill().iloc[-1]
    return {"wb_killed": float(last["killed_cum"]), "wb_children_killed": float(last["killed_children_cum"]),
            "wb_settler_attacks": float(last["settler_attacks_cum"]),
            "wb_displaced": float(last["displaced_persons_cum"])}


def structural() -> pd.DataFrame:
    lk = name_lookup()
    out = ucdp_by_country()
    ghi = _read("ghi")
    ghi["iso3"] = to_iso(ghi["country"], lk)
    out = out.join(ghi.dropna(subset=["iso3"]).groupby("iso3")["ghi_2026"].first(), how="outer")
    out = out.join(ghi.dropna(subset=["iso3"]).groupby("iso3")[["ghi_provisional", "ghi_2018"]].first(), how="outer")
    unmatched = {"ghi": sorted(ghi.loc[ghi["iso3"].isna(), "country"])}
    out.attrs["unmatched"] = unmatched

    app = _read("ifrc_appeals")
    if not app.empty:
        app = app[app["requested"] > 0]
        g = app.groupby("iso3")[["requested", "funded"]].sum()
        out = out.join(g.rename(columns={"requested": "ifrc_requested", "funded": "ifrc_funded"}), how="outer")
        out["ifrc_funded_pct"] = (out["ifrc_funded"] / out["ifrc_requested"] * 100).clip(upper=100).round(1)
        out["ifrc_appeals"] = app.groupby("iso3").apply(
            lambda d: d.sort_values("requested", ascending=False)[["name", "type", "requested", "funded", "start"]]
            .head(4).to_dict("records"))
    return out


# ---------- live: disasters + news ----------

def _point_in_poly(lon, lat, rings) -> bool:
    inside = False
    for ring in rings:
        j = len(ring) - 1
        for i in range(len(ring)):
            xi, yi = ring[i]
            xj, yj = ring[j]
            if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / (yj - yi) + xi:
                inside = not inside
            j = i
    return inside


def haversine(lat1, lon1, lat2, lon2) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def locate_iso3(lon, lat, countries_gj) -> str:
    """Point -> ISO3 (or nearest country centroid within ~600 km for offshore events)."""
    for f in countries_gj["features"]:
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        if any(_point_in_poly(lon, lat, p) for p in polys):
            return f["properties"]["iso3"]
    best, dist = "", 1e9
    for f in countries_gj["features"]:
        p = f["properties"]
        d = haversine(lat, lon, p["lat"], p["lon"])
        if d < dist:
            best, dist = p["iso3"], d
    return best if dist < 600 else ""


ALERT_W = {"Red": 3.0, "Orange": 1.5, "Yellow": 0.5, "Green": 0.2}


def live_events(countries_gj) -> list[dict]:
    p = LIVE / "disasters.json"
    events = json.loads(p.read_text(encoding="utf-8")) if p.exists() else []
    out = []
    for e in events:
        if e.get("lat") is None:
            continue
        if not e.get("iso3"):
            e["iso3"] = locate_iso3(e["lon"], e["lat"], countries_gj)
        e["age_days"] = round(_age_days(e["date"]), 1)
        if e["age_days"] <= 45:
            out.append(e)
    return out


def disaster_scores(events: list[dict]) -> pd.DataFrame:
    """Two separate signals (combined with vulnerability in build_dashboard):

    hazard — time-decayed natural-hazard alerts (half-life 10 days). A hazard alone is not a
             humanitarian need: a M5.5 quake in the USA is handled by the state.
    ifrc   — newly launched IFRC appeals/DREFs. These already mean the national capacity was
             exceeded, so they are NOT discounted by vulnerability.
    """
    hz, ifrc = {}, {}
    for e in events:
        if e.get("iso3"):
            w = ALERT_W.get(e.get("alert") or "Green", 0.2) * 0.5 ** (e["age_days"] / 10)
            hz[e["iso3"]] = hz.get(e["iso3"], 0) + w
    app = _read("ifrc_appeals")
    if not app.empty:
        for _, a in app.iterrows():
            age = _age_days(a["start"])
            if a["iso3"] and age <= 45:
                w = (2.0 if a["type"] == "Emergency Appeal" else 1.0) * 0.5 ** (age / 10)
                ifrc[a["iso3"]] = ifrc.get(a["iso3"], 0) + w
    return pd.DataFrame({"hazard": pd.Series(hz, dtype=float),
                         "ifrc": pd.Series(ifrc, dtype=float)}).div(3.0).clip(upper=1.0)


def news() -> pd.DataFrame:
    p = LIVE / "news.json"
    if not p.exists():
        return pd.DataFrame()
    df = pd.DataFrame(json.loads(p.read_text(encoding="utf-8"))).drop_duplicates("id")
    df["age_days"] = df["date"].map(_age_days)
    df = df[df["age_days"] <= 30].copy()
    texts = (df["title"] + ". " + df["text"].fillna("")).tolist()
    preds = sector_model.predict(texts) if texts else []
    df["sectors"] = [p["sectors"] for p in preds]
    pil = pillar_model.predict_proba(texts) if texts else []
    df["p_casualties"] = [p["Casualties"] for p in pil]
    df["p_displacement"] = [p["Displacement"] for p in pil]
    return df


def conflict_news_scores(news_df: pd.DataFrame) -> pd.Series:
    """Real-time violence signal from independent reporting: decayed sum of P(casualties).

    Each outlet's contribution per country is capped at 1, so a national newspaper covering
    its own country intensively (e.g. Dawn → Pakistan) cannot dominate; the signal needs
    several independent outlets reporting casualties (4 outlets at full strength = max).
    """
    if news_df.empty:
        return pd.Series(dtype=float)
    d = news_df[(news_df["age_days"] <= 14) & (news_df["group"] == "independent")]
    d = d.explode("iso3s").dropna(subset=["iso3s"])
    # only articles the model classifies as reporting casualties (its tuned threshold, 0.55);
    # summing many low probabilities produced noise (e.g. a comedian's remark scored as casualties)
    d = d[d["p_casualties"] >= 0.55]
    d = d.assign(w=d["p_casualties"] * 0.5 ** (d["age_days"] / 7))
    per_source = d.groupby(["iso3s", "source"])["w"].sum().clip(upper=1.0)
    return (per_source.groupby(level=0).sum() / 4.0).clip(upper=1.0)


def attention(news_df: pd.DataFrame) -> pd.DataFrame:
    if news_df.empty:
        return pd.DataFrame()
    d = news_df.explode("iso3s").dropna(subset=["iso3s"])
    return d.groupby(["iso3s", "group"]).size().unstack(fill_value=0)


# ---------- trends: is the situation getting worse or better? ----------

def monthly_violence() -> pd.DataFrame:
    """Deaths per month and country (UCDP), Gaza from the Ministry of Health daily series."""
    u = _read("ucdp_events")
    u["iso3"] = to_iso(u["country"], name_lookup())
    u.loc[u["adm_1"].fillna("").str.contains("Gaza|West Bank", case=False), "iso3"] = "PSE"
    u["m"] = pd.to_datetime(u["date_start"], errors="coerce").dt.to_period("M")
    end = u["m"].max()
    u = u[u["m"] > end - 24]
    piv = u.pivot_table(index="iso3", columns="m", values="best", aggfunc="sum", fill_value=0)
    piv = piv.reindex(columns=pd.period_range(end - 23, end, freq="M"), fill_value=0)
    d = _read("t4p_daily")
    if not d.empty:  # Gaza: Ministry of Health is the primary source
        d["m"] = pd.to_datetime(d["report_date"]).dt.to_period("M")
        g = d.groupby("m")["killed"].sum()
        piv.loc["PSE"] = g.reindex(piv.columns).fillna(piv.loc["PSE"] if "PSE" in piv.index else 0)
    return piv


def trends(pop: pd.Series) -> pd.DataFrame:
    """Recent 3-month mean vs median of the 12 months before (robust to a single massacre month).

    worsening : ratio >= 1.5, >= 50 deaths/month now, and not falling vs the previous quarter
    easing_ongoing : ratio <= 0.5 but killing continues (>= 100/month or heavy in >= 9 of 12 months)
    improving : ratio <= 0.5 and now < 20 deaths/month (strict: recent UCDP months are
                preliminary and usually revised UPWARD, so improvement is easy to over-read)
    chronic   : heavy violence in >= 9 of the last 12 months without a clear trend
    persistent: months with heavy violence (>= 100 deaths or >= 1 per 100k) in the last 12
    """
    piv = monthly_violence()
    cols = piv.columns
    recent = piv[cols[-3:]].mean(axis=1)
    prev3 = piv[cols[-6:-3]].mean(axis=1)
    base = piv[cols[-15:-3]].median(axis=1)
    ratio = (recent + 5) / (base + 5)
    p = pop.reindex(piv.index)
    heavy = (piv[cols[-12:]].ge(100)) | (piv[cols[-12:]].div(p, axis=0).mul(1e5).ge(1))
    out = pd.DataFrame({"recent_monthly": recent.round(0), "base_monthly": base.round(0),
                        "trend_ratio": ratio.round(2), "heavy_months_12": heavy.sum(axis=1)})
    ongoing = (recent >= 100) | (out["heavy_months_12"] >= 9)
    out["status"] = "stable"
    out.loc[out["heavy_months_12"] >= 9, "status"] = "chronic"
    # worsening: clearly above the usual level, a meaningful absolute size (>= 50/month, so a rise
    # from 4 to 28 deaths is not flagged), and not already falling from an even worse previous quarter
    worse = (ratio >= 1.5) & (recent >= 50) & (recent >= 0.8 * prev3)
    # easing: below the usual level OR well below the previous quarter (e.g. after a spike)
    easing = ((ratio <= 0.5) & (base >= 20)) | ((recent <= 0.5 * prev3) & (prev3 >= 100))
    out.loc[worse, "status"] = "worsening"
    # a drop in recorded deaths is NOT called improvement while killing continues
    out.loc[easing & ~worse & ongoing, "status"] = "easing_ongoing"
    out.loc[easing & ~worse & ~ongoing & (recent < 20), "status"] = "improving"
    # 0..1: a doubling = 0.33, 8x = 1
    out["escalation"] = (np.log2(ratio.clip(lower=1)) / 3).clip(upper=1).where(out["status"] == "worsening", 0)
    out["prev3_monthly"] = prev3.round(0)
    out["monthly"] = [{str(c): int(v) for c, v in row.items()} for _, row in piv.iterrows()]
    out.attrs["months"] = [str(c) for c in cols]
    return out
