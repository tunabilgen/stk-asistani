# 2. Ödev sunumu — olası sorular ve cevaplar

Her soruda önce kısa Türkçe açıklama, sonra söylenebilecek kısa İngilizce cevap var.
Bilmediğiniz bir şey sorulursa uydurmayın: "We have not measured that yet; it is in our Assignment 3 plan." deyin.

---

## A. Sessizlik ve sıralama

**1. "İhtiyaç"ı (need) nasıl ölçüyorsunuz?**
İki parçalı. *Süreğen mağduriyet*: UCDP'den 100 bin kişi başına sivil ölüm, Küresel Açlık Endeksi (GHI) ve çatışma yoğunluğu. *Son dönem şiddeti*: son 3 ayın ölümleri. Sessizlik hesabında ikisinden büyük olanı kullanılıyor. Hepsi BM dışı kaynaklardan geliyor.
> "Need combines civilian deaths per 100,000 people from UCDP, the Global Hunger Index and recent conflict deaths. All from non-UN sources, and every number is named in the app."

**2. Oranı neden 1'de sınırlıyorsunuz?**
Haddinden fazla haber alan bir kriz (Ukrayna, 3,46) "eksi sessizlik" almasın diye. Fazla ilgi başka bir krizin sessizliğini telafi etmez.
> "Over-coverage is not negative silence. A crisis that gets more than its share simply has zero silence."

**3. Filistin her gün haberlerde; nasıl oluyor da hak ettiğinin sadece %59'unu alıyor?**
Çünkü Filistin'in ihtiyaç puanı en yüksek (1,0). Batı medyasının dış haberlerinin %3,4'ünü alıyor, ama ihtiyaç payı bundan daha büyük. "Çok haber var" ile "ihtiyaca göre yeterli haber var" farklı şeyler.
> "In absolute terms Palestine gets a lot of coverage. Relative to its need, which is the highest in our data, it still gets only 59% of its fair share."

**4. Neden ABD ve İngiltere haberlerini çıkarıyorsunuz?**
Batı medyası kendi ülkesini çok yazar. Biz *dış haberler* içindeki payı ölçüyoruz; yoksa ABD ve İngiltere bütün oranları bozar.
> "We measure foreign coverage. Home-country news would dominate the shares."

**5. "Batı medyası" kim? Bu liste taraflı değil mi?**
24 ana akım alan adı (BBC, Guardian, NYT, CNN, Reuters, AP, WSJ…), listesi kodda açık (`src/sources/gdelt.py`). Bizim seçimimiz; raporda kısıt olarak yazıyor. 3. ödevde listeyi değiştirince sonucun ne kadar değiştiğini ölçeceğiz.
> "It is our choice and it is public in the code. We list it as a limitation and will test how sensitive the ranking is to it."

**6. Sıralama ağırlıklara ne kadar duyarlı? (Hocanın 1. ödev geri bildirimi)**
Tamamı yapılmadı, dürüst olun. Yapılan tek kontrol: küçük RSS örneği ile GDELT'i karşılaştırdık, sıralamalar arası korelasyon 0,80 ve ilk 10'un 8'i aynı. Ağırlık analizi 3. ödevde.
> "Partly done: changing the media source kept 8 of the top 10. The full weight sensitivity analysis is in our Assignment 3 plan."

## B. GDELT, medya ve BM verileri

**7. 275 bin haberi gerçekten okudunuz mu?**
Hayır. GDELT her 30 dakikada bir haber kaydı yayımlıyor (link, kaynak, konum). 30 günün dosyalarını indirdik (30 Eylül – 29 Ekim) ve link başına ülkeleri saydık. Ham dosya (23 MB) bilgisayarda; repoda ülke bazlı özet ve indirme kodu var.
> "We did not read them. We counted GDELT event records: one link per article, with the country GDELT located it in."

