/* STK Asistanı — front-end */
const I18N = {
  tr: {
    tagline: "Bağımsız kaynaklarla kriz izleme ve kampanya önerisi",
    lensPriority: "Öncelik", lensSilence: "Sessizlik", lensTrend: "Kötüleşme",
    lensPriorityNote: "İhtiyaç, aciliyet, faaliyet alanlarınız ve ihtiyaç sahibi kişi başına düşen yardımın azlığına göre sıralanır.",
    lensSilenceNote: "Ana akım Batı medyasının haber yapmadığı ihtiyaç: ihtiyaç × (1 − Batı medyasında görünürlük).",
    lensTrendNote: "Son 3 ayda şiddeti önceki 12 aya göre artan krizler — erken müdahale fırsatı.",
    settings: "Ayarlar", tabRank: "Sıralama", tabNews: "Bağımsız haberler",
    layerEvents: "Afetler", layerIgnored: "Görmezden gelinen", layerGlobe: "Küre",
    legendPriority: "Öncelik skoru", legendSilence: "Sessizlik endeksi", legendTrend: "Kötüleşme skoru",
    ignoredShort: "Batı medyası görmüyor", exclShort: "Kapsam dışı",
    profileBased: "merkezli", edit: "Düzenle", noSectors: "alan seçilmedi",
    direct: "Doğrudan müdahale", partner: "Ortak üzerinden", ignored: "Batı medyası görmüyor",
    st_worsening: "Kötüleşiyor", st_easing_ongoing: "Azaldı ama sürüyor", st_chronic: "Kronik", st_improving: "İyileşiyor",
    excluded: "STK politikası gereği kapsam dışı", noneWorsening: "Şu an kötüleşen kriz yok.",
    updated: "Veri", score: "skor", rankOf: "sıra",
    makeCampaign: "Kampanya önerisi oluştur", close: "Kapat",
    tSummary: "Özet", tProjects: "Proje fikirleri", tData: "Veriler",
    projLoading: "İller analiz ediliyor (şiddet, iklim, rakım)… ilk açılış birkaç saniye sürebilir.",
    projIntro: "İller ihtiyaca göre sıralandı. Her il için güvenlik düzeyi, son yılın iklimi ve ona uygun sürdürülebilir proje türleri. Bir projeye tıklayın, sahadan bilginizi ekleyin, taslak oluşturun.",
    secLow: "Düşük risk", secMed: "Orta risk", secHigh: "Yüksek risk — acil yardım / ortak", deaths12: "12 ayda ölüm", newsShort: "haber",
    womenFocus: "kadın odaklı", moreIdeas: "diğer uygun proje (seçili alanlarınız dışında)", cropDisclaimer: "Ürün önerileri genel iklim eşiklerine dayanır; yerel ziraat uzmanı, su hakları ve pazar araştırmasıyla doğrulanmalıdır. İklim: Open-Meteo (ERA5), şiddet: UCDP.",
    projFormLead: "Taslak, ilin şiddet, iklim, rakım ve haber verisiyle ülkenin bağlamı kullanılarak yazılır. Sahadan bildiğiniz bir şey varsa ekleyin — taslak buna göre şekillenir.",
    fieldNote: "Sahadan not (isteğe bağlı)", fieldNotePh: "Örn: Köyde 40 dul kadın var, çoğu el işinde deneyimli; pazara 12 km; elektrik günde 4 saat.",
    genProject: "Proje taslağı oluştur", pWhyHere: "Neden burada?", pTarget: "Hedef grup", pProcure: "Satın alınacaklar",
    pTraining: "Eğitim", pSustain: "Sürdürülebilirlik", pExit: "Çıkış stratejisi", pTimeline: "Takvim", pBudget: "Bütçe dağılımı",
    pVerify: "Sahada doğrulanacaklar", tNews: "Haberler", tPartners: "Ortaklar",
    why: "Skor neden böyle?", trend: "Gidişat", trendSub: "Son 24 ay, aylık ölüm · koyu: son 3 ay",
    trendText: "Son 3 ay ortalaması ayda {r}; önceki 12 ayın medyanı ayda {b} (×{x}). Son 12 ayda ağır şiddet görülen ay sayısı: {h}.",
    ghiTrend: "Açlık Endeksi 2018 → 2026", sectorNeed: "Alanlara göre ihtiyaç", yearly: "Yıllara göre çatışma ölümleri",
    ifrc: "Kızılay / Kızılhaç acil çağrıları", events: "Doğal afet uyarıları", indicators: "Göstergeler",
    cAcuteD: "Doğal afet (× kırılganlık)", cAcuteW: "Son dönem şiddet / can kaybı", cCiv: "Sivillere yönelik şiddet",
    cProt: "Süregelen mağduriyet", cSector: "Faaliyet alanınızdaki ihtiyaç", cNeglect: "Fonlama açığı (IFRC)",
    cEsc: "Kötüleşme", cAid: "Kişi başı yardım açığı",
    kAidPP: "Ağır ihtiyaç sahibi kişi başına insani yardım (yıllık)", kAidSrc: "OECD, 2023–2024 ortalaması",
    kAidNA: "yalnızca tanınmış krizlerde hesaplanır", kNeed: "Ağır ihtiyaç sahibi nüfus (tahmini)",
    kNeedSrc: "nüfus × süregelen mağduriyetin 0,3 üstündeki kısmı", kAid: "İnsani yardım (yıllık, tüm bağışçılar)", cIndep: "Bağımsız medyada görünürlük", cWest: "Batı medyasında görünürlük", cSilence: "Sessizlik endeksi",
    kDeaths: "Çatışma ölümleri, 3 yıl", kPer100k: "Her 100 bin kişide ölüm", kCivil: "Sivil ölümler, 3 yıl",
    kGhi: "Küresel Açlık Endeksi 2026", kVuln: "Kırılganlık (açlık / şiddet)", kIfrc: "IFRC çağrılarının fonlanan kısmı",
    kNews: "Haber, 30 gün: bağımsız / Batı", provisional: "geçici kategori", distance: "Uzaklık",
    gaza: "Filistin — kayıtlı kayıplar", gKilled: "Gazze'de öldürülen", gChildren: "Çocuk", gWomen: "Kadın",
    gFamine: "Açlıktan ölüm", gAid: "Yardım beklerken öldürülen", gInjured: "Yaralı", gLast30: "Son 30 gün",
    wbKilled: "Batı Şeria'da öldürülen", wbSettler: "Yerleşimci saldırısı", wbDisplaced: "Batı Şeria'da yerinden edilen",
    ofWhich: "{n} çocuk dahil",
    gazaNote: "Kayıtlı ölümlerdir; enkaz altındakiler, hastalık ve tıbbi bakım yokluğundan ölenler dahil değildir — gerçek kayıp daha yüksektir. Bakanlık sivil/savaşan ayrımı yayımlamaz; çocuk ve kadın sayısı yalnızca yayımlanan dökümdür, diğer ölenlerin savaşan olduğu anlamına gelmez.",
    accessNote: "Doğrudan müdahale öncesi insani erişim, sınır geçişi ve izinleri kontrol edin; erişim kısıtlıysa ortak üzerinden çalışın.",
    partners: "Olası yerel ortaklar", verified: "IFRC dizininde doğrulandı", unverified: "Haberde geçiyor — doğrulanmadı",
    noPartners: "Bu ülke için ulusal Kızılay/Kızılhaç ya da haberlerde geçen kuruluş bulunamadı.",
    ddTitle: "Ortaklık öncesi durum tespiti",
    dd: ["Kayıt ve yasal statü belgeleri", "Son 2 yılın denetlenmiş mali tabloları", "Yaptırım / terör listesi taraması",
         "Çocuk koruma ve istismar önleme politikaları", "Birlikte çalıştığı STK'lardan ve yerel topluluktan referans"],
    newsNote: "Sektör etiketleri yapay zekâ modelince atanır. Yanlışsa düzeltin; model bir sonraki eğitimde öğrenir.",
    fixLabel: "etiketi düzelt", save: "Kaydet", thanks: "Teşekkürler — model bir sonraki eğitimde bunu öğrenecek.",
    western: "Batı medyası", noData: "Veri yok",
    ovTitle: "Bugünün tablosu", ovLead: "Haritadan ya da listeden bir ülke seçerek dosyasını açın.",
    ovWorse: "Kötüleşen", ovIgnored: "Batı medyasının görmediği", ovTop: "En yüksek öncelik",
    ovSources: "Kaynaklar: UCDP (Uppsala Üniv.), Küresel Açlık Endeksi, IFRC, Gazze Sağlık Bakanlığı (Tech for Palestine), USGS, NASA ve 15 bağımsız haber kaynağı. BM verisi kullanılmaz.",
    sProfile: "STK profili", sName: "STK adı", sHome: "Merkez ülke", sSectors: "Faaliyet alanları",
    sTeams: "Sahada ekibi olan ülkeler", sExcl: "Faaliyet dışı ülkeler", sExclHelp: "Bu ülkeler skor almaz ve gri görünür.",
    sAdd: "Ülke ekle…", sBudget: "Bütçe ölçeği", small: "Küçük (< 50 bin $)", medium: "Orta (50–500 bin $)", large: "Büyük (> 500 bin $)",
    sRadius: "Doğrudan müdahale yarıçapı", sWeights: "Önceliklendirme ağırlıkları",
    wAcute: "Güncel afet / acil", wProt: "Süregelen mağduriyet", wSector: "Alanımdaki ihtiyaç", wTrend: "Kötüleşen kriz bonusu",
    wAid: "Kişi başı yardım açığı", wNeglect: "Fonlama açığı (IFRC)", wForgot: "Görmezden gelinen kriz bonusu", sReset: "Varsayılana dön",
    sModel: "Model ve veri", refresh: "Canlı veriyi yenile", refreshing: "Yenileniyor…",
    llmOn: "Kampanya metni: {m}", llmOff: "Kampanya metni: şablon (LLM anahtarı yok)",
    modelInfo: "Sektör modeli: TF-IDF + lojistik regresyon, micro-F1 {f} (anahtar kelime yöntemi {b}). Can kaybı modeli macro-F1 {p}.",
    generating: "Kampanya önerisi hazırlanıyor…", serverNeeded: "Kampanya üretimi için sunucu gerekiyor: python app.py",
    campWhy: "Neden şimdi?", campWhere: "Nerede ve nasıl", campTargets: "Hedef gruplar", campActs: "Faaliyetler",
    campPartners: "Önerilen ortaklar", campDonor: "Bağışçı mesajı", campPosts: "Sosyal medya", campRisks: "Riskler ve zarar vermeme",
    campKpis: "Başarı göstergeleri", campSources: "Kaynaklar", engine: "Üretici", copy: "Metni kopyala", copied: "Kopyalandı ✓",
    km: "km",
  },
  en: {
    tagline: "Crisis monitoring and campaign recommendations from independent sources",
    lensPriority: "Priority", lensSilence: "Silence", lensTrend: "Worsening",
    lensPriorityNote: "Ranked by need, urgency, your sectors and how little aid reaches each person in need.",
    lensSilenceNote: "Need left unreported by Western mainstream media: need × (1 − Western visibility).",
    lensTrendNote: "Crises whose violence rose in the last 3 months vs the previous 12 — a chance to act early.",
    settings: "Settings", tabRank: "Ranking", tabNews: "Independent news",
    layerEvents: "Disasters", layerIgnored: "Ignored", layerGlobe: "Globe",
    legendPriority: "Priority score", legendSilence: "Silence index", legendTrend: "Worsening score",
    ignoredShort: "Ignored by Western media", exclShort: "Out of scope",
    profileBased: "based", edit: "Edit", noSectors: "no sectors selected",
    direct: "Direct response", partner: "Via partner", ignored: "Ignored by Western media",
    st_worsening: "Worsening", st_easing_ongoing: "Easing but ongoing", st_chronic: "Chronic", st_improving: "Improving",
    excluded: "Out of scope by NGO policy", noneWorsening: "No worsening crisis right now.",
    updated: "Data", score: "score", rankOf: "rank",
    makeCampaign: "Generate campaign recommendation", close: "Close",
    tSummary: "Summary", tProjects: "Project ideas", tData: "Data",
    projLoading: "Analysing provinces (violence, climate, elevation)… the first time can take a few seconds.",
    projIntro: "Provinces ranked by need. For each: security level, last year's climate and sustainable project types that fit. Click a project, add what you know from the field and draft it.",
    secLow: "Low risk", secMed: "Medium risk", secHigh: "High risk — emergency / partner", deaths12: "deaths in 12 months", newsShort: "news",
    womenFocus: "women-focused", moreIdeas: "other feasible projects (outside your selected sectors)", cropDisclaimer: "Crop suggestions come from general climate envelopes; confirm with a local agronomist, water rights and market research. Climate: Open-Meteo (ERA5); violence: UCDP.",
    projFormLead: "The draft uses the province's violence, climate, elevation and news data plus the country context. If you know something from the field, add it — the draft will follow it.",
    fieldNote: "Field note (optional)", fieldNotePh: "E.g. 40 widows in the village, most experienced in handicrafts; market 12 km away; power 4 hours a day.",
    genProject: "Draft project proposal", pWhyHere: "Why here?", pTarget: "Target group", pProcure: "Procurement",
    pTraining: "Training", pSustain: "Sustainability", pExit: "Exit strategy", pTimeline: "Timeline", pBudget: "Budget split",
    pVerify: "To verify on site", tNews: "News", tPartners: "Partners",
    why: "Why this score?", trend: "Trajectory", trendSub: "Last 24 months, deaths per month · dark: last 3 months",
    trendText: "Last 3 months average {r}/month; median of the previous 12 months {b}/month (×{x}). Heavy violence in {h} of the last 12 months.",
    ghiTrend: "Global Hunger Index 2018 → 2026", sectorNeed: "Need by sector", yearly: "Conflict deaths per year",
    ifrc: "Red Crescent / Red Cross appeals", events: "Natural-hazard alerts", indicators: "Indicators",
    cAcuteD: "Natural hazard (× vulnerability)", cAcuteW: "Recent violence / casualties", cCiv: "Violence against civilians",
    cProt: "Protracted suffering", cSector: "Need in your sectors", cNeglect: "Funding gap (IFRC)",
    cEsc: "Worsening", cAid: "Aid gap per person",
    kAidPP: "Humanitarian aid per person in severe need (yearly)", kAidSrc: "OECD, 2023–2024 average",
    kAidNA: "computed for recognised crises only", kNeed: "People in severe need (estimate)",
    kNeedSrc: "population × protracted suffering above 0.3", kAid: "Humanitarian aid (yearly, all donors)", cIndep: "Visibility in independent media", cWest: "Visibility in Western media", cSilence: "Silence index",
    kDeaths: "Conflict deaths, 3 years", kPer100k: "Deaths per 100k people", kCivil: "Civilian deaths, 3 years",
    kGhi: "Global Hunger Index 2026", kVuln: "Vulnerability (hunger / violence)", kIfrc: "IFRC appeals funded",
    kNews: "News, 30 days: independent / Western", provisional: "provisional category", distance: "Distance",
    gaza: "Palestine — registered casualties", gKilled: "Killed in Gaza", gChildren: "Children", gWomen: "Women",
    gFamine: "Starvation deaths", gAid: "Killed while seeking aid", gInjured: "Injured", gLast30: "Last 30 days",
    wbKilled: "Killed in the West Bank", wbSettler: "Settler attacks", wbDisplaced: "Displaced in the West Bank",
    ofWhich: "of which {n} children",
    gazaNote: "Registered deaths; people under rubble and deaths from disease and lack of care are not included — the true toll is higher. The Ministry publishes no civilian/combatant split; children and women are the only published breakdown, which does not imply the others were combatants.",
    accessNote: "Before a direct response, check humanitarian access, border crossings and permits; if access is restricted, work through a partner.",
    partners: "Possible local partners", verified: "Verified in IFRC directory", unverified: "Mentioned in news — unverified",
    noPartners: "No national Red Crescent/Red Cross society or news-mentioned organisation found.",
    ddTitle: "Due diligence before partnering",
    dd: ["Registration and legal status documents", "Audited financial statements (last 2 years)", "Sanctions / terrorism list screening",
         "Child safeguarding and abuse-prevention policies", "References from peer NGOs and the local community"],
    newsNote: "Sector tags are assigned by the AI model. If one is wrong, fix it; the model learns at the next training run.",
    fixLabel: "fix label", save: "Save", thanks: "Thanks — the model will learn this at the next training run.",
    western: "Western media", noData: "No data",
    ovTitle: "Today's picture", ovLead: "Pick a country on the map or in the list to open its file.",
    ovWorse: "Worsening", ovIgnored: "Ignored by Western media", ovTop: "Highest priority",
    ovSources: "Sources: UCDP (Uppsala Univ.), Global Hunger Index, IFRC, Gaza Ministry of Health (Tech for Palestine), USGS, NASA and 15 independent news outlets. No UN data.",
    sProfile: "NGO profile", sName: "NGO name", sHome: "Home country", sSectors: "Areas of work",
    sTeams: "Countries with field teams", sExcl: "Excluded countries", sExclHelp: "These countries get no score and are shown grey.",
    sAdd: "Add a country…", sBudget: "Budget size", small: "Small (< $50k)", medium: "Medium ($50k–500k)", large: "Large (> $500k)",
    sRadius: "Direct response radius", sWeights: "Prioritisation weights",
    wAcute: "Current disaster / acute", wProt: "Protracted suffering", wSector: "Need in my sectors", wTrend: "Worsening crisis bonus",
    wAid: "Aid gap per person", wNeglect: "Funding gap (IFRC)", wForgot: "Ignored crisis bonus", sReset: "Reset to defaults",
    sModel: "Model and data", refresh: "Refresh live data", refreshing: "Refreshing…",
    llmOn: "Campaign text: {m}", llmOff: "Campaign text: template (no LLM key)",
    modelInfo: "Sector model: TF-IDF + logistic regression, micro-F1 {f} (keyword baseline {b}). Casualty model macro-F1 {p}.",
    generating: "Drafting the campaign recommendation…", serverNeeded: "Campaign generation needs the server: python app.py",
    campWhy: "Why now?", campWhere: "Where and how", campTargets: "Target groups", campActs: "Activities",
    campPartners: "Suggested partners", campDonor: "Donor message", campPosts: "Social media", campRisks: "Risks and do-no-harm",
    campKpis: "Success indicators", campSources: "Sources", engine: "Engine", copy: "Copy text", copied: "Copied ✓",
    km: "km",
  },
};

