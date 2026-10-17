"""Knowledge base for sustainable, place-specific project ideas.

CROPS    — general agronomic climate envelopes (mean / coldest / warmest month temperature in °C,
           annual rainfall in mm, max elevation in m). These are coarse screening thresholds from general
           agronomy and MUST be confirmed with a local agronomist; the UI says so.
PROJECTS — sustainable intervention templates: when they fit (security, climate, sectors), what is
           procured, how the project sustains itself after the NGO leaves, typical risks.
"""

# name_tr, name_en, type, mean(lo,hi), coldest(lo,hi), warmest(lo,hi), rain(lo,hi), elev_max
CROPS = {
    "wheat":      ("Buğday", "Wheat", "field", (4, 20), (-18, 15), (15, 32), (250, 900), 3500),
    "barley":     ("Arpa", "Barley", "field", (2, 20), (-20, 15), (12, 32), (200, 800), 4000),
    "chickpea":   ("Nohut", "Chickpea", "field", (10, 25), (-5, 18), (20, 35), (250, 700), 2500),
    "lentil":     ("Mercimek", "Lentil", "field", (8, 22), (-8, 15), (18, 32), (250, 600), 2500),
    "potato":     ("Patates", "Potato", "vegetable", (5, 20), (-15, 15), (14, 26), (400, 1200), 4000),
    "tomato":     ("Domates", "Tomato", "vegetable", (14, 28), (2, 25), (22, 35), (400, 1200), 2000),
    "onion":      ("Soğan", "Onion", "vegetable", (10, 25), (-5, 20), (18, 32), (350, 900), 2500),
    "beans":      ("Fasulye", "Beans", "field", (15, 27), (5, 24), (20, 32), (400, 1500), 2500),
    "maize":      ("Mısır", "Maize", "field", (15, 30), (0, 26), (22, 35), (500, 1200), 2500),
    "sorghum":    ("Sorgum", "Sorghum", "field", (20, 32), (10, 28), (26, 40), (300, 900), 1500),
    "millet":     ("Darı", "Millet", "field", (22, 33), (12, 30), (27, 40), (200, 700), 1500),
    "cassava":    ("Manyok", "Cassava", "field", (21, 32), (16, 30), (24, 34), (800, 2500), 1500),
    "apricot":    ("Kayısı", "Apricot", "tree", (8, 20), (-15, 5), (20, 32), (300, 800), 2600),
    "almond":     ("Badem", "Almond", "tree", (12, 22), (-5, 9), (24, 35), (300, 700), 2000),
    "grape":      ("Üzüm", "Grape", "tree", (11, 22), (-10, 9), (20, 33), (300, 800), 2000),
    "pomegranate": ("Nar", "Pomegranate", "tree", (14, 26), (-5, 13), (25, 38), (250, 800), 1500),
    "olive":      ("Zeytin", "Olive", "tree", (14, 22), (0, 13), (22, 32), (300, 800), 1200),
    "date_palm":  ("Hurma", "Date palm", "tree", (21, 32), (8, 25), (30, 42), (0, 400), 800),
    "pistachio":  ("Antep fıstığı", "Pistachio", "tree", (12, 22), (-10, 7), (26, 36), (200, 600), 2000),
    "walnut":     ("Ceviz", "Walnut", "tree", (8, 18), (-15, 5), (18, 30), (500, 1200), 2500),
    "saffron":    ("Safran", "Saffron", "field", (8, 20), (-10, 5), (20, 32), (250, 500), 2500),
}


def suitable_crops(cl: dict | None) -> list[dict]:
    """Crops whose envelope fits the climate; 'irrigation' if rainfall is below the minimum."""
    if not cl:
        return []
    out = []
    for key, (tr, en, typ, mean, cold, warm, rain, elev) in CROPS.items():
        if not (mean[0] <= cl["temp_mean"] <= mean[1] and cold[0] <= cl["temp_coldest"] <= cold[1]
                and warm[0] <= cl["temp_warmest"] <= warm[1]):
            continue
        if cl.get("elevation") is not None and cl["elevation"] > elev:
            continue
        if cl["rain_mm"] > rain[1] * 1.5:
            continue
        out.append({"key": key, "tr": tr, "en": en, "type": typ, "irrigation": cl["rain_mm"] < rain[0]})
    return out