**8. %33'e karşı %19 farkı anlamlı mı?**
Bu bir oran, istatistiksel test değil. Türk örneği daha küçük (1.584'e karşı 3.964 haber). Ayrıca Türk medyası çoğunlukla Filistin, Yemen ve Suriye'ye bakıyor; Afrika krizlerinde o da sessiz.
> "It is a descriptive share, not a test. The Turkish sample is smaller, and Turkish attention is concentrated on Palestine, Yemen and Syria."

**9. Korelasyonlar anlamlı mı?**
35 ülke, küçük örnek. Batı medyası ile ihtiyaç arasındaki ρ = 0,25 anlamlı değil (p = 0,14). ReliefWeb ile ihtiyaç arasındaki ρ = 0,63 anlamlı (p < 0,001). Yani "medya ihtiyacı takip etmiyor" demek güvenli; "hiç etkisi yok" demek değil.
> "With 35 countries, media versus need is weak and not significant; ReliefWeb versus need is strong and significant."

**10. ReliefWeb'de Filistin hakkında çok rapor olması doğal değil mi, orada spor haberi yok?**
Bu yüzden ham sayı değil, 35 kriz içindeki payları ihtiyaca göre karşılaştırıyoruz.
> "Raw counts are not comparable, so we compare each crisis's share within the 35 crises, relative to need."

**11. ReliefWeb ve FTS'yi neden sıralamaya koymadınız?**
Sayılar ne kadar yazıldığını gösteriyor, nasıl yazıldığını değil. Yayıncılar bağışçılara ve ev sahibi hükümetlere bağımlı; tarafsızlık ilkesi yüzünden çoğu zaman sorumluyu adlandırmıyorlar. Sıralamanın tek bir kurumsal ekosisteme bağlı olmasını istemiyoruz. 1. ödevin ilk sürümünde bu yüzden Gazze olması gerekenden düşük sıralanmıştı.
> "They show volume, not language, and their publishers depend on donors and host governments. We keep the ranking independent of one institutional ecosystem."

**12. ReliefWeb verisini nasıl aldınız?**
API onaylı uygulama adı istiyor; herkese açık RSS'i kullandık. RSS bir sorguda en çok 20 rapor veriyor; tarih aralıklarını bölerek saydık. Sadece Yemen'de bir gün sınıra takıldı, Yemen'in sayısı alt sınır.
> "Through the public RSS feed, splitting date ranges to get complete counts. Only Yemen hit the cap on one day, so its count is a lower bound."

**13. Sessiz krizler daha az fon alıyor mu? ($3,9'a karşı $51,6)**
Bu bir ipucu, kanıt değil. Görünür krizlerin ihtiyacı da daha yüksek. İhtiyaç kontrol edilince ilişki zayıf (kısmi ρ = 0,28, p = 0,10, anlamlı değil).
> "It is a hint, not proof: after controlling for need, the link is weak and not significant."

**14. Gazze haberlerinin İsrail'e yazılması Batı medyasının taraflılığı değil mi?**
Bu ölçümde oran her grupta aynı (Batı %90, Türk %96, diğer %90). Yani sebep GDELT'in konum algoritması, tek bir medya grubu değil. Batı medyasının *dili* taraflı olabilir; onu 3. ödevde çerçeveleme analiziyle ölçeceğiz. Bu veriyle onu iddia edemeyiz.
> "In this measure the rate is the same for every group, so it comes from GDELT's geocoder. Whether the language is biased is a different question, which we measure in Assignment 3."

## C. Modeller

**15. Neden confusion matrix tek bir tablo değil?**
Görev çok etiketli: bir metin aynı anda birden fazla sektöre ait olabilir. Bu yüzden her sektör kendi evet/hayır sorusu; her sektöre bir 2×2 tablo.
> "The task is multi-label, so each sector is its own yes/no decision with its own 2×2 matrix."

**16. Micro-F1 ve macro-F1 farkı ne?**
Micro: bütün kararlar tek havuzda; sık sektörler (sağlık, koruma) baskın. Macro: 10 sektörün ortalaması; nadir sektörler (lojistik, tarım) eşit ağırlıkta. Macro daha düşük, çünkü nadir sektörler zayıf.
> "Micro-F1 is dominated by frequent sectors; macro-F1 weights every sector equally, so it shows the weak rare ones."

**17. Eşikleri ayarlarken teste bakıp hile yapmadınız mı?**
Hayır. Eşikler doğrulama (validation) setinde seçildi, test seti sadece en sonda bir kez kullanıldı. Bütün modellere aynı kural uygulandı.
> "Thresholds were tuned on the validation split only; the test split was used once, the same way for every model."

**18. Fine-tuning neden bu kadar kötü (0,41)? Neden GPU / Colab kullanmadınız?**
Laptop işlemcisinde verinin sadece %10'u, 2 tur; kayıp hâlâ düşüyordu. Yani yöntem değil, hesaplama gücü. GPU ile 3. ödevde tekrar denenebilir. Ama doğrusal model zaten 0,78 ve bir dakikada yeniden eğitiliyor; uygulama için yeterli.
> "Compute, not the method: 10% of the data for 2 epochs on a CPU. We report it as a negative result."

**19. SVM biraz daha iyiyken neden lojistik regresyon?**
Fark çok küçük (0,781'e karşı 0,780). Lojistik regresyon olasılık veriyor; panel ve kendi kendine öğrenme adımı olasılığa ihtiyaç duyuyor.
> "They are tied, and logistic regression gives probabilities, which the dashboard and self-training need."

**20. LLM testini Claude yapmış. Bu adil mi?**
DeepSeek'in ücretsiz kotası 37 metinde bitti. Testi tamamlamak için Claude aynı 200 metni, aynı sektör tanımlarıyla, doğru cevapları görmeden etiketledi. Kısıtları da söyleyin:
- Bu bir API çalıştırması değil, sohbet içinde tek seferlik bir etiketleme.
- HumSet açık bir veri seti; LLM'in eğitiminde görülmüş olabilir.
- Claude bu projede kod yazarken de kullanılan araç.

Sonuç: LLM farkı sadece 1,5 puan çıktı. Yani "LLM çok daha iyi" demiyoruz, tersine küçük örneğin yanılttığını gösteriyoruz.
> "Blind, same prompt, all 200 excerpts. It is one pass, not a scripted run, and HumSet is public, so we treat it as indicative. The main lesson: the lead shrank from 10 points on 37 texts to 1.5 on 200."

**21. Türkçe/Arapça sonucu çeviriyle ölçülmüş; gerçek haberde de böyle mi?**
Bilmiyoruz; makine çevirisi gerçek haberden daha temiz. 3. ödevde gerçek Türkçe ve Arapça başlıkları elle etiketleyip test edeceğiz. Arapça haber kaynağımız da henüz yok.
> "We don't know yet. Translations are cleaner than real news; real headlines are in our Assignment 3 plan, and Arabic sources too."

## D. Uygulama, LLM ve etik

**22. LLM uydurursa ne olur?**
LLM sadece bizim verdiğimiz doğrulanmış verileri (kaynak adlı sayılar, doğrulanmış ortak adayları) kullanabiliyor. Bir doğrulayıcı listede olmayan ortak adlarını siliyor, verilerde olmayan sayıları işaretliyor. Son onayı her zaman bir insan veriyor.
> "It may only use our facts; a validator removes unknown partners and flags unknown numbers; a human approves every text."

**23. Videodaki kampanya taslağı canlı mıydı?**
Hayır, kayıtlı taslaktı ve ekranda öyle etiketli. Sudan (Türkçe) taslağını DeepSeek yazdı. Kota bitince diğer beş taslağı Claude aynı talimat ve verilerle yazdı; her birinin üzerinde hangi modelin yazdığı görünüyor.
> "Saved drafts, clearly labelled with the model that wrote them. Sudan was DeepSeek; five others Claude, with the same prompt and facts."

**24. Varsayılan olarak İsrail'in "kapsam dışı" olması taraflılık değil mi?**
Bu, STK'nın kendi ayarı (ekip olarak bizim seçtiğimiz varsayılan değer) ve değiştirilebilir. Veri değişmiyor: ülke gri görünüyor ve üzerinde "STK politikası gereği kapsam dışı" yazıyor. Yani seçim gizlenmiyor, şeffaf.
> "It is an NGO policy setting, editable by the user. The data is not changed, and the map says clearly why the country is grey."

**25. STK'larla hiç konuşmadınız; aracın işe yaradığını nereden biliyorsunuz?**
Henüz bilmiyoruz; bunu açıkça söyleyin. 3. ödevde dört persona ile yapılandırılmış testler yapacağız (küçük Türk STK'sı, uluslararası STK, gazeteci, bağışçı). Bunun gerçek kullanıcı görüşmesinden daha zayıf olduğunu raporda yazacağız.
> "We don't know yet. Persona tests come in Assignment 3, and we will say clearly that they are weaker than real interviews."

**26. Projede yapay zekâ araçlarını nasıl kullandınız?**
Dürüst olun: kod yazmada ve analizde Claude Code'dan yardım aldık. Proje fikri, kararlar (BM verisini sıralamaya almamak, ihtiyaca göre sessizlik, Gazze düzeltmesi) ve yorumlar bizim. Claude'un yazdığı kampanya taslakları ve LLM testi her yerde etiketli.
> "We used Claude Code for coding and analysis. The design decisions and interpretations are ours, and AI-written content is labelled."

**27. Hangi SDG hedefleri?**
17.17 (sivil toplum ortaklıkları), 16.1 (şiddete bağlı ölümleri azaltmak), 2.1 (açlığı bitirmek), 1.5 / 11.5 (afetlere dayanıklılık).
> "17.17 partnerships, 16.1 violence, 2.1 hunger, plus 1.5 and 11.5 on disasters."

---

**En önemli üç kural:**
1. Persona testi **yapılacak**, yapılmadı.
2. Arapça haber **toplanmıyor**, sadece model Arapça okuyabiliyor.
3. Gazze bulgusu **algoritma hatası**; "Batı taraflı" iddiası 3. ödevin konusu.