const DEFAULT_W = { acute: 6, prot: 6, sector: 7, aid: 5, trend: 5, neglect: 3, forgot: 3 };
const store = {
  get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} },
};
const S = {
  lang: store.get("lang2", "tr"), theme: store.get("theme", "light"), lens: store.get("lens2", "priority"),
  sideTab: "rank", tab: "summary", data: null, byIso: {}, selected: null, scores: {}, rankPos: {},
  map: null, globe: false, llm: null,
  sectors: new Set(store.get("sectors2", ["food", "health", "shelter"])),
  w: { ...DEFAULT_W, ...store.get("weights", {}) },
  profile: { name: "Örnek Derneği", home: "TUR", budget: "medium", radius: 2500, teams: [], excluded: ["ISR"],
             ...store.get("profile", {}) },
};
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const t = (k) => I18N[S.lang][k] ?? k;
const loc = () => (S.lang === "tr" ? "tr-TR" : "en-GB");
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const n1 = (v) => (v == null ? "—" : (+v).toLocaleString(loc(), { maximumFractionDigits: 1 }));
const n0 = (v) => (v == null || Number.isNaN(+v) ? "—" : Math.round(+v).toLocaleString(loc()));
function compact(v) {
  if (v == null || Number.isNaN(+v)) return "—";
  return new Intl.NumberFormat(loc(), { notation: "compact", maximumFractionDigits: 1 }).format(v);
}
const cname = (c) => (S.lang === "tr" && c.name_tr) || c.name;
const secName = (k) => S.data.sectors[k][S.lang];
const saveProfile = () => store.set("profile", S.profile);

