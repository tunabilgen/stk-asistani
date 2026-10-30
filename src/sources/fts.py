"""OCHA Financial Tracking Service (FTS): humanitarian funding received per destination country.

UN data. It is used ONLY as an external benchmark in the attention-vs-funding analysis
(src/attention_analysis.py) — "does institutional funding reach the crises the media ignore?".
It never enters the crisis ranking.

Usage:  python -m src.sources.fts   -> data/processed/fts_funding.parquet
"""
import pandas as pd
import requests

from src.config import PROCESSED, USER_AGENT

API = "https://api.hpc.tools/v1/public"


def funding(years=(2025, 2026)) -> pd.DataFrame:
    h = {"User-Agent": USER_AGENT}
    loc = {d["id"]: d["iso3"] for d in requests.get(f"{API}/location", headers=h, timeout=60).json()["data"]
           if d.get("iso3")}
    rows = []
    for y in years:
        d = requests.get(f"{API}/fts/flow", params={"year": y, "groupby": "Location"}, headers=h,
                         timeout=120).json()["data"]
        # report3 = total funding by destination location (all flows, de-duplicated by FTS)
        obj = d["report3"]["fundingTotals"]["objects"][0]
        for o in obj["singleFundingObjects"]:
            if o.get("id") in loc:
                rows.append({"iso3": loc[o["id"]], "year": y, "funding_usd": o["totalFunding"]})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = funding()
    df.to_parquet(PROCESSED / "fts_funding.parquet")
    print(df.groupby("year")["funding_usd"].agg(["count", "sum"]))
    print(df[df.year == 2026].nlargest(12, "funding_usd").to_string(index=False))
