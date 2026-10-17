"""Live feeds: USGS significant earthquakes and (optional) GDELT news search."""
import time
from datetime import datetime, timezone

import requests

from src.config import USER_AGENT

H = {"User-Agent": USER_AGENT}


def usgs_quakes() -> list[dict]:
    """M5.5+ earthquakes of the last 30 days with PAGER impact alert."""
    r = requests.get("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/"
                     "significant_month.geojson", headers=H, timeout=60)
    r.raise_for_status()
    out = []
    for f in r.json()["features"]:
        p = f["properties"]
        lon, lat = f["geometry"]["coordinates"][:2]
        out.append({
            "source": "USGS", "id": f"usgs-{f['id']}", "type": "EQ",
            "title": p["title"], "alert": (p.get("alert") or "green").capitalize(),
            "mag": p["mag"], "lat": lat, "lon": lon, "iso3": "",
            "date": datetime.fromtimestamp(p["time"] / 1000, timezone.utc).isoformat(),
            "url": p["url"],
        })
    return out


def gdelt_articles(query: str, timespan: str = "3d", maxrecords: int = 75) -> list[dict]:
    """Global news via the GDELT DOC 2.0 API (max one request per 5 s)."""
    params = {"query": query, "mode": "artlist", "format": "json",
              "maxrecords": maxrecords, "timespan": timespan, "sort": "datedesc"}
    for attempt in range(3):
        r = requests.get("https://api.gdeltproject.org/api/v2/doc/doc",
                         params=params, headers=H, timeout=60)
        if r.status_code == 429:
            time.sleep(6 * (attempt + 1))
            continue
        r.raise_for_status()
        try:
            arts = r.json().get("articles", [])
        except ValueError:
            return []
        return [{"source": "GDELT", "id": a["url"], "title": a.get("title", ""),
                 "url": a["url"], "date": a.get("seendate"),
                 "country_name": a.get("sourcecountry"), "lang": a.get("language"),
                 "domain": a.get("domain"), "text": a.get("title", "")} for a in arts]
    return []