function haversine(a, b) {
  const R = 6371, r = Math.PI / 180;
  const dLat = (b.lat - a.lat) * r, dLon = (b.lon - a.lon) * r;
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(a.lat * r) * Math.cos(b.lat * r) * Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(h));
}

/* ======================= scoring (transparent, user-weighted) ======================= */
function computeScores() {
  const w = S.w, home = S.byIso[S.profile.home], teams = new Set(S.profile.teams), excl = new Set(S.profile.excluded);
  S.scores = {};
  for (const c of S.data.countries) {
    const sc = c.score, prot = sc.protracted;
    if (excl.has(c.iso3)) { S.scores[c.iso3] = { s: 0, excluded: true }; continue; }
    if (prot === null && !sc.acute) continue; // no evidence at all -> unscored
    let sectorNeed = null;
    for (const k of S.sectors) {
      const v = sc.sector[k];
      if (v != null) sectorNeed = Math.max(sectorNeed ?? 0, v);
    }
    if (sectorNeed === null) sectorNeed = (prot ?? 0) * 0.5;
    const parts = [[sc.acute, w.acute], [prot ?? 0, w.prot], [sectorNeed, w.sector],
      [sc.aid_gap ?? 0, w.aid],         // aid per person in severe need (0 outside recognised crises)
      [sc.neglect ?? 0.5, w.neglect]];  // unknown funding gap = neutral, never a penalty
    const wsum = parts.reduce((a, [, x]) => a + x, 0) || 1;
    let s = parts.reduce((a, [v, x]) => a + v * x, 0) / wsum;
    // bonuses only add — a crisis that is not worsening (or not ignored) is never pulled down
    s += (sc.escalation || 0) * 0.2 * (w.trend / 10);   // worsening: recent 3 months vs previous 12
    if (c.forgotten) s += 0.15 * (w.forgot / 10);
    if (S.lens === "silence") s = c.silence == null ? 0 : c.silence * (0.7 + 0.3 * sectorNeed);
    if (S.lens === "trend") s = (sc.escalation || 0) * (0.4 + 0.6 * Math.max(prot ?? 0, sectorNeed));
    const dist = home ? haversine(home, c) : null;
    const direct = c.iso3 === home?.iso3 || teams.has(c.iso3) || (dist !== null && dist <= S.profile.radius);
    S.scores[c.iso3] = { s: Math.round(Math.min(1, s) * 100), sectorNeed, dist: dist && Math.round(dist), direct };
  }
  const order = Object.entries(S.scores).filter(([, x]) => !x.excluded && (S.lens !== "trend" || x.s > 0))
    .sort((a, b) => b[1].s - a[1].s);
  S.rankPos = Object.fromEntries(order.map(([iso], i) => [iso, i + 1]));
  S.order = order;
}

/* ======================= map ======================= */
const MAP_STYLE = {
  light: "https://basemaps.cartocdn.com/gl/positron-nolabels-gl-style/style.json",
  dark: "https://basemaps.cartocdn.com/gl/dark-matter-nolabels-gl-style/style.json",
};
const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();

function initMap() {
  S.map = new maplibregl.Map({ container: "map", style: MAP_STYLE[S.theme], center: [32, 18], zoom: 1.7, minZoom: 1,
    attributionControl: { compact: true } });
  S.map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
  S.map.on("style.load", addLayers);
  bindMapEvents();
}

