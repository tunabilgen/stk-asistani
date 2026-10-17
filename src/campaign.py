"""Campaign recommendation generator (LLM, grounded on our own data).

The LLM (DeepSeek via any OpenAI-compatible endpoint) only *writes*; every fact it may use
is passed in a FACTS block built from UCDP, GHI, IFRC, Tech for Palestine and independent news. Afterwards we validate:
  - partner organisations must come from the candidate list (no invented NGOs),
  - every number in the output must appear in the facts (no invented statistics),
  - sources must be URLs we supplied.
If no API key is configured, or the call fails, a deterministic template is used instead.
"""
import json
import re

import requests

from src.config import LLM_API_KEY, LLM_BASE_URL, LLM_FALLBACK_MODELS, LLM_MODEL, SECTORS

SYSTEM = """You are "STK Asistanı", a humanitarian programming assistant for NGOs (STK).
Write a campaign recommendation for the NGO, using ONLY the facts in the FACTS block.
Rules:
- Never invent numbers, organisations, places or events. If a fact is missing, say it is unknown.
- Partners: choose only from FACTS.partner_candidates and always remind that due diligence is required.
- Data comes from independent sources (UCDP, Global Hunger Index, IFRC, Tech for Palestine,
  independent media). Name the source when you cite a figure. Mention known data gaps honestly.
- Respect dignity: no graphic or pitying language, no images of identifiable victims, no exaggeration.
- Follow Do-No-Harm and Core Humanitarian Standard principles; mention key risks.
- Write in the language requested (tr = Turkish, en = English).
Return ONLY valid JSON with keys:
title, summary, why_now (list), where (string), mode ("direct" or "partnership"),
target_groups (list), activities (list of {name, description}), partners (list of {name, reason}),
donor_message (string, <= 90 words), social_posts (list of 3 strings, <= 280 chars),
risks (list), kpis (list), sources (list of URLs from FACTS)."""


def build_facts(country: dict, ngo: dict, sectors: list[str], mode: str, events: list[dict]) -> dict:
    ind = country["ind"]
    return {
        "country": country["name"], "country_tr": country.get("name_tr") or country["name"],
        "iso3": country["iso3"], "deaths_source": ind.get("deaths_source") or "UCDP",
        "ngo": {"name": ngo.get("name", "NGO"), "home_country": ngo.get("home"),
                "sectors": [SECTORS[s][1] for s in sectors],
                "sectors_tr": [SECTORS[s][0] for s in sectors], "budget_band": ngo.get("budget")},
        "recommended_mode": mode,
        "distance_km": country.get("distance_km"),
        "indicators": {
            "conflict deaths, last 3 years (UCDP, Uppsala University)": ind.get("ucdp_deaths_3y"),
            "civilian deaths, last 3 years (UCDP)": ind.get("ucdp_civilian_3y"),
            "conflict deaths, last 90 days of data (UCDP)": ind.get("ucdp_deaths_90d"),
            "Global Hunger Index 2026 score (Concern/Welthungerhilfe; >=35 alarming)": ind.get("ghi_2026"),
            "GHI value is a provisional category midpoint": ind.get("ghi_provisional"),
            "vulnerability 0-1 (hunger or ongoing violence)": ind.get("vulnerability"),
            "IFRC appeals requested CHF": ind.get("ifrc_requested"),
            "IFRC appeals funded %": ind.get("ifrc_funded_pct"),
            "news items last 30 days: independent / Western": [ind.get("news_independent"),
                                                                 ind.get("news_western")],
        },
        "gaza_ministry_of_health_via_tech_for_palestine": country.get("gaza"),
        "ignored_by_western_media": country.get("forgotten"),
        "trend": {k: country.get("trend", {}).get(k) for k in
                  ("status", "recent_monthly", "base_monthly", "ratio", "heavy_months_12", "ghi_2018", "ghi_2026")},
        "acute_scores_0_1": {"natural_hazard": country["score"].get("acute_disaster"),
                             "recent_armed_violence": country["score"].get("acute_conflict")},
        "need_score_by_sector_0_1": {SECTORS[s][1]: country["score"]["sector"].get(s) for s in sectors},
        "known_data_gaps": [g["en"] for g in country.get("known_gaps", {}).values()],
        "ifrc_appeals": country.get("ifrc_appeals", []),
        "live_events": [{"title": e["title"], "alert": e.get("alert"), "date": (e.get("date") or "")[:10],
                         "url": e.get("url")} for e in events][:5],
        "recent_reports": [n for n in country.get("news", []) if n.get("group") != "western"][:8],
        "partner_candidates": [{"name": p["name"], "type": p.get("type"), "evidence": p.get("evidence")}
                               for p in country.get("partners", [])][:10],
    }


