"""News feeds — independent & Global-South outlets, NGO/rights organisations, and (only to
measure the attention gap) Western mainstream media.

Country tagging is done with a gazetteer (country + crisis place names). Demonyms are used
only when no place name is found, so that "X strikes kill 20 in Gaza" is tagged with the place
where people are affected, not with the attacking state.
"""
import html
import re
import time
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

import requests

from src.config import USER_AGENT

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " + USER_AGENT}

# group: "independent" = counts as a source of evidence; "western" = attention comparison only
FEEDS = {
    "Al Jazeera": ("independent", "https://www.aljazeera.com/xml/rss/all.xml"),
    "Middle East Eye": ("independent", "https://www.middleeasteye.net/rss"),
    "Anadolu Agency": ("independent", "https://www.aa.com.tr/en/rss/default?cat=guncel"),
    "Yeni Şafak": ("independent", "https://www.yenisafak.com/en/rss"),
    "Daily Sabah": ("independent", "https://www.dailysabah.com/rss/world"),
    "The New Arab": ("independent", "https://www.newarab.com/rss"),
    "Middle East Monitor": ("independent", "https://www.middleeastmonitor.com/feed/"),
    "Mondoweiss": ("independent", "https://mondoweiss.net/feed/"),
    "Radio Dabanga": ("independent", "https://www.dabangasudan.org/en/feed"),
    "Ariana News": ("independent", "https://www.ariananews.af/feed/"),
    "Amu TV": ("independent", "https://amu.tv/feed/"),
    "Dawn": ("independent", "https://www.dawn.com/feeds/home"),
    "Africanews": ("independent", "https://www.africanews.com/feed/rss"),
    "MSF": ("independent", "https://www.msf.org/rss/all"),
    "Amnesty International": ("independent", "https://www.amnesty.org/en/feed/"),
    "BBC World": ("western", "https://feeds.bbci.co.uk/news/world/rss.xml"),
    "The Guardian": ("western", "https://www.theguardian.com/world/rss"),
    "New York Times": ("western", "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"),
    # Turkish-language media (what Turkish NGOs read), across the political spectrum; used for the
    # Turkish-vs-Western coverage comparison. Sector labels via the multilingual model.
    "TRT Haber": ("turkish", "https://www.trthaber.com/dunya_articles.rss"),
    "AA Türkçe": ("turkish", "https://www.aa.com.tr/tr/rss/default?cat=dunya"),
    "Hürriyet": ("turkish", "https://www.hurriyet.com.tr/rss/dunya"),
    "Yeni Şafak (TR)": ("turkish", "https://www.yenisafak.com/rss?xml=dunya"),
    "Sabah": ("turkish", "https://www.sabah.com.tr/rss/dunya.xml"),
    "Cumhuriyet": ("turkish", "https://www.cumhuriyet.com.tr/rss/son_dakika.xml"),
    "BirGün": ("turkish", "https://www.birgun.net/rss/home"),
    "bianet": ("turkish", "https://bianet.org/biamag.rss"),
}


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def _date(s):
    try:
        return parsedate_to_datetime(s).isoformat()
    except Exception:
        return s


def fetch_feed(name: str) -> list[dict]:
    group, url = FEEDS[name]
    r = requests.get(url, headers=H, timeout=60)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    items = []
    ns_atom = "{http://www.w3.org/2005/Atom}"
    for it in list(root.iter("item")) + list(root.iter(ns_atom + "entry")):
        title = it.findtext("title") or it.findtext(ns_atom + "title") or ""
        link = it.findtext("link") or ""
        if not link and it.find(ns_atom + "link") is not None:
            link = it.find(ns_atom + "link").get("href", "")
        desc = (it.findtext("description") or it.findtext(ns_atom + "summary")
                or it.findtext("{http://purl.org/rss/1.0/modules/content/}encoded") or "")
        date = it.findtext("pubDate") or it.findtext(ns_atom + "updated") or ""
        items.append({"source": name, "group": group, "id": link.strip() or title,
                      "title": _clean(title), "url": link.strip(), "date": _date(date),
                      "text": _clean(desc)[:1500]})
    return items


def fetch_all() -> list[dict]:
    out = []
    for name in FEEDS:
        try:
            out += fetch_feed(name)
        except Exception as e:
            print(f"  feed {name}: failed ({type(e).__name__})")
        time.sleep(0.5)
    return out


