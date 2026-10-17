"""Non-UN data sources: academic datasets, NGO indices, Red Cross/Red Crescent, science agencies.

| function        | publisher                                        | type          |
|-----------------|--------------------------------------------------|---------------|
| ucdp_*          | Uppsala Conflict Data Program, Uppsala University | academic      |
| ghi             | Global Hunger Index — Concern Worldwide & Welthungerhilfe | NGO index |
| tech4palestine  | Tech for Palestine (Gaza Ministry of Health data)| volunteer open data |
| ifrc_*          | IFRC GO platform (Red Cross / Red Crescent)      | humanitarian movement |
| eonet           | NASA Earth Observatory Natural Event Tracker      | science agency |
"""
import io
import re
import zipfile

import pandas as pd
import requests

from src.config import USER_AGENT

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " + USER_AGENT}


def _get(url, **kw):
    r = requests.get(url, headers=H, timeout=300, **kw)
    r.raise_for_status()
    return r


# ---------- UCDP (conflict deaths, 1989 → present) ----------
UCDP_GED = "https://ucdp.uu.se/downloads/ged/ged261-csv.zip"
UCDP_CANDIDATE = ["https://ucdp.uu.se/downloads/candidateged/GEDEvent_v26_01_26_06.csv",
                  "https://ucdp.uu.se/downloads/candidateged/GEDEvent_v26_0_7.csv",
                  "https://ucdp.uu.se/downloads/candidateged/GEDEvent_v26_0_8.csv"]
UCDP_COLS = ["id", "year", "type_of_violence", "conflict_name", "side_a", "side_b", "country",
             "adm_1", "latitude", "longitude", "date_start", "deaths_civilians", "best"]


def ucdp_events(since_year: int = 2016) -> pd.DataFrame:
    """Georeferenced event dataset (final 1989–last year) + monthly candidate events (this year)."""
    z = zipfile.ZipFile(io.BytesIO(_get(UCDP_GED).content))
    ged = pd.read_csv(z.open(z.namelist()[0]), usecols=UCDP_COLS, low_memory=False)
    ged = ged[ged["year"] >= since_year]
    cand = [pd.read_csv(io.BytesIO(_get(u).content), usecols=UCDP_COLS, low_memory=False)
            for u in UCDP_CANDIDATE]
    df = pd.concat([ged, *cand], ignore_index=True).drop_duplicates("id", keep="last")
    df["date_start"] = df["date_start"].str[:10]
    return df


# ---------- Global Hunger Index 2026 ----------
def _range_mid(v: str):
    """'35-49.9*' -> 42.5 ; '<= 9.9*' -> 5 ; numeric strings -> float."""
    v = str(v).replace("*", "").strip()
    m = re.match(r"^(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)$", v)
    if m:
        return (float(m.group(1)) + float(m.group(2))) / 2
    if v.startswith("<"):
        return 5.0
    return pd.to_numeric(v, errors="coerce")


def ghi() -> pd.DataFrame:
    """GHI 2026 scores; countries with incomplete data get GHI's provisional category
    (e.g. Sudan, South Sudan, Yemen: 'alarming' 35-49.9) at the range midpoint."""
    raw = pd.read_excel(io.BytesIO(_get("https://www.globalhungerindex.org/xlsx/2026.xlsx").content),
                        sheet_name="GHI Ranking 2026", header=None).iloc[:, 1:8]
    raw.columns = ["rank", "country", "y2000", "y2006", "y2012", "y2018", "y2026"]
    rows = []
    for _, r in raw.iterrows():
        val = str(r["y2026"])
        if r["country"] is None or str(r["country"]) in ("nan", "Country") or val == "nan":
            continue
        provisional = "*" in val or "-" in val
        names = re.split(r",\s*|\s+and\s+", str(r["country"]))
        for n in names:
            rows.append({"country": n.strip(), "ghi_2026": _range_mid(val.replace("<5", "2.5")),
                         "ghi_2018": _range_mid(str(r["y2018"]).replace("<5", "2.5")),
                         "ghi_provisional": provisional})
    return pd.DataFrame(rows).dropna(subset=["ghi_2026"]).drop_duplicates("country")


