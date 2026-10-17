"""Download all (non-UN) sources into data/raw and data/processed.

Usage:  python -m src.ingest            # everything (structured indices + live)
        python -m src.ingest --live     # only news, disasters, IFRC appeals, Gaza data
"""
import argparse
import json
from datetime import datetime, timezone

import pandas as pd
import requests

from src.config import LIVE, PROCESSED, USER_AGENT, WEB_DATA
from src.sources import independent as ind
from src.sources import live, news

NE_URL = ("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/"
          "master/geojson/ne_110m_admin_0_countries.geojson")
TODAY = datetime.now(timezone.utc).date().isoformat()


def save_json(obj, path):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


def ingest_countries():
    """Slim Natural Earth countries for the web map."""
    gj = requests.get(NE_URL, headers={"User-Agent": USER_AGENT}, timeout=120).json()
    rows = []
    for f in gj["features"]:
        p = f["properties"]
        iso3 = p["ISO_A3"] if p["ISO_A3"] != "-99" else p["ADM0_A3"]
        f["properties"] = {"iso3": iso3, "name": p["NAME"], "name_tr": p.get("NAME_TR"),
                           "lat": p["LABEL_Y"], "lon": p["LABEL_X"]}
        rows.append({"iso3": iso3, "name": p["NAME"], "name_long": p["NAME_LONG"],
                     "name_tr": p.get("NAME_TR"), "lat": p["LABEL_Y"], "lon": p["LABEL_X"],
                     "region": p["REGION_UN"], "subregion": p["SUBREGION"],
                     "pop_est": p["POP_EST"], "pop_year": p.get("POP_YEAR")})
    save_json(gj, WEB_DATA / "countries.geojson")
    pd.DataFrame(rows).to_parquet(PROCESSED / "countries.parquet")
    print(f"countries: {len(rows)}")


def ingest_structured():
    steps = {
        "ucdp_events": ind.ucdp_events,
        "ghi": ind.ghi,
        "ifrc_societies": ind.ifrc_societies,
        "oecd_humanitarian": ind.oecd_humanitarian,
    }
    for name, fn in steps.items():
        try:
            df = fn()
            df.to_parquet(PROCESSED / f"{name}.parquet")
            print(f"{name}: {len(df)} rows")
        except Exception as e:
            print(f"{name}: FAILED ({type(e).__name__}: {e})")


def _merge_store(name: str, items: list[dict]):
    """Accumulate history so the models keep seeing new data over time."""
    path = LIVE / f"{name}.json"
    old = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    stamp = datetime.now(timezone.utc).isoformat()
    new = {x["id"]: {**x, "fetched_at": stamp} for x in items}
    merged = list(new.values()) + [x for x in old if x["id"] not in new]
    save_json(merged, path)
    return len(new), len(merged)


def ingest_live():
    # news (independent + western comparison), tagged with countries
    items = news.fetch_all()
    for x in items:
        x["iso3s"] = news.tag_countries(x["title"] + " " + x["text"])
    print("news: %d fetched, %d stored" % _merge_store("news", items))

    events = []
    for fn in (live.usgs_quakes, ind.eonet):
        try:
            events += fn()
        except Exception as e:
            print(f"{fn.__name__}: FAILED ({e})")
    print("disasters: %d fetched, %d stored" % _merge_store("disasters", events))

    try:
        ind.ifrc_appeals(TODAY).to_parquet(PROCESSED / "ifrc_appeals.parquet")
        print("IFRC appeals: ok")
    except Exception as e:
        print(f"IFRC appeals: FAILED ({e})")

    try:
        t4p = ind.tech4palestine()
        save_json(t4p["summary"], LIVE / "t4p_summary.json")
        t4p["daily"].to_parquet(PROCESSED / "t4p_daily.parquet")
        t4p["west_bank"].to_parquet(PROCESSED / "t4p_west_bank.parquet")
        print("Tech for Palestine: ok, last update", t4p["summary"].get("lastDailyUpdate"))
    except Exception as e:
        print(f"Tech for Palestine: FAILED ({e})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="only refresh live feeds")
    a = ap.parse_args()
    if not a.live:
        ingest_countries()
        ingest_structured()
    ingest_live()