def _call_llm(facts: dict, lang: str, model: str) -> dict:
    r = requests.post(
        LLM_BASE_URL.rstrip("/") + "/chat/completions",
        headers={"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json",
                 "X-Title": "STK Asistani"},  # OpenRouter app attribution (optional)
        json={"model": model, "temperature": 0.3, "max_tokens": 2500,
              "response_format": {"type": "json_object"},
              "messages": [{"role": "system", "content": SYSTEM},
                           {"role": "user", "content": f"LANGUAGE: {lang}\nFACTS:\n"
                            + json.dumps(facts, ensure_ascii=False, default=str)}]},
        timeout=120)
    r.raise_for_status()
    text = r.json()["choices"][0]["message"]["content"]
    text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.M)
    return json.loads(text)


def _numbers(s: str) -> set[str]:
    return {re.sub(r"[.,\s]", "", m) for m in re.findall(r"\d[\d.,\s]{2,}\d", s)}


def validate(out: dict, facts: dict) -> list[str]:
    """Return warnings for anything not grounded in FACTS (and drop invented partners)."""
    warn = []
    allowed = {p["name"] for p in facts["partner_candidates"]}
    kept = [p for p in out.get("partners", []) if p.get("name") in allowed]
    if len(kept) < len(out.get("partners", [])):
        warn.append("Removed partner names not found among the candidates (IFRC societies / independent news).")
    out["partners"] = kept
    fact_text = json.dumps(facts, ensure_ascii=False, default=str)
    fact_nums = _numbers(fact_text) | {re.sub(r"\D", "", fact_text[m.start():m.end()])
                                       for m in re.finditer(r"\d+", fact_text)}
    body = json.dumps({k: v for k, v in out.items() if k != "sources"}, ensure_ascii=False)
    unknown = [n for n in _numbers(body) if n not in fact_nums and len(n) >= 4]
    if unknown:
        warn.append(f"Unverified numbers in text (check before use): {', '.join(sorted(unknown)[:6])}")
    urls = {x.get("url") for x in facts["recent_reports"] + facts["live_events"]}
    out["sources"] = [u for u in out.get("sources", []) if u in urls] or [u for u in urls if u][:4]
    return warn


def _fmt(n):
    if n is None:
        return "?"
    return f"{n/1e6:.1f}M" if n >= 1e6 else f"{n/1e3:.0f}K" if n >= 1e3 else str(round(n))