# ---------- Tech for Palestine (Gaza MoH + West Bank) ----------
def tech4palestine() -> dict:
    base = "https://data.techforpalestine.org/api/v2/"
    summary = _get(base + "summary.json").json()
    daily = pd.DataFrame(_get(base + "casualties_daily.min.json").json())
    west_bank = pd.DataFrame(_get(base + "west_bank_daily.min.json").json()).drop(columns=["verified"], errors="ignore")
    return {"summary": summary, "daily": daily, "west_bank": west_bank}


# ---------- IFRC GO ----------
def _ifrc_all(path: str, **params) -> list[dict]:
    url, out = f"https://goadmin.ifrc.org/api/v2/{path}/", []
    params = {"limit": 500, **params}
    while url:
        j = _get(url, params=params).json()
        out += j["results"]
        url, params = j.get("next"), None
    return out


def ifrc_appeals(active_on: str) -> pd.DataFrame:
    rows = []
    for a in _ifrc_all("appeal", end_date__gt=active_on):
        c = a.get("country") or {}
        rows.append({"iso3": c.get("iso3"), "name": a["name"], "type": a["atype_display"],
                     "requested": float(a["amount_requested"] or 0),
                     "funded": float(a["amount_funded"] or 0),
                     "beneficiaries": a.get("num_beneficiaries"), "start": a["start_date"][:10],
                     "code": a["code"],
                     "url": f"https://go.ifrc.org/emergencies/{a['event']}" if a.get("event") else None})
    return pd.DataFrame(rows)


def ifrc_societies() -> pd.DataFrame:
    rows = [{"iso3": c["iso3"], "society": c.get("society_name"),
             "website": c.get("website") or c.get("society_url"),
             "directory": c.get("url_ifrc")}
            for c in _ifrc_all("country") if c.get("iso3") and c.get("society_name")]
    return pd.DataFrame(rows)


# ---------- NASA EONET ----------
EONET_KEEP = {"Severe Storms", "Volcanoes", "Floods", "Landslides", "Drought", "Dust and Haze"}


def eonet(days: int = 45) -> list[dict]:
    j = _get(f"https://eonet.gsfc.nasa.gov/api/v3/events?status=open&days={days}").json()
    out = []
    for e in j["events"]:
        cat = e["categories"][0]["title"]
        if cat not in EONET_KEEP or not e.get("geometry"):
            continue
        g = e["geometry"][-1]
        lon, lat = g["coordinates"][:2] if g["type"] == "Point" else g["coordinates"][0][0][:2]
        out.append({"source": "NASA EONET", "id": f"eonet-{e['id']}", "type": cat, "title": e["title"],
                    # EONET carries no impact level -> "Yellow"
                    "alert": "Yellow", "lat": lat, "lon": lon, "iso3": "", "date": g["date"],
                    "url": (e.get("sources") or [{}])[0].get("url")})
    return out


# ---------- OECD: humanitarian aid disbursed, by recipient ----------
OECD = "https://sdmx.oecd.org/public/rest/data/OECD.DCD.FSD,DSD_DAC2@DF_DAC2A,/"


def oecd_humanitarian(start: int = 2022) -> pd.DataFrame:
    """Humanitarian aid (DAC2A measure 216, all reporting donors, constant USD) per recipient/year.
    Also returns Türkiye's own reporting separately: it records the cost of hosting Syrian refugees
    in Türkiye as humanitarian aid to Syria, which does not reach people inside Syria."""
    def get(donor):
        r = _get(f"{OECD}{donor}..216.USD.Q?startPeriod={start}&format=csvfilewithlabels")
        d = pd.read_csv(io.StringIO(r.text))
        d["usd"] = d["OBS_VALUE"] * 10 ** d["UNIT_MULT"]
        return d[["RECIPIENT", "TIME_PERIOD", "usd"]].assign(donor=donor)
    return pd.concat([get("ALLD"), get("TUR")], ignore_index=True)
