"""STK Asistanı — local web server.

    python app.py            ->  http://localhost:8000

Serves the interactive map (web/) and the API used by it:
  POST /api/campaign   generate a grounded campaign recommendation (LLM or template)
  POST /api/feedback   human correction of a news item's sectors (feeds self-training)
  POST /api/refresh    refresh live feeds + rebuild dashboard data
"""
import json
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from src import campaign
from src.config import DATA, LLM_API_KEY, LLM_MODEL, SECTORS, WEB_DATA

WEB = Path(__file__).parent / "web"
app = Flask(__name__, static_folder=None)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0  # always serve fresh data/js after a rebuild


def dashboard():
    return json.loads((WEB_DATA / "dashboard.json").read_text(encoding="utf-8"))


@app.get("/")
def index():
    return send_from_directory(WEB, "index.html")


@app.get("/<path:p>")
def static_files(p):
    return send_from_directory(WEB, p)


@app.get("/api/status")
def status():
    return jsonify({"llm": LLM_MODEL if LLM_API_KEY else None})


@app.post("/api/campaign")
def make_campaign():
    q = request.get_json(force=True)
    d = dashboard()
    country = next((c for c in d["countries"] if c["iso3"] == q["iso3"]), None)
    if not country:
        return jsonify({"error": "unknown country"}), 404
    country["distance_km"] = q.get("distance_km")
    sectors = [s for s in q.get("sectors", []) if s in SECTORS]
    events = [e for e in d["events"]
              if q["iso3"] in (e.get("iso3s") or []) or e.get("iso3") == q["iso3"]]
    return jsonify(campaign.generate(country, q.get("ngo", {}), sectors,
                                     q.get("mode", "direct"), events, q.get("lang", "tr")))


@app.get("/api/regions/<iso3>")
def regions_api(iso3):
    from src import catalog, regions
    import math
    d = dashboard()
    country = next((c for c in d["countries"] if c["iso3"] == iso3), None)
    if not country:
        return jsonify({"error": "unknown country"}), 404
    sectors = set(filter(None, request.args.get("sectors", "").split(",")))
    budget = request.args.get("budget", "medium")
    prof = regions.profile(iso3)
    hunger = (country["ind"].get("ghi_2026") or 0) / 50
    lang = request.args.get("lang", "tr")
    out = []
    for p in prof["provinces"]:
        v = p["violence"]
        # province need: violence burden (log) + national hunger + being in the news
        need = 0.5 * min(1, math.log10(1 + v.get("deaths_3y", 0)) / 4) + 0.4 * min(1, hunger) + (0.1 if p["news"] else 0)
        ideas = catalog.match(p, sectors, budget, hunger)
        for i in ideas:
            t = catalog.PROJECTS[i["key"]]
            i["name"] = t["tr"] if lang == "tr" else t["en"]
            i["women"] = t["women"]
            i["months"] = t["months"]
            i["crops"] = [c["tr"] if lang == "tr" else c["en"] for c in i["crops"]]
        out.append({**p, "need": round(need, 3), "ideas": ideas})
    out.sort(key=lambda p: -p["need"])
    return jsonify({"iso3": iso3, "generated_at": prof["generated_at"], "provinces": out, "geometry": prof["geometry"]})


@app.post("/api/project")
def project_api():
    from src import regions
    q = request.get_json(force=True)
    d = dashboard()
    country = next((c for c in d["countries"] if c["iso3"] == q["iso3"]), None)
    prov = next((p for p in regions.profile(q["iso3"])["provinces"] if p["id"] == q["province"]), None)
    if not country or not prov:
        return jsonify({"error": "unknown country or province"}), 404
    sectors = [s for s in q.get("sectors", []) if s in SECTORS]
    return jsonify(campaign.generate_project(country, prov, q["project"], q.get("ngo", {}), sectors,
                                             q.get("field_note", ""), q.get("lang", "tr")))


@app.post("/api/feedback")
def feedback():
    q = request.get_json(force=True)
    labels = [s for s in q.get("labels", []) if s in SECTORS]
    if not q.get("text"):
        return jsonify({"error": "text required"}), 400
    path = DATA / "feedback" / "labels.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"text": q["text"], "labels": labels}, ensure_ascii=False) + "\n")
    return jsonify({"ok": True})


@app.post("/api/refresh")
def refresh():
    from src import build_dashboard, ingest
    ingest.ingest_live()
    build_dashboard.build()
    return jsonify({"ok": True, "generated_at": dashboard()["generated_at"]})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=False)