function addLayers() {
  const m = S.map;
  if (m.getSource("countries")) return;
  m.addSource("countries", { type: "geojson", data: "data/countries.geojson", promoteId: "iso3" });
  m.addLayer({ id: "c-fill", type: "fill", source: "countries", paint: {
    "fill-color": ["case",
      ["boolean", ["feature-state", "excluded"], false], css("--line-2"),
      ["==", ["feature-state", "score"], null], css("--bg"),
      ["interpolate", ["linear"], ["feature-state", "score"],
        0, css("--r0"), 25, css("--r1"), 50, css("--r2"), 75, css("--r3"), 100, css("--r4")]],
    "fill-opacity": ["case", ["boolean", ["feature-state", "hover"], false], 1, 0.92] } });
  m.addLayer({ id: "c-line", type: "line", source: "countries",
    paint: { "line-color": css("--surface"), "line-width": 0.7 } });
  m.addLayer({ id: "c-ignored", type: "line", source: "countries", filter: ["in", ["get", "iso3"], ["literal", []]],
    paint: { "line-color": css("--accent"), "line-width": 1.6, "line-dasharray": [2, 1.4] } });
  m.addLayer({ id: "c-sel", type: "line", source: "countries", filter: ["==", ["get", "iso3"], ""],
    paint: { "line-color": css("--ink"), "line-width": 2.2 } });
  m.addSource("hot", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
  m.addLayer({ id: "hot", type: "circle", source: "hot", paint: {
    "circle-color": css("--accent"), "circle-opacity": 0.12, "circle-stroke-color": css("--accent"),
    "circle-stroke-width": 1.2, "circle-radius": ["interpolate", ["linear"], ["get", "s"], 60, 5, 100, 13] } });
  m.addSource("events", { type: "geojson", data: eventsGeo() });
  m.addLayer({ id: "ev", type: "circle", source: "events", paint: {
    "circle-color": ["match", ["get", "alert"], "Red", css("--worse"), css("--easing")],
    "circle-radius": ["interpolate", ["linear"], ["zoom"], 1, 4, 6, 8],
    "circle-stroke-color": css("--raised"), "circle-stroke-width": 1.5 } });
  paintMap();
  const h = location.hash.slice(1).toUpperCase();
  if (S.byIso[h] && !S.selected) select(h, true);
}

function bindMapEvents() {
  const m = S.map;
  let hovered = null;
  const popup = new maplibregl.Popup({ closeButton: false, closeOnClick: false, offset: 10 });
  m.on("mousemove", "c-fill", (e) => {
    const iso = e.features[0].properties.iso3;
    if (hovered !== iso) {
      if (hovered) m.setFeatureState({ source: "countries", id: hovered }, { hover: false });
      hovered = iso;
      m.setFeatureState({ source: "countries", id: iso }, { hover: true });
    }
    m.getCanvas().style.cursor = "pointer";
    const c = S.byIso[iso], sc = S.scores[iso];
    if (!c) return popup.remove();
    popup.setLngLat(e.lngLat).setHTML(`<div class="pop"><b>${esc(cname(c))}</b>
      ${sc && !sc.excluded ? `<div class="row"><span>${t("score")}</span><span>${sc.s}${S.rankPos[iso] ? ` · #${S.rankPos[iso]}` : ""}</span></div>` : ""}
      ${sc?.excluded ? `<div class="row"><span>${t("excluded")}</span></div>` : ""}
      ${statusEl(c) ? `<div class="row">${statusEl(c)}</div>` : ""}</div>`).addTo(m);
  });
  m.on("mouseleave", "c-fill", () => {
    if (hovered) m.setFeatureState({ source: "countries", id: hovered }, { hover: false });
    hovered = null; popup.remove(); m.getCanvas().style.cursor = "";
  });
  m.on("click", "c-fill", (e) => select(e.features[0].properties.iso3));
  m.on("click", "hot", (e) => select(e.features[0].properties.iso3, true));
  m.on("click", "ev", (e) => {
    const p = e.features[0].properties;
    new maplibregl.Popup({ offset: 10 }).setLngLat(e.lngLat).setHTML(`<div class="pop"><b>${esc(p.title)}</b>
      <div class="row"><span>${esc(p.source)} · ${esc(p.alert)}</span><span>${esc((p.date || "").slice(0, 10))}</span></div>
      ${p.url ? `<a href="${esc(p.url)}" target="_blank" rel="noopener">↗</a>` : ""}</div>`).addTo(m);
  });
  for (const id of ["hot", "ev"]) {
    m.on("mouseenter", id, () => (m.getCanvas().style.cursor = "pointer"));
    m.on("mouseleave", id, () => (m.getCanvas().style.cursor = ""));
  }
}

function eventsGeo() {
  return { type: "FeatureCollection", features: S.data.events.filter((e) => e.lat != null)
    .map((e) => ({ type: "Feature", geometry: { type: "Point", coordinates: [e.lon, e.lat] },
      properties: { title: e.title, alert: e.alert, source: e.source, date: e.date, url: e.url } })) };
}

function paintMap() {
  const m = S.map;
  if (!m?.getSource("countries")) return;
  for (const c of S.data.countries) {
    const sc = S.scores[c.iso3];
    m.setFeatureState({ source: "countries", id: c.iso3 },
      { score: sc && !sc.excluded ? sc.s : null, excluded: !!sc?.excluded });
  }
  m.getSource("hot")?.setData({ type: "FeatureCollection", features: Object.entries(S.scores)
    .filter(([, sc]) => sc.s >= 60 && !sc.excluded).map(([iso, sc]) => ({ type: "Feature",
      geometry: { type: "Point", coordinates: [S.byIso[iso].lon, S.byIso[iso].lat] }, properties: { iso3: iso, s: sc.s } })) });
  const ign = $("#tIgnored").checked ? S.data.countries.filter((c) => c.forgotten).map((c) => c.iso3) : [];
  m.setFilter("c-ignored", ["in", ["get", "iso3"], ["literal", ign]]);
  m.setLayoutProperty("ev", "visibility", $("#tEvents").checked ? "visible" : "none");
  m.setFilter("c-sel", ["==", ["get", "iso3"], S.selected || ""]);
}

/* ======================= side panel ======================= */
const SHOWN_STATUS = new Set(["worsening", "chronic", "improving"]);  // "easing but ongoing" is not labelled
function statusEl(c) {
  const st = c.trend?.status;
  return SHOWN_STATUS.has(st) ? `<span class="status st-${st}">${t("st_" + st)}</span>` : "";
}

function renderProfileLine() {
  const home = S.byIso[S.profile.home];
  $("#profileLine").innerHTML = `<b>${esc(S.profile.name)}</b><span>· ${esc(home ? cname(home) : "—")} ${t("profileBased")}</span>
    <button id="editProfile">${t("edit")}</button>`;
  $("#editProfile").onclick = openDrawer;
  $("#sectorRow").innerHTML = Object.keys(S.data.sectors).map((k) =>
    `<button class="chip ${S.sectors.has(k) ? "on" : ""}" data-k="${k}" aria-pressed="${S.sectors.has(k)}">${esc(secName(k))}</button>`).join("");
  $$("#sectorRow .chip").forEach((b) => (b.onclick = () => {
    S.sectors.has(b.dataset.k) ? S.sectors.delete(b.dataset.k) : S.sectors.add(b.dataset.k);
    store.set("sectors2", [...S.sectors]);
    renderProfileLine(); refreshAll();
  }));
}

function renderRanking() {
  $("#lensNote").textContent = t({ silence: "lensSilenceNote", trend: "lensTrendNote" }[S.lens] || "lensPriorityNote");
  const rows = S.order.slice(0, 30);
  $("#rank").innerHTML = rows.length ? rows.map(([iso, sc], i) => {
    const c = S.byIso[iso];
    return `<li data-iso="${iso}" class="${S.selected === iso ? "sel" : ""}">
      <span class="pos num">${i + 1}</span>
      <div style="min-width:0"><div class="nm">${esc(cname(c))}</div>
        <div class="sub">${statusEl(c)}${c.forgotten ? `<span class="flag ignored">${t("ignored")}</span>` : ""}</div></div>
      <span class="score num">${sc.s}</span>
      <div class="meter"><i style="width:${sc.s}%"></i></div></li>`;
  }).join("") : `<li class="empty">${t("noneWorsening")}</li>`;
  $$("#rank li[data-iso]").forEach((li) => (li.onclick = () => select(li.dataset.iso, true)));
}

function renderNewsfeed() {
  $("#newsfeed").innerHTML = S.data.news.slice(0, 60).map((n) => `<li>
    <a href="${esc(n.url)}" target="_blank" rel="noopener">${esc(n.title)}</a>
    <div class="meta"><span>${esc(n.publisher)}</span><span>${esc(n.date.slice(0, 10))}</span>
      ${n.iso3s.filter((i) => S.byIso[i]).map((i) => `<button data-iso="${i}">${esc(cname(S.byIso[i]))}</button>`).join("")}</div></li>`).join("");
  $$("#newsfeed button[data-iso]").forEach((b) => (b.onclick = () => select(b.dataset.iso, true)));
}

/* ======================= dossier ======================= */
function bar(label, v, hi) {
  const unk = v == null;
  const pct = unk ? 0 : Math.round(v * 100);
  return `<div class="bar ${hi ? "hi" : ""} ${unk ? "unk" : ""}"><span class="lbl">${label}</span>
    <span class="val num">${unk ? "—" : pct}</span><div class="trk"><i style="width:${pct}%"></i></div></div>`;
}
function barChart(entries, highlightLast = 0) {
  if (!entries.length) return `<p class="note">${t("noData")}</p>`;
  const W = 360, H = 84, max = Math.max(...entries.map(([, v]) => v), 1), bw = W / entries.length;
  const ink = css("--ink-2"), acc = css("--accent");
  return `<div class="chart"><svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" role="img">
    ${entries.map(([k, v], i) => { const h = Math.max(1, (v / max) * (H - 2));
      return `<rect x="${i * bw + 1}" y="${H - h}" width="${Math.max(1, bw - 2)}" height="${h}" rx="1.5"
        fill="${i >= entries.length - highlightLast ? acc : ink}" opacity="${i >= entries.length - highlightLast ? 1 : 0.35}"><title>${k}: ${n0(v)}</title></rect>`; }).join("")}
  </svg><div class="axis"><span>${entries[0][0]}</span><span>max ${compact(max)}</span><span>${entries[entries.length - 1][0]}</span></div></div>`;
}
function stat(v, l) { return `<div class="stat"><div class="v num">${v}</div><div class="l">${l}</div></div>`; }

function renderOverview() {
  const ov = $("#overview");
  if (S.selected) { ov.hidden = true; return; }
  ov.hidden = false;
  const worse = S.data.countries.filter((c) => c.trend?.status === "worsening" && !S.profile.excluded.includes(c.iso3))
    .sort((a, b) => b.trend.ratio - a.trend.ratio);
  const ign = S.data.countries.filter((c) => c.forgotten);
  const top = S.order.slice(0, 5);
  const li = (c, right) => `<li data-iso="${c.iso3}"><span class="nm">${esc(cname(c))}</span><span class="muted num">${right}</span></li>`;
  ov.innerHTML = `<div class="ov">
    <div><h1>${t("ovTitle")}</h1><p class="lead">${t("ovLead")}</p></div>
    <div class="stats">${stat(worse.length, t("ovWorse"))}${stat(ign.length, t("ovIgnored"))}${stat(S.data.news.length, t("tabNews"))}</div>
    <div class="sec"><h3>${t("ovTop")}</h3><ul class="list ov-list">${top.map(([iso, sc]) => li(S.byIso[iso], sc.s)).join("")}</ul></div>
    ${worse.length ? `<div class="sec"><h3>${t("ovWorse")}</h3><ul class="list ov-list">${worse.map((c) =>
      li(c, `×${c.trend.ratio}`)).join("")}</ul></div>` : ""}
    <p class="note">${t("ovSources")}</p></div>`;
  $$(".ov-list li", ov).forEach((x) => (x.onclick = () => select(x.dataset.iso, true)));
}

function renderDetail() {
  const iso = S.selected, box = $("#detail");
  if (!iso) { box.hidden = true; $("#dossier").classList.remove("open"); renderOverview(); return; }
  const c = S.byIso[iso], sc = S.scores[iso] || {}, ind = c.ind;
  box.hidden = false; $("#overview").hidden = true; $("#dossier").classList.add("open");
  const pos = S.rankPos[iso];
  const tabs = [["summary", "tSummary"], ["projects", "tProjects"], ["data", "tData"], ["news", "tNews"], ["partners", "tPartners"]];
  box.innerHTML = `<div class="d-head">
      <div class="d-title"><h1>${esc(cname(c))}</h1>
        <div class="d-score">${sc.excluded ? "" : `<div class="v num">${sc.s ?? "—"}</div><div class="l">${t("score")}${pos ? ` · ${t("rankOf")} ${pos}` : ""}</div>`}</div></div>
      <div class="d-sub">${statusEl(c)}${c.forgotten ? `<span class="flag ignored">${t("ignored")}</span>` : ""}
        ${sc.excluded ? `<span class="flag">${t("excluded")}</span>` : `<span>${t(sc.direct ? "direct" : "partner")}</span>`}
        ${sc.dist != null ? `<span class="muted">${t("distance")} ${n0(sc.dist)} ${t("km")}</span>` : ""}</div>
      <div class="d-actions"><button class="btn primary" id="campBtn" ${sc.excluded ? "disabled" : ""}>${t("makeCampaign")}</button>
        <button class="btn ghost" id="closeDetail" aria-label="${t("close")}">✕</button></div>
      <div class="d-tabs tabs" style="padding:0;border:0">${tabs.map(([k, l]) =>
        `<button class="tab ${S.tab === k ? "on" : ""}" data-tab="${k}">${t(l)}</button>`).join("")}</div>
    </div><div class="d-body">${{ summary: tabSummary, projects: tabProjects, data: tabData, news: tabNews, partners: tabPartners }[S.tab](c, sc, ind)}</div>`;
  $("#campBtn").onclick = () => generateCampaign(iso);
  $("#closeDetail").onclick = () => { showProvinces(null); S.selected = null; history.replaceState(null, "", location.pathname); refreshAll(); };
  $$(".d-tabs .tab", box).forEach((b) => (b.onclick = () => { S.tab = b.dataset.tab; renderDetail(); }));
  $$(".fix", box).forEach((a) => (a.onclick = () => editLabels(c, +a.dataset.i)));
  if (S.tab === "projects") loadProjects(c); else showProvinces(null);
}

function tabSummary(c, sc, ind) {
  const g = c.gaza, tr = c.trend || {};
  const months = Object.entries(tr.monthly || {});
  const notes = Object.values(c.known_gaps || {}).map((x) => esc(x[S.lang]));
  return `
  ${sc.direct && !sc.excluded ? `<div class="callout info">${t("accessNote")}</div>` : ""}
  ${g ? `<div class="sec"><h3>${t("gaza")}</h3><div class="stats">
      ${stat(n0(g.killed_total), t("gKilled"))}${stat(n0(g.children_killed), t("gChildren"))}${stat(n0(g.women_killed), t("gWomen"))}
      ${stat(n0(g.famine_deaths), t("gFamine") + (g.child_famine_deaths != null ? `<br>${t("ofWhich").replace("{n}", n0(g.child_famine_deaths))}` : ""))}
      ${stat(n0(g.aid_seekers_killed), t("gAid"))}${stat(n0(g.killed_30d), t("gLast30"))}
      ${g.wb_killed != null ? stat(n0(g.wb_killed), t("wbKilled") + `<br>${t("ofWhich").replace("{n}", n0(g.wb_children_killed))}`) : ""}
      ${g.wb_settler_attacks != null ? stat(n0(g.wb_settler_attacks), t("wbSettler")) : ""}
      ${g.wb_displaced != null ? stat(n0(g.wb_displaced), t("wbDisplaced")) : ""}
    </div><p class="note">${t("gazaNote")} · Tech for Palestine, ${esc(g.last_update)}</p></div>` : ""}
  <div class="stats">
    ${stat(compact(ind.ucdp_deaths_3y), t("kDeaths"))}
    ${stat(n0(ind.civilian_per100k_3y), t("kPer100k").replace("ölüm", "sivil ölüm").replace("Deaths", "Civilian deaths"))}
    ${stat(ind.ghi_2026 != null ? (ind.ghi_provisional ? "≈" : "") + n1(ind.ghi_2026) : "—", t("kGhi"))}
  </div>
  <div class="sec"><h3>${t("trend")}</h3><p class="note" style="margin:-6px 0 8px">${t("trendSub")}</p>
    ${barChart(months, 3)}
    ${tr.recent_monthly != null ? `<p class="note">${t("trendText").replace("{r}", n0(tr.recent_monthly)).replace("{b}", n0(tr.base_monthly))
      .replace("{x}", tr.ratio).replace("{h}", tr.heavy_months_12)}${tr.ghi_2018 != null && tr.ghi_2026 != null ? `<br>${t("ghiTrend")}: ${n1(tr.ghi_2018)} → ${n1(tr.ghi_2026)}` : ""}</p>` : ""}
  </div>
  <div class="sec"><h3>${t("why")}</h3><div class="bars">
    ${bar(t("cCiv"), c.score.civilian_harm, true)}${bar(t("cProt"), c.score.protracted, true)}
    ${bar(t("cAcuteW"), c.score.acute_conflict)}${bar(t("cAcuteD"), c.score.acute_disaster)}
    ${bar(t("cEsc"), c.score.escalation)}${bar(t("cSector"), sc.sectorNeed)}${bar(t("cAid"), c.score.aid_gap, true)}${bar(t("cNeglect"), c.score.neglect)}
    ${bar(t("cIndep"), c.score.att_indep)}${bar(t("cWest"), c.score.att_western)}${bar(t("cSilence"), c.silence)}
  </div></div>
  ${notes.length ? `<div class="callout">${notes.join("<br>")}</div>` : ""}`;
}

/* ---------- place-specific project ideas ---------- */
S.regions = {};
function tabProjects() { return `<div id="projBox"><div class="loading"><span class="spinner"></span>${t("projLoading")}</div></div>`; }

async function loadProjects(c) {
  const key = `${c.iso3}|${[...S.sectors].sort().join(",")}|${S.profile.budget}|${S.lang}`;
  if (!S.regions[key]) {
    try {
      const q = new URLSearchParams({ sectors: [...S.sectors].join(","), budget: S.profile.budget, lang: S.lang });
      const r = await fetch(`api/regions/${c.iso3}?${q}`);
      if (!r.ok) throw new Error(r.status);
      S.regions[key] = await r.json();
    } catch { if ($("#projBox")) $("#projBox").innerHTML = `<p class="note">${t("serverNeeded")}</p>`; return; }
  }
  const data = S.regions[key];
  if (S.selected !== c.iso3 || S.tab !== "projects" || !$("#projBox")) return;
  showProvinces(data);
  const provs = data.provinces.filter((p) => p.ideas.length);
  const secLbl = { low: t("secLow"), medium: t("secMed"), high: t("secHigh") };
  $("#projBox").innerHTML = `<p class="note" style="margin-top:0">${t("projIntro")}</p>
    <div class="legend-keys" style="margin:8px 0 4px">${["low", "medium", "high"].map((k) =>
      `<span><i class="sec-dot sec-${k}"></i>${secLbl[k]}</span>`).join("")}</div>
    <ul class="list prov-list">${provs.slice(0, 15).map((p) => {
      const cl = p.climate;
      return `<li class="prov" data-id="${esc(p.id)}">
        <div class="prov-head"><b>${esc((S.lang === "tr" && p.name_tr) || p.name)}</b>
          <span class="sec-pill sec-${p.security}">${secLbl[p.security]}</span></div>
        <div class="meta">${cl ? `<span>${n0(cl.rain_mm)} mm</span><span>${n1(cl.temp_mean)}°C</span><span>${n0(cl.elevation)} m</span>` : ""}
          ${p.violence.deaths_12m ? `<span>${t("deaths12")}: ${n0(p.violence.deaths_12m)}</span>` : ""}
          ${p.news.length ? `<span>${p.news.length} ${t("newsShort")}</span>` : ""}</div>
        <div class="ideas">${p.ideas.slice(0, 3).map(ideaBtn(p)).join("")}</div>
        ${p.ideas.length > 3 ? `<details class="more"><summary>+ ${p.ideas.length - 3} ${t("moreIdeas")}</summary>
          <div class="ideas">${p.ideas.slice(3).map(ideaBtn(p)).join("")}</div></details>` : ""}</li>`; }).join("")}</ul>
    <p class="note">${t("cropDisclaimer")}</p>`;
  $$(".idea", $("#projBox")).forEach((b) => (b.onclick = () => openProject(c, data, b.dataset.prov, b.dataset.key)));
  $$(".prov", $("#projBox")).forEach((li) => (li.onmouseenter = () => highlightProvince(li.dataset.id)));
}

const ideaBtn = (p) => (i) => `<button class="idea" data-prov="${esc(p.id)}" data-key="${i.key}">
  <span>${esc(i.name)}</span>${i.crops?.length ? `<small>${esc(i.crops.slice(0, 5).join(", "))}</small>` : ""}
  ${i.women ? `<small class="women">${t("womenFocus")}</small>` : ""}</button>`;

function showProvinces(data) {
  const m = S.map;
  if (!m?.getLayer("c-fill")) return;   // base layers not ready yet
  if (!m.getSource("prov")) {
    m.addSource("prov", { type: "geojson", data: { type: "FeatureCollection", features: [] }, promoteId: "id" });
    m.addLayer({ id: "prov-fill", type: "fill", source: "prov", paint: {
      "fill-color": ["match", ["get", "sec"], "high", css("--worse"), "medium", css("--easing"), css("--better")],
      "fill-opacity": ["case", ["boolean", ["feature-state", "hl"], false], 0.7, 0.4] } });
    m.addLayer({ id: "prov-line", type: "line", source: "prov", paint: { "line-color": css("--ink"), "line-width": 1, "line-opacity": 0.7 } });
    const pp = new maplibregl.Popup({ closeButton: false, closeOnClick: false, offset: 6 });
    m.on("mousemove", "prov-fill", (e) => {
      const f = e.features[0].properties, pr = (S.provData?.provinces || []).find((x) => x.id === f.id);
      pp.setLngLat(e.lngLat).setHTML(`<div class="pop"><b>${esc((S.lang === "tr" && pr?.name_tr) || f.name)}</b>
        ${pr ? `<div class="row"><span>${t({ low: "secLow", medium: "secMed", high: "secHigh" }[pr.security])}</span></div>` : ""}</div>`).addTo(m);
    });
    m.on("mouseleave", "prov-fill", () => pp.remove());
    m.on("click", "prov-fill", (e) => {
      const id = e.features[0].properties.id, li = $(`.prov[data-id="${CSS.escape(id)}"]`);
      if (li) { li.scrollIntoView({ block: "center", behavior: "smooth" }); highlightProvince(id); }
    });
  }
  S.provData = data;
  if (!data) { m.getSource("prov").setData({ type: "FeatureCollection", features: [] }); return; }
  const sec = Object.fromEntries(data.provinces.map((p) => [p.id, p.security]));
  m.getSource("prov").setData({ type: "FeatureCollection", features: data.geometry.features.map((f) =>
    ({ ...f, properties: { ...f.properties, sec: sec[f.properties.id] || "low" } })) });
  // zoom to the provinces so they are actually visible
  let w = 180, so = 90, e = -180, n = -90;
  for (const f of data.geometry.features) for (const poly of f.geometry.coordinates) for (const ring of poly)
    for (const [x, y] of ring) { w = Math.min(w, x); e = Math.max(e, x); so = Math.min(so, y); n = Math.max(n, y); }
  if (w < e) m.fitBounds([[w, so], [e, n]], { padding: 40, duration: 900, maxZoom: 7 });
}
function highlightProvince(id) {
  if (!S.map?.getSource("prov")) return;
  if (S.hlProv) S.map.setFeatureState({ source: "prov", id: S.hlProv }, { hl: false });
  S.hlProv = id; S.map.setFeatureState({ source: "prov", id }, { hl: true });
  $$(".prov").forEach((x) => x.classList.toggle("on", x.dataset.id === id));
}

function openProject(c, data, provId, key) {
  const p = data.provinces.find((x) => x.id === provId), idea = p.ideas.find((i) => i.key === key);
  $("#campaignModal").hidden = false;
  $("#campaignBody").innerHTML = `<div class="camp">
    <div class="kicker"><span>${esc(cname(c))}</span><span>${esc((S.lang === "tr" && p.name_tr) || p.name)}</span></div>
    <h1>${esc(idea.name)}</h1>
    <p class="lead">${t("projFormLead")}</p>
    <label class="field" style="margin-top:14px"><span>${t("fieldNote")}</span>
      <textarea id="fieldNote" rows="4" placeholder="${t("fieldNotePh")}"></textarea></label>
    <div class="camp-foot"><span class="note" style="margin:0">${S.llm ? t("llmOn").replace("{m}", esc(S.llm)) : t("llmOff")}</span>
      <button class="btn primary" style="flex:0" id="genProject">${t("genProject")}</button></div></div>`;
  $("#genProject").onclick = () => generateProject(c, p, idea, $("#fieldNote").value);
}

async function generateProject(c, p, idea, note) {
  $("#campaignBody").innerHTML = `<div class="loading"><span class="spinner"></span>${t("generating")}</div>`;
  let res;
  try {
    const r = await fetch("api/project", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({
      iso3: c.iso3, province: p.id, project: idea.key, sectors: [...S.sectors], lang: S.lang, field_note: note,
      ngo: { name: S.profile.name, home: S.byIso[S.profile.home]?.name, budget: S.profile.budget } }) });
    if (!r.ok) throw new Error(r.status);
    res = await r.json();
  } catch { $("#campaignBody").innerHTML = `<p>${t("serverNeeded")}</p>`; return; }
  const k = res.project, L = (x) => (Array.isArray(x) ? x : x ? [x] : []);
  const li = (arr, f = (x) => esc(typeof x === "string" ? x : JSON.stringify(x))) => L(arr).length ? `<ul>${L(arr).map((x) => `<li>${f(x)}</li>`).join("")}</ul>` : "";
  const sec = (title, html) => (html && html !== "<p></p>" ? `<h3>${title}</h3>${html}` : "");
  $("#campaignBody").innerHTML = `<div class="camp" id="campText">
    <div class="kicker"><span>${esc(cname(c))}</span><span>${esc((S.lang === "tr" && p.name_tr) || p.name)}</span></div>
    <h1>${esc(k.title)}</h1>${k.problem ? `<p class="lead">${esc(k.problem)}</p>` : ""}
    ${sec(t("pWhyHere"), li(k.why_here))}
    ${sec(t("pTarget"), k.target_group?.who ? `<p>${esc(k.target_group.who)}${k.target_group.households_estimate_note ? ` — ${esc(k.target_group.households_estimate_note)}` : ""}</p>` : "")}
    ${sec(t("campActs"), li(k.activities, (a) => `${a.phase ? `<b>${esc(a.phase)}</b> · ` : ""}<b>${esc(a.name)}</b>${a.description ? " — " + esc(a.description) : ""}`))}
    ${sec(t("pProcure"), li(k.procurement, (x) => `<b>${esc(x.item)}</b>${x.purpose ? " — " + esc(x.purpose) : ""}`))}
    ${sec(t("pTraining"), li(k.training))}
    ${sec(t("pSustain"), k.sustainability ? `<p>${esc(k.sustainability)}</p>` : "")}
    ${sec(t("pExit"), k.exit_strategy ? `<p>${esc(k.exit_strategy)}</p>` : "")}
    ${sec(t("campPartners"), k.partner ? `<p>${esc(k.partner)}</p>` : "")}
    ${sec(t("pTimeline"), li(k.timeline, (x) => `<b>${esc(x.month)}</b> — ${esc(x.milestone)}`))}
    ${sec(t("pBudget"), li(k.budget_split, (x) => `${esc(x.line)}: <b>%${esc(x.percent)}</b>`))}
    ${sec(t("campKpis"), li(k.kpis))}
    ${sec(t("campRisks"), li(k.risks, (x) => `<b>${esc(x.risk ?? x)}</b>${x.mitigation ? " — " + esc(x.mitigation) : ""}`))}
    ${sec(t("pVerify"), li(k.verify_on_site))}
    ${sec(t("campDonor"), k.donor_message ? `<p>${esc(k.donor_message)}</p>` : "")}
    ${sec(t("campSources"), li(k.sources, (u) => `<a href="${esc(u)}" target="_blank" rel="noopener">${esc(u)}</a>`))}
  </div>
  ${res.warnings.map((w) => `<div class="callout" style="margin-top:12px">${esc(w)}</div>`).join("")}
  <div class="camp-foot"><span class="note" style="margin:0">${t("engine")}: ${esc(res.engine)}</span>
    <button class="btn ghost" id="copyBtn">${t("copy")}</button></div>`;
  $("#copyBtn").onclick = async () => { try { await navigator.clipboard.writeText($("#campText").innerText); $("#copyBtn").textContent = t("copied"); } catch {} };
}

