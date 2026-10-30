"""ReliefWeb (UN OCHA) report counts per country — BENCHMARK ONLY, never used in the ranking.

Question (instructor feedback on Assignment 1): when mainstream media are silent about a crisis, does the
humanitarian system (UN agencies, NGOs, Red Cross) still report on it?  ReliefWeb is the main publication
platform of that system, so the number of reports per country is a measure of "humanitarian attention".

The ReliefWeb API now needs a pre-approved appname, so we use the public RSS feed, which returns the 20 newest
reports for a search. We count reports per primary country over the same 30 days as GDELT by querying day
ranges and splitting any range that hits the 20-item cap.

Usage:  python -m src.sources.reliefweb [start YYYY-MM-DD] [end YYYY-MM-DD]
Output: data/processed/reliefweb_counts.parquet (iso3, reports, capped_days)
"""
import re
import sys
import time
from datetime import date, timedelta

import pandas as pd
import requests

from src.config import PROCESSED, ROOT, USER_AGENT

RSS = "https://reliefweb.int/updates/rss.xml"
CAP = 20
OUT = PROCESSED / "reliefweb_counts.parquet"


def _fetch(iso3: str, d0: date, d1: date) -> set[str]:
    q = f"primary_country.iso3:{iso3.lower()} AND date.created:[{d0} TO {d1}]"
    for attempt in range(3):
        try:
            r = requests.get(RSS, params={"search": q}, headers={"User-Agent": USER_AGENT}, timeout=60)
            r.raise_for_status()
            time.sleep(0.4)  # be polite to a public service
            return set(re.findall(r"<guid[^>]*>([^<]+)</guid>", r.text))
        except requests.RequestException:
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"ReliefWeb RSS failed for {iso3} {d0}..{d1}")


def count(iso3: str, d0: date, d1: date) -> tuple[int, int]:
    """Reports with primary country iso3 created in [d0, d1]; second value = days still at the cap."""
    ids = _fetch(iso3, d0, d1)
    if len(ids) < CAP:
        return len(ids), 0
    if d0 == d1:  # more than 20 reports in one day: count is a lower bound
        return len(ids), 1
    mid = d0 + (d1 - d0) // 2
    a, b = count(iso3, d0, mid), count(iso3, mid + timedelta(days=1), d1)
    return a[0] + b[0], a[1] + b[1]


def collect(isos: list[str], d0: date, d1: date) -> pd.DataFrame:
    rows = []
    for iso in isos:
        n, capped = count(iso, d0, d1)
        rows.append({"iso3": iso, "reports": n, "capped_days": capped})
        print(iso, n, "capped" if capped else "", flush=True)
    df = pd.DataFrame(rows)
    df.attrs = {"start": str(d0), "end": str(d1)}
    df.to_parquet(OUT, index=False)
    return df


if __name__ == "__main__":
    end = date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else date.today() - timedelta(days=1)
    start = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else end - timedelta(days=29)
    ds = pd.read_csv(ROOT / "data/final/country_crisis_dataset.csv")
    isos = ds.loc[ds["n_prot"] >= 0.30, "iso3"].tolist()  # same crisis set as src/attention_analysis.py
    collect(isos, start, end)