def template(facts: dict, lang: str) -> dict:
    """Deterministic fallback — no LLM needed."""
    tr = lang == "tr"
    c, ind = (facts["country_tr"] if tr else facts["country"]), facts["indicators"]
    src = facts["deaths_source"]
    src = "Gazze Sağlık Bakanlığı" if tr and src != "UCDP" else ("Gaza Ministry of Health" if src != "UCDP" else "UCDP")
    secs = facts["ngo"]["sectors_tr" if tr else "sectors"]
    sec = ", ".join(secs) or ("insani yardım" if tr else "humanitarian aid")
    partner = facts["recommended_mode"] == "partnership"
    why = []
    if ind["conflict deaths, last 3 years (UCDP, Uppsala University)"]:
        n = _fmt(ind["conflict deaths, last 3 years (UCDP, Uppsala University)"])
        why.append(f"Son 3 yılda çatışmalarda {n} ölüm ({src})" if tr else f"{n} conflict deaths in 3 years ({src})")
    if ind["Global Hunger Index 2026 score (Concern/Welthungerhilfe; >=35 alarming)"]:
        g = ind["Global Hunger Index 2026 score (Concern/Welthungerhilfe; >=35 alarming)"]
        why.append(f"Küresel Açlık Endeksi: {g}" if tr else f"Global Hunger Index: {g}")
    gz = facts.get("gaza_ministry_of_health_via_tech_for_palestine")
    if gz:
        tn = lambda x: f"{x:,.0f}".replace(",", ".")  # Turkish thousands separator
        why.append((f"Gazze'de {tn(gz['killed_total'])} kişi öldürüldü (bunların {tn(gz['children_killed'])} "
                    f"kadarı çocuk); {gz['famine_deaths']:.0f} kişi açlıktan öldü" if tr else
                    f"{gz['killed_total']:,} killed in Gaza incl. {gz['children_killed']:,} children; "
                    f"{gz['famine_deaths']:.0f} starvation deaths"))
    if ind["IFRC appeals funded %"] is not None:
        p = ind["IFRC appeals funded %"]
        why.append(f"Kızılay/Kızılhaç çağrıları yalnızca %{p:.0f} fonlandı" if tr
                   else f"Red Crescent/Red Cross appeals only {p:.0f}% funded")
    for e in facts["live_events"][:2]:
        why.append(f"{e['title']} ({e['alert']}, {e['date']})")
    if facts["ignored_by_western_media"]:
        why.append("Batı medyasının görmezden geldiği kriz" if tr else "Crisis ignored by Western media")
    return {
        "title": (f"{c}: {sec} kampanyası" if tr else f"{c}: {sec} campaign"),
        "summary": (f"{c} için {sec} alanında "
                    + ("yerel ortak üzerinden" if partner else "doğrudan") + " müdahale önerilir."
                    if tr else f"A {sec} response in {c}, delivered "
                    + ("through a local partner." if partner else "directly.")),
        "why_now": why, "where": c, "mode": facts["recommended_mode"],
        "target_groups": ["Kadınlar, çocuklar, yaşlılar, engelliler" if tr
                          else "Women, children, older people, persons with disabilities"],
        "activities": [{"name": s, "description": ""} for s in secs],
        "partners": [{"name": p["name"], "reason": p.get("evidence", "")}
                     for p in facts["partner_candidates"][:3]],
        "donor_message": "", "social_posts": [], "risks": [
            "Ortak kuruluş için durum tespiti (due diligence) şarttır" if tr
            else "Partner due diligence is required"],
        "kpis": [], "sources": [r["url"] for r in facts["recent_reports"][:3]],
    }


def generate(country, ngo, sectors, mode, events, lang="tr") -> dict:
    facts = build_facts(country, ngo, sectors, mode, events)
    engine, warn = "template", []
    if LLM_API_KEY:
        out = None
        for model in [LLM_MODEL, *LLM_FALLBACK_MODELS]:
            try:
                out = _call_llm(facts, lang, model)
                engine = model
                break
            except Exception as e:
                warn.append(f"{model} unavailable ({type(e).__name__}: {str(e)[:100]})")
        if out is None:
            warn.append("All LLMs failed; template used.")
            out = template(facts, lang)
    else:
        warn.append("No LLM API key configured (.env); template used.")
        out = template(facts, lang)
    warn += validate(out, facts)
    return {"campaign": out, "engine": engine, "warnings": warn, "facts": facts}


# ======================= place-specific sustainable project proposals =======================
PROJECT_SYSTEM = """You are "STK Asistanı", a programme designer for NGOs. Design ONE concrete, sustainable project
for the PROVINCE and PROJECT TYPE given in FACTS. Use ONLY the facts provided; where something must be checked on the
ground (land, water rights, local prices, number of households), say so explicitly under "verify_on_site".
Principles: Do No Harm, Core Humanitarian Standard, local ownership, women's participation where culturally possible,
no dependency — the project must be able to continue after the NGO leaves.
Crop suggestions come from coarse climate envelopes and must be confirmed with a local agronomist; never invent yields
or prices. Budget: give a percentage split across cost lines (not currency amounts) unless FACTS.ngo.budget_amount exists.
Write in the requested language (tr = Turkish, en = English).
Return ONLY valid JSON with keys:
title, location, problem (string), target_group {who, households_estimate_note}, why_here (list),
activities (list of {phase, name, description}), procurement (list of {item, purpose}),
training (list), sustainability (string), exit_strategy (string), partner (string), timeline (list of {month, milestone}),
budget_split (list of {line, percent}), kpis (list), risks (list of {risk, mitigation}), verify_on_site (list),
donor_message (string, <= 90 words), sources (list of URLs from FACTS)."""


