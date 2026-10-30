"""GDELT 2.0 event files -> which countries the world's media write about, by media group.

GDELT publishes every 15 minutes a file of news-reported events with the place where the
event happened (FIPS country code) and the article URL. We sample one file every 30 minutes
over the last N days, keep one row per (article, event country), and label each article by
the outlet's domain: Western mainstream, Turkish, or other.

This scales the attention analysis from ~90 hand-collected RSS items to tens of thousands
of articles (instructor feedback on Assignment 1).

Usage:  python -m src.sources.gdelt [days]      -> data/processed/gdelt_articles.parquet
"""
import io
import re
import sys
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import pandas as pd
import requests

from src.config import PROCESSED, USER_AGENT

BASE = "https://data.gdeltproject.org/gdeltv2/{}.export.CSV.zip"
NE_URL = ("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/"
          "master/geojson/ne_110m_admin_0_countries.geojson")
COL_COUNTRY, COL_URL = 53, 60  # ActionGeo_CountryCode (FIPS 10-4), SOURCEURL

WESTERN = {"bbc.co.uk", "bbc.com", "theguardian.com", "nytimes.com", "cnn.com", "washingtonpost.com",
           "reuters.com", "apnews.com", "foxnews.com", "nbcnews.com", "cbsnews.com", "abcnews.go.com",
           "npr.org", "wsj.com", "telegraph.co.uk", "independent.co.uk", "skynews.com", "news.sky.com",
           "latimes.com", "usatoday.com", "politico.com", "bloomberg.com", "ft.com", "time.com"}
TURKISH = {"dailysabah.com", "trtworld.com", "aa.com.tr", "trthaber.com", "yenisafak.com", "hurriyet.com.tr",
           "hurriyetdailynews.com", "sabah.com.tr", "milliyet.com.tr", "sozcu.com.tr", "cumhuriyet.com.tr",
           "ntv.com.tr", "haberturk.com", "aksam.com.tr", "star.com.tr", "birgun.net", "t24.com.tr",
           "bianet.org", "duvarenglish.com", "turkiyetoday.com", "dunya.com", "takvim.com.tr",
           "ensonhaber.com", "haber7.com", "sondakika.com", "cnnturk.com", "trt.net.tr", "ahaber.com.tr"}
# FIPS codes missing from Natural Earth (FIPS_10 = -99) or needing re-assignment (Gaza, West Bank)
FIPS_EXTRA = {"GZ": "PSE", "WE": "PSE", "IS": "ISR", "NO": "NOR", "KV": "XKX", "OD": "SSD", "RB": "SRB", "MJ": "MNE"}


def fips_to_iso3() -> dict:
    gj = requests.get(NE_URL, headers={"User-Agent": USER_AGENT}, timeout=120).json()
    out = {}
    for f in gj["features"]:
        p = f["properties"]
        iso3 = p["ISO_A3"] if p["ISO_A3"] != "-99" else p["ADM0_A3"]
        if p.get("FIPS_10") and p["FIPS_10"] != "-99":
            out[p["FIPS_10"]] = iso3
    out.update(FIPS_EXTRA)
    return out


def domain(url: str) -> str:
    host = (urlparse(url).hostname or "").lower()
    return host[4:] if host.startswith("www.") else host


def media_group(d: str) -> str:
    if d in WESTERN or any(d.endswith("." + w) for w in WESTERN):
        return "western"
    if d in TURKISH or d.endswith(".tr") or any(d.endswith("." + t) for t in TURKISH):
        return "turkish"
    return "other"


def _fetch(stamp: str) -> pd.DataFrame | None:
    try:
        r = requests.get(BASE.format(stamp), headers={"User-Agent": USER_AGENT}, timeout=60)
        if r.status_code != 200:
            return None
        z = zipfile.ZipFile(io.BytesIO(r.content))
        df = pd.read_csv(z.open(z.namelist()[0]), sep="\t", header=None, usecols=[1, COL_COUNTRY, COL_URL],
                         dtype=str, quoting=3, on_bad_lines="skip")
        df.columns = ["date", "fips", "url"]
        return df.dropna()
    except Exception:
        return None


def collect(days: int = 30, step_min: int = 30, workers: int = 8) -> pd.DataFrame:
    end = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    end -= timedelta(minutes=end.minute % 15 + 30)  # newest file that surely exists
    stamps = [(end - timedelta(minutes=step_min * i)).strftime("%Y%m%d%H%M%S")
              for i in range(days * 24 * 60 // step_min)]
    with ThreadPoolExecutor(workers) as ex:
        parts = [p for p in ex.map(_fetch, stamps) if p is not None]
    print(f"gdelt: {len(parts)}/{len(stamps)} files")
    df = pd.concat(parts, ignore_index=True)
    fmap = fips_to_iso3()
    df["iso3"] = df["fips"].map(fmap)
    df = df.dropna(subset=["iso3"]).drop_duplicates(["url", "iso3"])
    df["domain"] = df["url"].map(domain)
    df["group"] = df["domain"].map(media_group)
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d", errors="coerce")
    return enrich(df[["date", "iso3", "domain", "group", "url"]])


def _slug_text(url: str) -> str:
    path = urlparse(url).path
    return re.sub(r"[-_/.+%0-9]+", " ", path).lower()


def enrich(df: pd.DataFrame) -> pd.DataFrame:
    """Add the countries named in the article URL (same gazetteer as the RSS news).

    GDELT's automatic geocoder picks one place per event; a story about Gaza is often located in
    "Israel" (the acting state). Every article is therefore also counted for each country its URL
    names. `geo` keeps the provenance: "gdelt" (geocoder) or "url" (added from the URL).
    """
    from src.sources.news import PLACES, _rx
    pats = [(iso, re.compile(r"\b(" + "|".join(map(_rx, ws)) + r")\b", re.I)) for iso, ws in PLACES.items()]
    df = df[df.get("geo", pd.Series("gdelt", index=df.index)) != "url"].copy()
    df["geo"] = "gdelt"
    urls = df.drop_duplicates("url")[["date", "domain", "group", "url"]]
    slugs = urls["url"].map(_slug_text)
    extra = [dict(r, iso3=iso, geo="url") for (_, r), s in zip(urls.iterrows(), slugs)
             for iso, p in pats if p.search(s)]
    out = pd.concat([df, pd.DataFrame(extra)], ignore_index=True)
    return out.drop_duplicates(["url", "iso3"], keep="first")


if __name__ == "__main__":
    if sys.argv[1:2] == ["enrich"]:  # re-apply URL tagging to the stored file, no download
        d = enrich(pd.read_parquet(PROCESSED / "gdelt_articles.parquet"))
        d.to_parquet(PROCESSED / "gdelt_articles.parquet")
        print(d["geo"].value_counts().to_dict())
        sys.exit()
    d = collect(int(sys.argv[1]) if len(sys.argv) > 1 else 30)
    d.to_parquet(PROCESSED / "gdelt_articles.parquet")
    print(d["group"].value_counts().to_dict(), "articles:", d["url"].nunique(), "domains:", d["domain"].nunique())