function tabData(c, sc, ind) {
  const secs = Object.entries(c.score.sector).filter(([, v]) => v != null).sort((a, b) => b[1] - a[1]);
  const years = Object.entries(c.conflict_history || {}).sort((a, b) => a[0] - b[0]);
  const row = (l, v, src) => `<tr><td>${l}${src ? `<span class="src">${src}</span>` : ""}</td><td class="num">${v}</td></tr>`;
  return `
  <div class="sec"><h3>${t("indicators")}</h3><table class="kv">
    ${row(t("kDeaths"), n0(ind.ucdp_deaths_3y), esc(ind.deaths_source || "UCDP"))}
    ${row(t("kPer100k"), n0(ind.deaths_per100k_3y))}
    ${row(t("kCivil"), `${n0(ind.ucdp_civilian_3y)} <span class="muted">(${n0(ind.civilian_per100k_3y)}/100k)</span>`)}
    ${row(t("kGhi"), n1(ind.ghi_2026), ind.ghi_provisional ? t("provisional") : "Concern / Welthungerhilfe")}
    ${row(t("kVuln"), ind.vulnerability != null ? Math.round(ind.vulnerability * 100) : "—")}
    ${row(t("kAidPP"), ind.aid_per_person != null ? `$${n0(ind.aid_per_person)}` : "—", ind.aid_per_person != null ? t("kAidSrc") : t("kAidNA"))}
    ${row(t("kNeed"), ind.need_people != null ? compact(ind.need_people) : "—", t("kNeedSrc"))}
    ${row(t("kAid"), ind.aid_usd ? `$${compact(ind.aid_usd)}` : "—", "OECD DAC2A · 2023–2024")}
    ${row(t("kIfrc"), ind.ifrc_funded_pct != null ? `%${Math.round(ind.ifrc_funded_pct)}` : "—", ind.ifrc_requested ? `${compact(ind.ifrc_requested)} CHF` : "")}
    ${row(t("kNews"), `${ind.news_independent ?? 0} / ${ind.news_western ?? 0}`)}
  </table></div>
  <div class="sec"><h3>${t("sectorNeed")}</h3><div class="bars">
    ${secs.map(([k, v]) => bar(esc(secName(k)), v, S.sectors.has(k))).join("") || `<p class="note">${t("noData")}</p>`}</div></div>
  <div class="sec"><h3>${t("yearly")}</h3>${barChart(years)}</div>
  ${c.ifrc_appeals?.length ? `<div class="sec"><h3>${t("ifrc")}</h3><ul class="list">${c.ifrc_appeals.map((a) =>
    `<li>${esc(a.name)}<div class="meta"><span>${esc(a.type)}</span><span>${esc(a.start)}</span><span>${compact(a.requested)} CHF</span>
      <span>%${a.requested ? Math.round((a.funded / a.requested) * 100) : "—"}</span></div></li>`).join("")}</ul></div>` : ""}
  ${(() => { const ev = S.data.events.filter((e) => e.iso3 === c.iso3); return ev.length ? `<div class="sec"><h3>${t("events")}</h3><ul class="list">${ev.map((e) =>
    `<li><a href="${esc(e.url)}" target="_blank" rel="noopener">${esc(e.title)}</a><div class="meta"><span>${esc(e.source)}</span><span>${esc(e.alert)}</span><span>${esc((e.date || "").slice(0, 10))}</span></div></li>`).join("")}</ul></div>` : ""; })()}`;
}

