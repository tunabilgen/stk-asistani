"""Sub-national (admin-1 / province) profiles, computed on demand per country and cached.

Per province:
  violence  — UCDP events assigned to the nearest province centroid (deaths last 12 months / 3 years,
              civilian deaths, main conflict actors); Gaza/West Bank: Gaza MoH data at the national level
  climate   — Open-Meteo ERA5 reanalysis for the last full year: annual rainfall, mean temperature,
              coldest/warmest month; elevation (Open-Meteo / Copernicus DEM)
  news      — independent news items naming the province
Sources: Natural Earth admin-1, UCDP, Open-Meteo (ECMWF ERA5). No UN data.
"""
import json
import math
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import requests

from src import features
from src.config import LIVE, PROCESSED, RAW, USER_AGENT

ADMIN1 = RAW / "indep" / "ne_admin1.geojson"
CACHE = PROCESSED / "regions"
CACHE.mkdir(parents=True, exist_ok=True)
NE0 = ("https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"
       "ne_110m_admin_0_countries.geojson")
H = {"User-Agent": USER_AGENT}
_admin1 = {}


def _adm0_to_iso3() -> dict:
    """Natural Earth admin-1 uses ADM0_A3 codes (e.g. PSX for Palestine, SDS for South Sudan)."""
    p = PROCESSED / "adm0_map.json"
    if p.exists():
        return json.loads(p.read_text())
    gj = requests.get(NE0, headers=H, timeout=120).json()
    m = {}
    for f in gj["features"]:
        q = f["properties"]
        iso = q["ISO_A3"] if q["ISO_A3"] != "-99" else q["ADM0_A3"]
        m[q["ADM0_A3"]] = iso
    m.update({"PSX": "PSE", "SDS": "SSD", "KOS": "XKX"})
    p.write_text(json.dumps(m))
    return m