# key: (tr, en, sectors, security allowed, budget class, months, women focus,
#       items_tr, items_en, sustainability_tr, sustainability_en, risks_tr, risks_en)
PROJECTS = {
    "farm_coop": dict(
        tr="Tohum, alet ve damla sulama ile çiftçi kooperatifi", en="Farmers' cooperative with seeds, tools and drip irrigation",
        sectors={"agriculture", "food", "livelihoods"}, security={"low", "medium"}, budget="medium", months=18, women=False,
        items_tr=["sertifikalı / yerel çeşit tohum", "el aletleri setleri", "damla sulama kitleri", "kompost ve organik gübre", "ortak depo"],
        items_en=["certified / local-variety seed", "hand-tool kits", "drip-irrigation kits", "compost and organic fertiliser", "shared storage"],
        sust_tr="Tohum bankası: her aile hasadının %10'unu geri verir, bir sonraki yıl yeni ailelere dağıtılır; kooperatif ortak satış yapar.",
        sust_en="Seed bank: each family returns 10% of its harvest, which is given to new families next season; the cooperative sells jointly.",
        risks_tr=["kuraklık / su hakkı anlaşmazlığı", "yerel güç sahiplerinin kooperatifi ele geçirmesi"],
        risks_en=["drought / water-rights disputes", "capture of the cooperative by local power holders"]),
    "orchard": dict(
        tr="Meyve bahçesi kurulumu (aşılı fidan + sulama)", en="Orchard establishment (grafted saplings + irrigation)",
        sectors={"agriculture", "livelihoods", "food"}, security={"low"}, budget="medium", months=36, women=False,
        items_tr=["aşılı fidanlar", "damla sulama", "çit / koruma", "budama ve aşı eğitimi"],
        items_en=["grafted saplings", "drip irrigation", "fencing", "pruning and grafting training"],
        sust_tr="Ağaçlar 3–5 yılda verime girer ve 20+ yıl gelir sağlar; fidanlık kurularak yeni aileler beslenir.",
        sust_en="Trees bear fruit in 3–5 years and earn income for 20+ years; a community nursery supplies new families.",
        risks_tr=["ilk 3 yıl gelir yok — ara ürün gerekir", "don / su kıtlığı"],
        risks_en=["no income in the first 3 years — intercropping needed", "frost / water scarcity"]),
    "greenhouse": dict(
        tr="Küçük ölçekli aile seraları", en="Small family greenhouses",
        sectors={"agriculture", "food", "livelihoods", "nutrition"}, security={"low", "medium"}, budget="medium", months=12, women=True,
        items_tr=["sera iskeleti ve örtüsü", "fide / tohum", "damla sulama", "eğitim"],
        items_en=["greenhouse frame and cover", "seedlings / seed", "drip irrigation", "training"],
        sust_tr="Soğuk iklimde yıl boyu sebze; satış geliri örtü yenileme fonuna ayrılır.",
        sust_en="Year-round vegetables in a cold climate; part of sales income funds cover replacement.",
        risks_tr=["kar / rüzgâr hasarı", "pazara erişim"], risks_en=["snow / wind damage", "market access"]),
    "food_processing": dict(
        tr="Kadın kooperatifi: kurutma ve gıda işleme (kuru meyve, salça, reçel)", en="Women's cooperative: drying and food processing",
        sectors={"livelihoods", "food", "agriculture"}, security={"low", "medium"}, budget="small", months=12, women=True,
        items_tr=["güneş enerjili kurutucular", "hijyenik işleme ekipmanı", "ambalaj ve etiket", "gıda güvenliği eğitimi"],
        items_en=["solar dryers", "hygienic processing equipment", "packaging and labels", "food-safety training"],
        sust_tr="Hasat kaybını azaltır, ürünün değerini artırır; kooperatif kendi ham maddesini yerel çiftçilerden alır.",
        sust_en="Cuts post-harvest loss and adds value; the cooperative buys raw produce from local farmers.",
        risks_tr=["pazar bulamama", "kadınların hareket kısıtı"], risks_en=["no market", "restrictions on women's mobility"]),
    "tailoring": dict(
        tr="Kadın dikiş ve tekstil atölyesi", en="Women's tailoring and textile workshop",
        sectors={"livelihoods", "protection", "education"}, security={"low", "medium"}, budget="small", months=12, women=True,
        items_tr=["dikiş makineleri (elektriksiz yerlerde pedallı)", "overlok makinesi", "başlangıç kumaş stoku", "güneş paneli (gerekirse)", "eğitmen"],
        items_en=["sewing machines (treadle where there is no power)", "overlock machine", "starter fabric stock", "solar panel (if needed)", "trainer"],
        sust_tr="Mezunlar atölyeyi kooperatif olarak devralır; okul üniforması ve yerel siparişlerle gelir; makineler eğitim sonrası mezunlara verilir.",
        sust_en="Graduates take over the workshop as a cooperative; income from school uniforms and local orders; machines go to graduates.",
        risks_tr=["pazar doygunluğu", "kadınların çalışmasına yönelik kısıtlar"], risks_en=["market saturation", "restrictions on women's work"]),
    "livestock": dict(
        tr="Küçükbaş hayvan (keçi / koyun) ve veteriner desteği", en="Small livestock (goats / sheep) with veterinary support",
        sectors={"livelihoods", "food", "nutrition", "agriculture"}, security={"low", "medium"}, budget="medium", months=24, women=True,
        items_tr=["damızlık hayvan", "aşı ve ilaç", "yem (ilk kış)", "barınak malzemesi", "köy veteriner gönüllüsü eğitimi"],
        items_en=["breeding animals", "vaccines and drugs", "feed (first winter)", "shelter materials", "village animal-health worker training"],
        sust_tr="Devret sistemi: her aile ilk dişi yavruyu başka bir aileye verir; süt ve yünle gelir.",
        sust_en="Pass-on scheme: each family gives its first female offspring to another family; income from milk and wool.",
        risks_tr=["kuraklıkta mera yetersizliği", "hayvan hastalıkları"], risks_en=["pasture shortage in drought", "animal disease"]),
    "poultry": dict(
        tr="Aile ölçeğinde tavukçuluk", en="Family-scale poultry",
        sectors={"livelihoods", "nutrition", "food"}, security={"low", "medium"}, budget="small", months=12, women=True,
        items_tr=["civciv", "kümes malzemesi", "yem", "aşı"], items_en=["chicks", "coop materials", "feed", "vaccines"],
        sust_tr="Yumurta ile çocuk beslenmesi ve gelir; kuluçka ile sürü kendini yeniler.",
        sust_en="Eggs for child nutrition and income; brooding renews the flock.",
        risks_tr=["kuş gribi / hastalık", "yem fiyatları"], risks_en=["avian flu / disease", "feed prices"]),
    "beekeeping": dict(
        tr="Arıcılık", en="Beekeeping",
        sectors={"livelihoods", "agriculture"}, security={"low", "medium"}, budget="small", months=18, women=True,
        items_tr=["kovanlar", "arı kolonileri", "koruyucu ekipman", "bal süzme ekipmanı"],
        items_en=["hives", "bee colonies", "protective gear", "honey extractor"],
        sust_tr="Bal kooperatifi; kolonilerin bölünmesiyle kovan sayısı her yıl artar.",
        sust_en="Honey cooperative; splitting colonies grows the number of hives every year.",
        risks_tr=["tarım ilacı", "kuraklıkta çiçek azlığı"], risks_en=["pesticides", "few flowers in drought"]),
    "solar_water": dict(
        tr="Güneş enerjili su kuyusu ve pompa", en="Solar-powered well and pump",
        sectors={"wash", "health", "agriculture"}, security={"low", "medium"}, budget="large", months=6, women=False,
        items_tr=["sondaj", "güneş paneli ve pompa", "su deposu", "çeşmeler", "su kalitesi testi"],
        items_en=["borehole drilling", "solar panels and pump", "storage tank", "tap stands", "water-quality testing"],
        sust_tr="Köy su komitesi kurulur; hane başı küçük aidatla bakım fonu oluşur; teknisyen eğitimi.",
        sust_en="A village water committee; a small household fee builds a maintenance fund; a trained technician.",
        risks_tr=["yeraltı suyu tükenmesi", "su erişiminde ayrımcılık"], risks_en=["groundwater depletion", "unequal access"]),
    "vocational": dict(
        tr="Gençlere mesleki eğitim (güneş paneli kurulumu, elektrik, telefon tamiri)", en="Vocational training for youth (solar installation, electrics, phone repair)",
        sectors={"livelihoods", "education"}, security={"low", "medium"}, budget="medium", months=9, women=False,
        items_tr=["atölye ekipmanı", "mezunlara alet setleri", "eğitmen", "mikro hibe"],
        items_en=["workshop equipment", "tool kits for graduates", "trainers", "micro-grants"],
        sust_tr="Mezunlar alet seti ve küçük hibeyle kendi işini kurar; usta–çırak ağı.",
        sust_en="Graduates start their own business with a tool kit and a small grant; master–apprentice network.",
        risks_tr=["iş piyasasının darlığı", "göç"], risks_en=["narrow job market", "migration"]),
    "school": dict(
        tr="Okul onarımı ve öğretmen desteği", en="School repair and teacher support",
        sectors={"education", "protection"}, security={"low", "medium"}, budget="large", months=12, women=False,
        items_tr=["onarım malzemesi", "sıra ve tahta", "kitap ve kırtasiye", "öğretmen teşviki"],
        items_en=["repair materials", "desks and boards", "books and stationery", "teacher incentives"],
        sust_tr="Veli–okul komitesi bakım üstlenir; yerel yönetimle öğretmen maaşı planı.",
        sust_en="A parent–school committee takes over maintenance; plan with local authorities for teacher pay.",
        risks_tr=["kız çocuklarının eğitime erişim kısıtı", "okulun hedef alınması"], risks_en=["restrictions on girls' education", "attacks on schools"]),
    "clinic": dict(
        tr="Mobil klinik / sağlık evi (yerel ortak üzerinden)", en="Mobile clinic / health post (through a local partner)",
        sectors={"health", "nutrition", "protection"}, security={"low", "medium", "high"}, budget="large", months=12, women=False,
        items_tr=["ilaç ve tıbbi sarf", "araç / sağlık evi donanımı", "sağlık personeli", "sevk sistemi"],
        items_en=["medicines and supplies", "vehicle / health-post equipment", "health staff", "referral system"],
        sust_tr="Yerel sağlık personeli eğitilir; topluluk sağlık gönüllüleri ağı kurulur.",
        sust_en="Local health staff trained; a network of community health volunteers.",
        risks_tr=["personelin güvenliği", "ilaç tedarik zinciri"], risks_en=["staff safety", "medicine supply chain"]),
    "emergency_food": dict(
        tr="Acil gıda / nakit yardımı", en="Emergency food / cash assistance",
        sectors={"food", "nutrition", "livelihoods"}, security={"low", "medium", "high"}, budget="small", months=3, women=False,
        items_tr=["gıda kolisi ya da nakit / kupon", "dağıtım lojistiği", "şikâyet mekanizması"],
        items_en=["food parcels or cash / vouchers", "distribution logistics", "complaints mechanism"],
        sust_tr="Köprü yardım: koşullar el verince bir geçim projesine bağlanır.",
        sust_en="Bridge assistance: linked to a livelihood project as soon as conditions allow.",
        risks_tr=["yardımın ele geçirilmesi", "dağıtım noktalarında şiddet"], risks_en=["aid diversion", "violence at distribution points"]),
    "nutrition": dict(
        tr="Anne–çocuk beslenme programı (tarama + ek gıda)", en="Mother-and-child nutrition (screening + supplementary food)",
        sectors={"nutrition", "health", "food"}, security={"low", "medium", "high"}, budget="medium", months=12, women=True,
        items_tr=["kol çevresi ölçüm bantları", "ek besin", "anne eğitimi", "sevk"],
        items_en=["MUAC tapes", "supplementary food", "mothers' education", "referral"],
        sust_tr="Topluluk sağlık gönüllüleri taramayı sürdürür; ev bahçesi ile desteklenir.",
        sust_en="Community health volunteers continue screening; supported by home gardens.",
        risks_tr=["tedarik kesintisi"], risks_en=["supply interruption"]),
    "psychosocial": dict(
        tr="Çocuk dostu alan ve psikososyal destek", en="Child-friendly space and psychosocial support",
        sectors={"protection", "education", "health"}, security={"medium", "high"}, budget="small", months=12, women=False,
        items_tr=["güvenli alan", "oyun ve eğitim malzemesi", "eğitimli personel"],
        items_en=["safe space", "play and learning materials", "trained staff"],
        sust_tr="Yerel gönüllüler ve öğretmenler eğitilir; okullara entegre edilir.",
        sust_en="Local volunteers and teachers trained; integrated into schools.",
        risks_tr=["personel güvenliği"], risks_en=["staff safety"]),
    "winterization": dict(
        tr="Barınak onarımı ve kış hazırlığı", en="Shelter repair and winterisation",
        sectors={"shelter", "health"}, security={"low", "medium", "high"}, budget="medium", months=4, women=False,
        items_tr=["yalıtım ve çatı malzemesi", "soba ve yakıt", "battaniye ve kışlık giysi"],
        items_en=["insulation and roofing", "stoves and fuel", "blankets and winter clothes"],
        sust_tr="Yerel ustalar eğitilir; malzemeler yerel pazardan alınır (ekonomiye katkı).",
        sust_en="Local builders trained; materials bought locally (supports the economy).",
        risks_tr=["yakıt fiyatları"], risks_en=["fuel prices"]),
}

