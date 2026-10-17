"""Partner candidates for remote operations (no UN sources).

1. The country's Red Crescent / Red Cross National Society — verified via the IFRC GO directory.
   Natural first partner for Turkish NGOs (Türk Kızılay is a sister society).
2. Organisations named in independent news / NGO reports about the country — extracted with a
   pattern-based named-entity rule (unverified: shown with an explicit "mentioned in news" label).

These are *candidates*, not endorsements: the UI always shows a due-diligence checklist.
"""
import re

import pandas as pd

from src.config import PROCESSED

ORG_RX = re.compile(
    r"\b((?:[A-Z][\w'’\-]+\s){0,5}"
    r"(?:Red Crescent|Red Cross|Foundation|Relief|Society|Association|Organi[sz]ation|"
    r"Initiative|Network|Committee|Aid|Charity|Hospital|Volunteers|Coalition|Center|Centre|Trust)"
    r"(?:\s(?:for|of)\s(?:[A-Z][\w'’\-]+\s?){1,4})?)")
STOP = re.compile(r"^(The|A|An|This|Our|Their|Its|His|Her|In|On|At|By|For|And|But|UN|United Nations|World|"
                  r"European|International Monetary|Security Council|General Assembly|Human Rights Council|"
                  r"National Security|Supreme Council|Revolutionary|Presidential|Military)\b")
EXCLUDE = re.compile(r"\b(News|Media|TV|Press|Agency|Times|Channel|Radio|Network|UN|UNRWA|UNICEF|UNHCR|WFP|WHO|OCHA|UNDP|FAO|IOM|Security Council|"
                     r"Ministry|Government|Army|Forces|Police|Parliament|Party|Bank|Fund|NATO|Council|Sovereignty|"
                     r"Transitional|Authority|Militia|Organization for Migration|Food Programme|Health Organization)\b")
GENERIC = {"red crescent", "red cross", "the red crescent", "the red cross"}


def societies() -> pd.DataFrame:
    p = PROCESSED / "ifrc_societies.parquet"
    return pd.read_parquet(p).set_index("iso3") if p.exists() else pd.DataFrame()


def news_orgs(news: pd.DataFrame, iso3: str, top: int = 8) -> list[dict]:
    if news.empty:
        return []
    d = news[(news["group"] == "independent") & news["iso3s"].map(lambda xs: iso3 in xs)]
    counts, where = {}, {}
    for _, r in d.iterrows():
        for m in ORG_RX.findall(r["title"] + ". " + r["text"]):
            name = m.strip(" .,'’")
            if (len(name.split()) < 2 or name.lower() in GENERIC or STOP.match(name)
                    or EXCLUDE.search(name)):
                continue
            counts[name] = counts.get(name, 0) + 1
            where.setdefault(name, r["url"])
    rows = sorted(counts.items(), key=lambda x: -x[1])[:top]
    return [{"name": n, "type": "Mentioned in independent news", "mentions": c,
             "evidence": "news mention — unverified", "url": where[n]} for n, c in rows]


def candidates(soc: pd.DataFrame, news: pd.DataFrame, iso3: str) -> list[dict]:
    out = []
    if iso3 in soc.index:
        s = soc.loc[iso3]
        out.append({"name": s["society"], "type": "Red Crescent / Red Cross National Society",
                    "website": s.get("website"), "url": s.get("directory"),
                    "evidence": "IFRC national societies directory (verified)"})
    for o in news_orgs(news, iso3):
        if out and re.search("Red Crescent|Red Cross", o["name"]):
            continue  # same national society, different spelling
        out.append(o)
    return out