function tabNews(c) {
  return `<p class="note" style="margin-top:0">${t("newsNote")}</p><ul class="list">${(c.news || []).map((n, i) => `<li>
    <a href="${esc(n.url)}" target="_blank" rel="noopener">${esc(n.title)}</a>
    <div class="meta"><span>${esc(n.publisher)}</span><span>${esc(n.date)}</span>${n.group === "western" ? `<span class="tagx">${t("western")}</span>` : ""}</div>
    <div class="meta" data-news="${i}">${n.sectors.map((s) => `<span class="tagx on">${esc(secName(s))}</span>`).join("")}
      <button class="linkbtn fix" data-i="${i}">${t("fixLabel")}</button></div></li>`).join("") || `<li class="muted">${t("noData")}</li>`}</ul>`;
}

function tabPartners(c) {
  return `<div class="sec"><h3>${t("partners")}</h3>${c.partners?.length ? `<ul class="list">${c.partners.map((p) => `<li class="partner">
    <b>${p.url ? `<a href="${esc(p.url)}" target="_blank" rel="noopener">${esc(p.name)}</a>` : esc(p.name)}</b>
    <div class="meta">${/verified\)/.test(p.evidence || "") ? `<span class="verified">✓ ${t("verified")}</span>` : `<span class="unverified">${t("unverified")}</span>`}
      ${p.mentions ? `<span>${p.mentions}×</span>` : ""}${p.website ? `<a href="${esc(p.website)}" target="_blank" rel="noopener">web ↗</a>` : ""}</div></li>`).join("")}</ul>`
    : `<p class="note">${t("noPartners")}</p>`}</div>
  <div class="sec"><h3>${t("ddTitle")}</h3><ul class="checklist">${t("dd").map((x) => `<li>${esc(x)}</li>`).join("")}</ul></div>`;
}