def build_project_facts(country: dict, province: dict, project_key: str, ngo: dict, sectors: list[str],
                        field_note: str, lang: str) -> dict:
    from src import catalog
    p = catalog.PROJECTS[project_key]
    crops = catalog.suitable_crops(province.get("climate"))
    return {
        "country": country["name_tr"] if lang == "tr" and country.get("name_tr") else country["name"],
        "province": (province.get("name_tr") or province["name"]) if lang == "tr" else province["name"],
        "province_type": province.get("type"),
        "project_type": p["tr"] if lang == "tr" else p["en"],
        "project_template": {"items": p["items_tr" if lang == "tr" else "items_en"],
                             "sustainability_model": p["sust_tr" if lang == "tr" else "sust_en"],
                             "typical_risks": p["risks_tr" if lang == "tr" else "risks_en"],
                             "typical_duration_months": p["months"], "women_focus": p["women"]},
        "province_facts": {
            "security_level": province["security"],
            "conflict_deaths_last_12_months": province["violence"].get("deaths_12m"),
            "civilian_deaths_last_12_months": province["violence"].get("civilian_12m"),
            "main_conflict_actors": province["violence"].get("actors"),
            "climate_last_year": province.get("climate"),
            "crops_matching_climate (verify with agronomist)": [
                {"crop": c["tr"] if lang == "tr" else c["en"], "needs_irrigation": c["irrigation"]} for c in crops],
            "recent_news_naming_province": province.get("news", []),
        },
        "country_context": {
            "global_hunger_index_2026": country["ind"].get("ghi_2026"),
            "trajectory": country.get("trend", {}).get("status"),
            "aid_per_person_in_severe_need_usd": country["ind"].get("aid_per_person"),
            "red_crescent_society": next((x["name"] for x in country.get("partners", [])
                                          if "verified" in (x.get("evidence") or "")), None),
            "known_data_notes": [g["en"] for g in country.get("known_gaps", {}).values()],
        },
        "ngo": {"name": ngo.get("name"), "home_country": ngo.get("home"), "sectors": sectors,
                "budget_band": ngo.get("budget")},
        "field_note_from_ngo": field_note or None,
    }