# ---------- gazetteer ----------
PLACES = {  # crisis places & regions -> ISO3 (extend freely)
    "PSE": ["gaza", "west bank", "rafah", "khan younis", "khan yunis", "jabalia", "jenin", "nablus",
            "tulkarem", "deir al-balah", "nuseirat", "hebron", "ramallah", "palestine", "palestinian territor"],
    "SDN": ["(?<!south )(?<!güney )sudan", "darfur", "el fasher", "al-fashir", "khartoum", "kordofan", "omdurman", "port sudan",
            "el obeid", "gezira", "zamzam", "tawila", "kadugli", "dilling"],
    "SSD": ["south sudan", "juba", "upper nile", "jonglei", "malakal"],
    "AFG": ["afghanistan", "kabul", "herat", "kandahar", "badakhshan", "balkh", "nangarhar"],
    "SYR": ["syria", "idlib", "aleppo", "damascus", "deir ez-zor", "deir el-zor", "homs", "latakia",
            "raqqa", "suwayda", "sweida"],
    "YEM": ["yemen", "sanaa", "sana'a", "aden", "hodeidah", "taiz", "marib"],
    "LBN": ["lebanon", "beirut", "south lebanon", "nabatieh", "tyre", "bekaa"],
    "COD": ["democratic republic of congo", "dr congo", "drc", "goma", "north kivu", "south kivu",
            "ituri", "bukavu", "kinshasa"],
    "SOM": ["somalia", "mogadishu", "puntland", "jubaland", "baidoa"],
    "ETH": ["ethiopia", "tigray", "amhara", "oromia", "addis ababa"],
    "MMR": ["myanmar", "rakhine", "arakan", "sagaing", "yangon", "burma"],
    "BGD": ["bangladesh", "cox's bazar", "dhaka"],
    "HTI": ["haiti", "port-au-prince"],
    "UKR": ["ukraine", "kharkiv", "kyiv", "odesa", "zaporizhzhia", "donetsk", "kherson", "sumy"],
    "IRQ": ["iraq", "baghdad", "mosul", "sinjar", "erbil"],
    "IRN": ["iran", "tehran"],
    "PAK": ["pakistan", "khyber pakhtunkhwa", "balochistan", "karachi", "lahore", "islamabad"],
    "IND": ["india", "kashmir", "manipur", "new delhi"],
    "MLI": ["(?-i:Mali)", "bamako", "timbuktu", "gao"],  # case-sensitive: Turkish "mali" = financial
    "BFA": ["burkina faso", "ouagadougou"],
    "NER": ["niger", "niamey"],
    "NGA": ["nigeria", "borno", "zamfara", "abuja", "lagos", "maiduguri"],
    "TCD": ["chad", "n'djamena", "adre"],
    "CAF": ["central african republic", "bangui"],
    "LBY": ["libya", "tripoli", "benghazi", "derna"],
    "MOZ": ["mozambique", "cabo delgado", "maputo"],
    "CMR": ["cameroon"], "KEN": ["kenya", "nairobi"], "UGA": ["uganda", "kampala"],
    "VEN": ["venezuela", "caracas"], "COL": ["colombia", "bogota", "catatumbo"],
    "CHN": ["xinjiang", "uyghur", "china", "beijing"],
    "ISR": ["israel", "tel aviv"], "TUR": ["turkey", "türkiye", "turkiye", "istanbul", "ankara",
                                           "hatay", "kahramanmaras", "gaziantep"],
    "EGY": ["egypt", "cairo", "sinai"], "JOR": ["jordan", "amman"], "TUN": ["tunisia"],
    "DZA": ["algeria"], "MAR": ["morocco"], "MRT": ["mauritania"], "SEN": ["senegal"],
    "ERI": ["eritrea"], "DJI": ["djibouti"], "RUS": ["russia", "moscow"], "AZE": ["azerbaijan"],
    "ARM": ["armenia"], "PHL": ["philippines", "mindanao"],
    "IDN": ["indonesia", "aceh", "sulawesi"], "MYS": ["malaysia"], "THA": ["thailand"],
    "NPL": ["nepal"], "LKA": ["sri lanka"], "MDG": ["madagascar"], "MWI": ["malawi"],
    "ZWE": ["zimbabwe"], "ZMB": ["zambia"], "AGO": ["angola"], "BDI": ["burundi"], "RWA": ["rwanda"],
    "TZA": ["tanzania"], "CUB": ["cuba"], "MEX": ["mexico"], "GTM": ["guatemala"],
    "HND": ["honduras"], "ECU": ["ecuador"], "PER": ["peru"], "BRA": ["brazil"],
    "UZB": ["uzbekistan"], "TJK": ["tajikistan"], "KGZ": ["kyrgyzstan"], "KAZ": ["kazakhstan"],
    "SAU": ["saudi arabia"], "QAT": ["qatar"], "ARE": ["united arab emirates", "uae"],
    "BIH": ["bosnia"], "XKX": ["kosovo"],
}
# Turkish exonyms (Turkish-language feeds); dotted capital İ is listed explicitly
TR_PLACES = {
    "PSE": ["filistin", "gazze", "batı şeria", "refah", "han yunus", "cenin", "nablus", "ramallah"],
    "SDN": ["darfur", "hartum", "faşir", "kordofan"], "SSD": ["güney sudan"],
    "AFG": ["afganistan", "kabil", "herat", "kandahar"], "SYR": ["suriye", "halep", "idlib", "İdlib", "şam", "humus"],
    "YEM": ["yemen", "sana", "hudeyde", "taiz"], "LBN": ["lübnan", "beyrut"], "COD": ["kongo"],
    "SOM": ["somali", "mogadişu"], "ETH": ["etiyopya", "tigray"], "MMR": ["myanmar", "arakan"],
    "BGD": ["bangladeş"], "HTI": ["haiti"], "UKR": ["ukrayna", "kiev", "harkiv", "odessa"],
    "IRQ": ["irak", "bağdat", "musul", "erbil"], "IRN": ["İran", "iran", "tahran"], "PAK": ["pakistan"],
    "IND": ["hindistan", "keşmir"], "NER": ["nijer"], "NGA": ["nijerya"], "TCD": ["çad"],
    "CAF": ["orta afrika"], "LBY": ["libya", "trablus", "bingazi"], "MOZ": ["mozambik"], "CMR": ["kamerun"],
    "COL": ["kolombiya"], "CHN": ["çin", "doğu türkistan", "uygur"], "ISR": ["İsrail", "israil", "tel aviv"],
    "EGY": ["mısır", "kahire"], "JOR": ["ürdün"], "RUS": ["rusya", "moskova"], "MDG": ["madagaskar"],
    "ZMB": ["zambiya"], "MWI": ["malavi"], "ZWE": ["zimbabve"], "RWA": ["ruanda"], "TZA": ["tanzanya"],
    "BDI": ["burundi"], "BFA": ["burkina faso"], "KEN": ["kenya"], "UGA": ["uganda"], "VEN": ["venezuela"],
    "AZE": ["azerbaycan"], "ARM": ["ermenistan"], "SAU": ["suudi arabistan"], "BIH": ["bosna"],
}
for _iso, _ws in TR_PLACES.items():
    PLACES.setdefault(_iso, []).extend(_ws)

DEMONYMS = {"PSE": ["palestinian"], "SDN": ["sudanese"], "AFG": ["afghan"], "SYR": ["syrian"],
            "YEM": ["yemeni"], "LBN": ["lebanese"], "SOM": ["somali"], "ETH": ["ethiopian"],
            "MMR": ["rohingya"], "HTI": ["haitian"], "UKR": ["ukrainian"], "IRQ": ["iraqi"],
            "COD": ["congolese"], "SSD": ["south sudanese"]}

def _rx(w):  # entries starting with "(?" are raw regex, the rest literal
    return w if w.startswith("(?") else re.escape(w)


_PL = [(iso, re.compile(r"\b(" + "|".join(map(_rx, ws)) + r")\b", re.I)) for iso, ws in PLACES.items()]
_DM = [(iso, re.compile(r"\b(" + "|".join(map(re.escape, ws)) + r")s?\b", re.I)) for iso, ws in DEMONYMS.items()]


def tag_countries(text: str) -> list[str]:
    found = [iso for iso, p in _PL if p.search(text)]
    if not found:
        found = [iso for iso, p in _DM if p.search(text)]
    if "PSE" in found and "ISR" in found:
        found.remove("ISR")  # report about Palestine: affected place is Palestine
    return found