function editLabels(c, i) {
  const n = c.news[i], box = $(`[data-news="${i}"]`), cur = new Set(n.sectors);
  box.innerHTML = Object.keys(S.data.sectors).map((k) =>
    `<span class="tagx edit ${cur.has(k) ? "on" : ""}" data-k="${k}">${esc(secName(k))}</span>`).join("") +
    `<button class="linkbtn">${t("save")}</button>`;
  $$(".tagx", box).forEach((x) => (x.onclick = () => x.classList.toggle("on")));
  $("button", box).onclick = async () => {
    const labels = $$(".tagx.on", box).map((x) => x.dataset.k);
    try {
      await fetch("api/feedback", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: n.title, labels }) });
      n.sectors = labels;
      box.innerHTML = `<span class="muted">${t("thanks")}</span>`;
    } catch { box.innerHTML = `<span class="muted">${t("serverNeeded")}</span>`; }
  };
}

function select(iso, fly) {
  if (!S.byIso[iso]) return;
  if (S.selected !== iso) S.tab = "summary";
  S.selected = iso;
  history.replaceState(null, "", "#" + iso);
  renderDetail(); renderRanking(); paintMap();
  $("#detail").scrollTop = 0; $("#dossier").scrollTop = 0;
  if (fly && S.map) { const c = S.byIso[iso]; S.map.flyTo({ center: [c.lon, c.lat], zoom: Math.max(S.map.getZoom(), 3.2), speed: 0.9 }); }
}

/* ======================= settings drawer ======================= */
function openDrawer() {
  renderSettings();
  $("#drawer").classList.add("open"); $("#drawer").setAttribute("aria-hidden", "false"); $("#drawerBackdrop").hidden = false;
}
function closeDrawer() {
  $("#drawer").classList.remove("open"); $("#drawer").setAttribute("aria-hidden", "true"); $("#drawerBackdrop").hidden = true;
}
function countryTags(key) {
  return `<div class="tags">${S.profile[key].map((iso) => S.byIso[iso] ? `<span class="tagx">${esc(cname(S.byIso[iso]))}
    <button data-rm="${key}" data-iso="${iso}" aria-label="remove">×</button></span>` : "").join("")}</div>
    <input type="text" list="countryList" data-add="${key}" placeholder="${t("sAdd")}">`;
}
function renderSettings() {
  const opts = [...S.data.countries].sort((a, b) => cname(a).localeCompare(cname(b), loc()));
  const m = S.data.model;
  const slider = (k) => `<label class="slider"><span class="lbl">${t("w" + k[0].toUpperCase() + k.slice(1))}</span><b class="num">${S.w[k]}</b>
    <input type="range" min="0" max="10" value="${S.w[k]}" data-w="${k}"></label>`;
  $("#settingsBody").innerHTML = `
    <datalist id="countryList">${opts.map((c) => `<option value="${esc(cname(c))}">`).join("")}</datalist>
    <div class="group-title">${t("sProfile")}</div>
    <label class="field"><span>${t("sName")}</span><input type="text" id="fName" value="${esc(S.profile.name)}"></label>
    <label class="field"><span>${t("sHome")}</span><select id="fHome">${opts.map((c) =>
      `<option value="${c.iso3}" ${c.iso3 === S.profile.home ? "selected" : ""}>${esc(cname(c))}</option>`).join("")}</select></label>
    <div class="field"><span>${t("sSectors")}</span><div class="tags">${Object.keys(S.data.sectors).map((k) =>
      `<button class="chip ${S.sectors.has(k) ? "on" : ""}" data-sec="${k}">${esc(secName(k))}</button>`).join("")}</div></div>
    <div class="field"><span>${t("sTeams")}</span>${countryTags("teams")}</div>
    <div class="field"><span>${t("sExcl")}</span><small>${t("sExclHelp")}</small>${countryTags("excluded")}</div>
    <label class="field"><span>${t("sBudget")}</span><select id="fBudget">${["small", "medium", "large"].map((b) =>
      `<option value="${b}" ${S.profile.budget === b ? "selected" : ""}>${t(b)}</option>`).join("")}</select></label>
    <label class="slider"><span class="lbl">${t("sRadius")}</span><b class="num" id="radiusVal">${n0(S.profile.radius)} km</b>
      <input type="range" min="500" max="6000" step="250" value="${S.profile.radius}" id="fRadius"></label>
    <div class="group-title">${t("sWeights")}</div>
    ${["acute", "prot", "sector", "aid", "trend", "neglect", "forgot"].map(slider).join("")}
    <button class="btn ghost" id="resetW">${t("sReset")}</button>
    <div class="meta-box"><div class="group-title" style="margin:0 0 6px">${t("sModel")}</div>
      ${t("modelInfo").replace("{f}", m.micro_f1.toFixed(2)).replace("{b}", m.baseline_micro_f1.toFixed(2)).replace("{p}", m.pillar_macro_f1.toFixed(2))}<br>
      ${S.llm ? t("llmOn").replace("{m}", esc(S.llm)) : t("llmOff")}<br>
      ${t("updated")}: ${esc(S.data.generated_at.replace("T", " "))} UTC
      <div style="margin-top:10px"><button class="btn ghost" id="refreshBtn">${t("refresh")}</button></div></div>`;
  const body = $("#settingsBody");
  $("#fName").oninput = (e) => { S.profile.name = e.target.value; saveProfile(); renderProfileLine(); };
  $("#fHome").onchange = (e) => { S.profile.home = e.target.value; saveProfile(); renderProfileLine(); refreshAll(); };
  $("#fBudget").onchange = (e) => { S.profile.budget = e.target.value; saveProfile(); };
  $("#fRadius").oninput = (e) => { S.profile.radius = +e.target.value; $("#radiusVal").textContent = `${n0(S.profile.radius)} km`; saveProfile(); refreshAll(); };
  $$("[data-sec]", body).forEach((b) => (b.onclick = () => {
    S.sectors.has(b.dataset.sec) ? S.sectors.delete(b.dataset.sec) : S.sectors.add(b.dataset.sec);
    store.set("sectors2", [...S.sectors]); b.classList.toggle("on"); renderProfileLine(); refreshAll();
  }));
  $$("[data-w]", body).forEach((r) => (r.oninput = () => {
    S.w[r.dataset.w] = +r.value; r.previousElementSibling.textContent = r.value; store.set("weights", S.w); refreshAll();
  }));
  $("#resetW").onclick = () => { S.w = { ...DEFAULT_W }; store.set("weights", S.w); renderSettings(); refreshAll(); };
  $$("[data-rm]", body).forEach((b) => (b.onclick = () => {
    S.profile[b.dataset.rm] = S.profile[b.dataset.rm].filter((x) => x !== b.dataset.iso); saveProfile(); renderSettings(); refreshAll();
  }));
  $$("[data-add]", body).forEach((inp) => (inp.onchange = () => {
    const c = S.data.countries.find((x) => cname(x).toLowerCase() === inp.value.trim().toLowerCase());
    if (c && !S.profile[inp.dataset.add].includes(c.iso3)) { S.profile[inp.dataset.add].push(c.iso3); saveProfile(); renderSettings(); refreshAll(); }
  }));
  $("#refreshBtn").onclick = async (e) => {
    e.target.textContent = t("refreshing"); e.target.disabled = true;
    try { await fetch("api/refresh", { method: "POST" }); location.reload(); }
    catch { e.target.textContent = t("refresh"); e.target.disabled = false; alert(t("serverNeeded")); }
  };
}