def project_template(f: dict, key: str, lang: str) -> dict:
    from src import catalog
    tr = lang == "tr"
    p = catalog.PROJECTS[key]
    pf = f["province_facts"]
    crops = ", ".join(c["crop"] + (" (sulama)" if tr and c["needs_irrigation"] else " (irrigation)" if c["needs_irrigation"] else "")
                      for c in pf["crops_matching_climate (verify with agronomist)"][:6])
    cl = pf["climate_last_year"] or {}
    num = (lambda v: f"{v:,.0f}".replace(",", ".")) if tr else (lambda v: f"{v:,.0f}")
    dec = (lambda v: f"{v:.1f}".replace(".", ",")) if tr else (lambda v: f"{v:.1f}")
    sec_lbl = ({"low": "düşük risk", "medium": "orta risk", "high": "yüksek risk"} if tr
               else {"low": "low risk", "medium": "medium risk", "high": "high risk"})[pf["security_level"]]
    why = []
    if f.get("field_note_from_ngo"):
        why.append(("Sahadan not: " if tr else "Field note: ") + f["field_note_from_ngo"])
    if cl:
        why.append((f"İklim ({cl.get('year')}): yıllık yağış {num(cl['rain_mm'])} mm, ortalama {dec(cl['temp_mean'])}°C, "
                    f"en soğuk ay {dec(cl['temp_coldest'])}°C, rakım {num(cl.get('elevation') or 0)} m" if tr else
                    f"Climate ({cl.get('year')}): {num(cl['rain_mm'])} mm rain/yr, mean {dec(cl['temp_mean'])}°C, "
                    f"coldest month {dec(cl['temp_coldest'])}°C, elevation {num(cl.get('elevation') or 0)} m"))
    if crops:
        why.append(("İklime uygun ürünler (ziraat uzmanıyla doğrulanmalı): " if tr else "Crops matching the climate (verify): ") + crops)
    why.append((f"Güvenlik: {sec_lbl} (son 12 ayda {pf['conflict_deaths_last_12_months']} çatışma ölümü, UCDP)"
                if tr else f"Security: {sec_lbl} ({pf['conflict_deaths_last_12_months']} conflict deaths in 12 months, UCDP)"))
    return {
        "title": f"{f['province']}, {f['country']}: {f['project_type']}",
        "location": f"{f['province']} ({f['country']})", "problem": "", "target_group": {"who": "", "households_estimate_note": ""},
        "why_here": why,
        "activities": [], "procurement": [{"item": i, "purpose": ""} for i in p["items_tr" if tr else "items_en"]],
        "training": [], "sustainability": p["sust_tr" if tr else "sust_en"], "exit_strategy": "",
        "partner": f["country_context"]["red_crescent_society"] or "", "timeline": [], "budget_split": [], "kpis": [],
        "risks": [{"risk": r, "mitigation": ""} for r in p["risks_tr" if tr else "risks_en"]],
        "verify_on_site": (["arazi ve su hakları", "yerel fiyatlar", "hane sayısı ve seçim kriterleri", "ürün uygunluğu (ziraat uzmanı)"]
                           if tr else ["land and water rights", "local prices", "number of households and selection criteria",
                                       "crop suitability (agronomist)"]),
        "donor_message": "", "sources": [n["url"] for n in pf["recent_news_naming_province"][:3]],
    }


def generate_project(country, province, project_key, ngo, sectors, field_note, lang="tr") -> dict:
    facts = build_project_facts(country, province, project_key, ngo, sectors, field_note, lang)
    engine, warn, out = "template", [], None
    if LLM_API_KEY:
        for model in [LLM_MODEL, *LLM_FALLBACK_MODELS]:
            try:
                r = requests.post(
                    LLM_BASE_URL.rstrip("/") + "/chat/completions",
                    headers={"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json",
                             "X-Title": "STK Asistani"},
                    json={"model": model, "temperature": 0.4, "max_tokens": 3500,
                          "response_format": {"type": "json_object"},
                          "messages": [{"role": "system", "content": PROJECT_SYSTEM},
                                       {"role": "user", "content": f"LANGUAGE: {lang}\nFACTS:\n"
                                        + json.dumps(facts, ensure_ascii=False, default=str)}]},
                    timeout=180)
                r.raise_for_status()
                text = re.sub(r"^```(json)?|```$", "", r.json()["choices"][0]["message"]["content"].strip(), flags=re.M)
                out, engine = json.loads(text), model
                break
            except Exception as e:
                warn.append(f"{model} unavailable ({type(e).__name__}: {str(e)[:100]})")
    else:
        warn.append("No LLM API key configured (.env); template used.")
    if out is None:
        out = project_template(facts, project_key, lang)
    urls = {n["url"] for n in facts["province_facts"]["recent_news_naming_province"]}
    out["sources"] = [u for u in out.get("sources", []) if u in urls]
    fact_nums = _numbers(json.dumps(facts, ensure_ascii=False, default=str))
    body = json.dumps({k: v for k, v in out.items() if k not in ("sources", "budget_split")}, ensure_ascii=False)
    unknown = [x for x in _numbers(body) if x not in fact_nums and len(x) >= 4]
    if unknown:
        warn.append(f"Unverified numbers in text (check before use): {', '.join(sorted(unknown)[:6])}")
    return {"project": out, "engine": engine, "warnings": warn, "facts": facts}