def _decimate(ring, max_pts=160):
    step = max(1, len(ring) // max_pts)
    pts = ring[::step]
    if pts[-1] != ring[-1]:
        pts.append(ring[-1])
    return [[round(x, 3), round(y, 3)] for x, y in pts]


def admin1(iso3: str) -> list[dict]:
    if not _admin1:
        m = _adm0_to_iso3()
        gj = json.loads(ADMIN1.read_text(encoding="utf-8"))
        for f in gj["features"]:
            q = f["properties"]
            iso = m.get(q["adm0_a3"], q["adm0_a3"])
            g = f["geometry"]
            if g is None:
                continue
            polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
            geom = {"type": "MultiPolygon", "coordinates": [[_decimate(r) for r in poly[:1]] for poly in polys]}
            _admin1.setdefault(iso, []).append({
                "id": q.get("iso_3166_2") or f"{iso}-{q['name']}", "name": q["name"],
                "name_tr": q.get("name_tr"), "type": q.get("type_en"),
                "lat": q["latitude"], "lon": q["longitude"], "geometry": geom})
    return _admin1.get(iso3, [])


def _haversine_matrix(lat, lon, clat, clon):
    r = np.pi / 180
    dlat = (clat[None, :] - lat[:, None]) * r
    dlon = (clon[None, :] - lon[:, None]) * r
    a = np.sin(dlat / 2) ** 2 + np.cos(lat[:, None] * r) * np.cos(clat[None, :] * r) * np.sin(dlon / 2) ** 2
    return 2 * 6371 * np.arcsin(np.sqrt(a))


def violence(iso3: str, provinces: list[dict]) -> dict:
    u = pd.read_parquet(PROCESSED / "ucdp_events.parquet")
    u["iso3"] = features.to_iso(u["country"], features.name_lookup())
    u.loc[u["adm_1"].fillna("").str.contains("Gaza|West Bank", case=False), "iso3"] = "PSE"
    u = u[(u["iso3"] == iso3) & u["latitude"].notna()].copy()
    if u.empty or not provinces:
        return {}
    u["date"] = pd.to_datetime(u["date_start"], errors="coerce")
    end = u["date"].max()
    clat = np.array([p["lat"] for p in provinces])
    clon = np.array([p["lon"] for p in provinces])
    d = _haversine_matrix(u["latitude"].to_numpy(), u["longitude"].to_numpy(), clat, clon)
    u["prov"] = [provinces[i]["id"] for i in d.argmin(axis=1)]
    out = {}
    for pid, g in u.groupby("prov"):
        last12 = g[g["date"] > end - pd.Timedelta(days=365)]
        last3y = g[g["date"] > end - pd.Timedelta(days=3 * 365)]
        actors = (last12["side_a"] + " – " + last12["side_b"]).value_counts().head(2).index.tolist()
        out[pid] = {"deaths_12m": int(last12["best"].sum()), "deaths_3y": int(last3y["best"].sum()),
                    "civilian_12m": int(last12["deaths_civilians"].sum()), "events_12m": int(len(last12)),
                    "last_event": str(g["date"].max().date()), "actors": actors}
    return out


def climate(provinces: list[dict]) -> dict:
    """ERA5 daily means for the last full year, via Open-Meteo (batched by 20 locations)."""
    year = datetime.now(timezone.utc).year - 1
    out = {}
    for i in range(0, len(provinces), 20):
        batch = provinces[i:i + 20]
        lat = ",".join(f"{p['lat']:.3f}" for p in batch)
        lon = ",".join(f"{p['lon']:.3f}" for p in batch)
        for attempt in range(3):
            try:
                r = requests.get("https://archive-api.open-meteo.com/v1/archive", headers=H, timeout=120,
                                 params={"latitude": lat, "longitude": lon, "start_date": f"{year}-01-01",
                                         "end_date": f"{year}-12-31",
                                         "daily": "temperature_2m_mean,precipitation_sum", "timezone": "GMT"})
                r.raise_for_status()
                break
            except requests.RequestException:
                time.sleep(3 * (attempt + 1))
        else:
            continue
        js = r.json()
        js = js if isinstance(js, list) else [js]
        for p, j in zip(batch, js):
            d = pd.DataFrame(j["daily"])
            d["m"] = d["time"].str[5:7]
            monthly = d.groupby("m")["temperature_2m_mean"].mean()
            out[p["id"]] = {"rain_mm": round(float(d["precipitation_sum"].sum())),
                            "temp_mean": round(float(d["temperature_2m_mean"].mean()), 1),
                            "temp_coldest": round(float(monthly.min()), 1),
                            "temp_warmest": round(float(monthly.max()), 1),
                            "elevation": j.get("elevation"), "year": year}
        time.sleep(0.5)
    return out


def news_mentions(provinces: list[dict]) -> dict:
    p = LIVE / "news.json"
    if not p.exists():
        return {}
    items = [x for x in json.loads(p.read_text(encoding="utf-8")) if x.get("group") == "independent"]
    out = {}
    for prov in provinces:
        name = prov["name"].lower()
        if len(name) < 4:
            continue
        hits = [x for x in items if name in (x["title"] + " " + x.get("text", "")).lower()]
        if hits:
            out[prov["id"]] = [{"title": x["title"], "url": x["url"], "source": x["source"],
                                "date": str(x["date"])[:10]} for x in hits[:5]]
    return out


def security_level(v: dict | None, national_recent: float) -> str:
    """low / medium / high from deaths in the last 12 months in the province."""
    d = (v or {}).get("deaths_12m", 0)
    if d >= 100:
        return "high"
    if d >= 10:
        return "medium"
    return "low"


def profile(iso3: str, refresh: bool = False) -> dict:
    cache = CACHE / f"{iso3}.json"
    if cache.exists() and not refresh:
        age = time.time() - cache.stat().st_mtime
        if age < 7 * 86400:
            return json.loads(cache.read_text(encoding="utf-8"))
    provs = admin1(iso3)
    vio = violence(iso3, provs)
    clim = climate(provs)
    nws = news_mentions(provs)
    out = []
    for p in provs:
        v = vio.get(p["id"])
        out.append({**{k: p[k] for k in ("id", "name", "name_tr", "type", "lat", "lon")},
                    "violence": v or {"deaths_12m": 0, "deaths_3y": 0, "civilian_12m": 0, "events_12m": 0},
                    "security": security_level(v, 0), "climate": clim.get(p["id"]),
                    "news": nws.get(p["id"], [])})
    res = {"iso3": iso3, "generated_at": datetime.now(timezone.utc).isoformat(timespec="minutes"),
           "provinces": out,
           "geometry": {"type": "FeatureCollection", "features": [
               {"type": "Feature", "geometry": p["geometry"], "properties": {"id": p["id"], "name": p["name"]}}
               for p in provs]}}
    cache.write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
    return res