BUDGET_RANK = {"small": 0, "medium": 1, "large": 2}


def match(province: dict, ngo_sectors: set, ngo_budget: str, hunger: float | None) -> list[dict]:
    """Return feasible project ideas for one province, best first, with plain-language reasons."""
    cl, sec = province.get("climate"), province["security"]
    crops = suitable_crops(cl)
    trees = [c for c in crops if c["type"] == "tree"]
    field = [c for c in crops if c["type"] != "tree"]
    ideas = []
    for key, p in PROJECTS.items():
        if sec not in p["security"]:
            continue
        if BUDGET_RANK[p["budget"]] > BUDGET_RANK.get(ngo_budget, 1):
            continue
        fit, why = 0.0, []
        if key == "farm_coop":
            if not field:
                continue
            fit += 0.4
        if key == "orchard":
            if not trees:
                continue
            fit += 0.4
        if key == "food_processing":
            if not (trees or field):
                continue
            fit += 0.25
        if key == "greenhouse":
            if not cl or cl["temp_coldest"] > 5:
                continue
            fit += 0.35
        if key == "livestock" and cl and cl["rain_mm"] > 900:
            continue
        if key == "beekeeping" and (not cl or cl["rain_mm"] < 250 or not 6 <= cl["temp_mean"] <= 28):
            continue
        if key == "solar_water":
            if cl and cl["rain_mm"] < 400:
                fit += 0.3
        if key == "winterization":
            if not cl or cl["temp_coldest"] > 3:
                continue
            fit += 0.3
        if key in ("emergency_food", "clinic", "psychosocial") and sec == "high":
            fit += 0.4
        if key in ("emergency_food", "nutrition") and hunger and hunger >= 0.6:
            fit += 0.3
        overlap = p["sectors"] & ngo_sectors
        fit += 0.25 * len(overlap)
        if not overlap and ngo_sectors:
            fit -= 0.3
        ideas.append({"key": key, "fit": round(fit, 2), "sectors": sorted(p["sectors"]),
                      "crops": [c for c in (trees if key == "orchard" else field if key == "farm_coop" else
                                            crops if key == "food_processing" else [])][:6]})
    ideas.sort(key=lambda x: -x["fit"])
    return ideas  # all feasible ideas, best first (UI shows the top 3 and folds the rest)