/* ======================= campaign ======================= */
async function generateCampaign(iso) {
  const c = S.byIso[iso], sc = S.scores[iso];
  $("#campaignModal").hidden = false;
  $("#campaignBody").innerHTML = `<div class="loading"><span class="spinner"></span>${t("generating")}</div>`;
  const payload = { iso3: iso, sectors: [...S.sectors], mode: sc.direct ? "direct" : "partnership", lang: S.lang, distance_km: sc.dist,
    ngo: { name: S.profile.name, home: S.byIso[S.profile.home]?.name, budget: S.profile.budget } };
  let res;
  try {
    const r = await fetch("api/campaign", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    if (!r.ok) throw new Error(r.status);
    res = await r.json();
  } catch { $("#campaignBody").innerHTML = `<p>${t("serverNeeded")}</p>`; return; }
  const k = res.campaign, L = (x) => (Array.isArray(x) ? x : x ? [x] : []);
  const li = (arr, f = (x) => esc(x)) => `<ul>${L(arr).map((x) => `<li>${f(x)}</li>`).join("")}</ul>`;
  $("#campaignBody").innerHTML = `<div class="camp" id="campText">
    <div class="kicker"><span>${esc(cname(c))}</span><span>${t(k.mode === "direct" ? "direct" : "partner")}</span>${statusEl(c)}</div>
    <h1>${esc(k.title)}</h1><p class="lead">${esc(k.summary)}</p>
    <h3>${t("campWhy")}</h3>${li(k.why_now)}
    <h3>${t("campWhere")}</h3><p>${esc(k.where)}</p>
    <h3>${t("campTargets")}</h3>${li(k.target_groups)}
    <h3>${t("campActs")}</h3>${li(k.activities, (a) => `<b>${esc(a.name ?? a)}</b>${a.description ? " — " + esc(a.description) : ""}`)}
    ${L(k.partners).length ? `<h3>${t("campPartners")}</h3>${li(k.partners, (p) => `<b>${esc(p.name)}</b>${p.reason ? " — " + esc(p.reason) : ""}`)}` : ""}
    ${k.donor_message ? `<h3>${t("campDonor")}</h3><p>${esc(k.donor_message)}</p>` : ""}
    ${L(k.social_posts).length ? `<h3>${t("campPosts")}</h3>${L(k.social_posts).map((p) => `<div class="post">${esc(p)}</div>`).join("")}` : ""}
    <h3>${t("campRisks")}</h3>${li(k.risks)}
    ${L(k.kpis).length ? `<h3>${t("campKpis")}</h3>${li(k.kpis)}` : ""}
    <h3>${t("campSources")}</h3>${li(k.sources, (u) => `<a href="${esc(u)}" target="_blank" rel="noopener">${esc(u)}</a>`)}
  </div>
  ${res.warnings.map((w) => `<div class="callout" style="margin-top:12px">${esc(w)}</div>`).join("")}
  <div class="camp-foot"><span class="note" style="margin:0">${t("engine")}: ${esc(res.engine)}</span>
    <button class="btn ghost" id="copyBtn">${t("copy")}</button></div>`;
  $("#copyBtn").onclick = async () => {
    try { await navigator.clipboard.writeText($("#campText").innerText); $("#copyBtn").textContent = t("copied"); } catch {}
  };
}

/* ======================= shell ======================= */
function refreshAll() {
  computeScores();
  renderRanking();
  paintMap();
  if (S.selected) renderDetail(); else renderOverview();
  $("#legendTitle").textContent = t({ silence: "legendSilence", trend: "legendTrend" }[S.lens] || "legendPriority");
}
function applyLang() {
  document.documentElement.lang = S.lang;
  $$("[data-i18n]").forEach((el) => (el.textContent = t(el.dataset.i18n)));
  $("#langBtn").textContent = S.lang === "tr" ? "EN" : "TR";
  $("#fresh").textContent = `${t("updated")}: ${S.data.generated_at.slice(0, 10)}`;
  renderProfileLine(); renderNewsfeed();
  if ($("#drawer").classList.contains("open")) renderSettings();
  refreshAll();
}
function applyTheme() {
  document.documentElement.dataset.theme = S.theme;
  if (S.map) {
    S.map.setStyle(MAP_STYLE[S.theme]);
    S.map.once("style.load", () => { if (S.globe) S.map.setProjection({ type: "globe" }); });
  }
}

async function boot() {
  document.documentElement.dataset.theme = S.theme;
  S.data = await (await fetch("data/dashboard.json")).json();
  S.data.countries.forEach((c) => (S.byIso[c.iso3] = c));
  try { S.llm = (await (await fetch("api/status")).json()).llm; } catch {}
  $$("[data-lens]").forEach((b) => (b.onclick = () => {
    S.lens = b.dataset.lens; store.set("lens2", S.lens);
    $$("[data-lens]").forEach((x) => x.classList.toggle("on", x === b)); refreshAll();
  }));
  $$("[data-lens]").forEach((x) => x.classList.toggle("on", x.dataset.lens === S.lens));
  $$("[data-side]").forEach((b) => (b.onclick = () => {
    S.sideTab = b.dataset.side;
    $$("[data-side]").forEach((x) => x.classList.toggle("on", x === b));
    $("#rank").hidden = S.sideTab !== "rank"; $("#lensNote").hidden = S.sideTab !== "rank"; $("#newsfeed").hidden = S.sideTab !== "news";
  }));
  $("#langBtn").onclick = () => { S.lang = S.lang === "tr" ? "en" : "tr"; store.set("lang2", S.lang); applyLang(); };
  $("#themeBtn").onclick = () => { S.theme = S.theme === "light" ? "dark" : "light"; store.set("theme", S.theme); applyTheme(); };
  $("#settingsBtn").onclick = openDrawer;
  $("#drawerClose").onclick = closeDrawer;
  $("#drawerBackdrop").onclick = closeDrawer;
  $("#tEvents").onchange = paintMap;
  $("#tIgnored").onchange = paintMap;
  $("#tGlobe").onchange = (e) => { S.globe = e.target.checked; S.map.setProjection({ type: S.globe ? "globe" : "mercator" }); };
  $("#closeModal").onclick = () => ($("#campaignModal").hidden = true);
  $("#campaignModal").onclick = (e) => { if (e.target.id === "campaignModal") e.target.hidden = true; };
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    if (!$("#campaignModal").hidden) $("#campaignModal").hidden = true;
    else if ($("#drawer").classList.contains("open")) closeDrawer();
    else if (S.selected) { S.selected = null; history.replaceState(null, "", location.pathname); refreshAll(); }
  });
  applyLang();
  initMap();
}
boot();
