# STK Asistanı — Sunum metni (Türkçe, ~7 dakika)

**Ufuk → Slayt 1–6 · Tuna → Slayt 7–12**
İpucu: yavaş konuşun; **kalın** sayıları net söyleyin. Slaytlar İngilizce kalabilir, anlatım Türkçe.

---

## UFUK

### Slayt 1 — Kapak (20 sn)
Herkese merhaba. Biz 6. grubuz; ben Ufuk Gündoğar, arkadaşım Tuna Bilgen.
Projemizin adı STK Asistanı.
Bu, STK'lara yardımın en çok nerede gerektiğini gösteren bir yapay zekâ aracı — ana akım medyanın görmezden geldiği krizler de dahil.

### Slayt 2 — Problem (45 sn)
Önce problemle başlayalım.
Küçük STK'ların analist ekibi yok; yüzden fazla krizi aynı anda takip edemiyorlar.
Bu yüzden genellikle haberlere bakarak karar veriyorlar.
Ama haberler adil değil.
Son 30 günde BBC, Guardian ve New York Times'ın dünya haberlerinin **yüzde 38'i** Ukrayna ve Rusya hakkındaydı.
Sudan, Kongo, Somali, Suriye ve Lübnan hakkında ise **yüzde sıfır**.
Oysa Sudan'da son üç yılda yaklaşık **90 bin** çatışma kaynaklı ölüm var.
Yani yardım ihtiyacı değil, manşetleri takip ediyor.

### Slayt 3 — Çözümümüz (40 sn)
Bizim cevabımız STK Asistanı.
STK ekiplerinin kendi çalışma alanlarındaki en acil ve en çok unutulan krizleri bulmasına yardım ediyor; bunları kampanyaya, yerel ortaklığa ve sürdürülebilir projeye dönüştürüyor.
Dünyanın her yerinden STK'lar kullanabilir; ilk pilot kullanıcılarımız Türkiye'deki küçük STK'lar.
Ana hedefimiz SDG 17.17, yani sivil toplum ortaklıkları. Ayrıca 16.1, şiddetin azaltılması ve 2.1, açlığın sona erdirilmesi hedeflerini destekliyoruz.
Başarıyı üç şekilde ölçüyoruz: uzman etiketlerine karşı model doğruluğu, sıralamanın alan bilgisiyle kontrolü ve farklı STK profilleriyle testler.

### Slayt 4 — Nasıl çalışıyor (40 sn)
Bu şema aracın nasıl çalıştığını gösteriyor.
Solda girdiler var: STK'nın profili, isteğe bağlı bir saha notu ve her gün otomatik gelen veriler.
Ortada yapay zekâ kısmı var: iki sınıflandırıcı haberleri okuyor, model yeni verilerle kendini güncelliyor ve bir puanlama adımı krizleri sıralıyor.
Sağda çıktılar var: dünya haritası, her ülke için bir dosya ve kampanya ya da proje taslağı.
Son kararı her zaman bir insan veriyor.

### Slayt 5 — Veri (35 sn)
Sadece bağımsız veri kaynakları kullanıyoruz.
Örneğin: Uppsala Üniversitesi'nin çatışma verisi, Küresel Açlık Endeksi, Kızılhaç ve Kızılay verileri ve Gazze Sağlık Bakanlığı'nın kayıp verileri.
Ayrıca her gün 15 bağımsız haber kaynağını okuyoruz.
Üç Batılı haber kaynağını ise sadece hangi krizleri görmezden geldiklerini ölçmek için kullanıyoruz.

### Slayt 6 — Veri temizleme (40 sn)
Veriyi temizlemek sonuçlarımızı ciddi şekilde değiştirdi. Birkaç örnek vereyim.
Eğitim verisinde etiketi olmayan metinleri çıkardık; geriye **115 bin** temiz metin kaldı.
Çatışma veri seti Gazze'deki olayları İsrail'in altına yazıyor; biz **8 binden fazla** olayı Filistin'e taşıdık.
Ve en önemli kuralımız: eksik veri hiçbir zaman "ihtiyaç yok" olarak sayılmıyor.
Şimdi sözü Tuna'ya bırakıyorum.

---

## TUNA

### Slayt 7 — İlgi farkı (35 sn)
Teşekkürler Ufuk.
Bu grafik, ihtiyacı en yüksek krizlerin haberlerde ne kadar yer aldığını karşılaştırıyor.
Yeşil bağımsız medya, gri Batı medyası.
Filistin bağımsız haberlerin **yüzde 12,5'ini** alıyor, ama Batı haberlerinin sadece **yüzde 3,3'ünü**.
Sudan Batı medyasında sıfır. Ukrayna ise tam tersi.
Bu farkı araçta "sessizlik endeksi" olarak kullanıyoruz.

### Slayt 8 — Kişi başına ölüm (40 sn)
Toplam sayılar gerçeği gizleyebilir; bu yüzden ölümleri nüfusa göre hesaplıyoruz.
Her 100 bin kişide Filistin'de **1.622**, İsrail'de **16** ölüm var. Yani yaklaşık yüz kat fark.
Ayrıca Ukrayna'da kaydedilen ölümlerin sadece **yüzde 3'ü** sivil.
Bu yüzden sivillere yönelik şiddeti puanda ayrı bir bileşen olarak ölçüyoruz.

### Slayt 9 — İlk model (45 sn)
Şimdi ilk modelimiz.
Uzmanların etiketlediği **115 bin** metinle TF-IDF ve lojistik regresyon modeli eğittik.
Model **0,78** F1 skoruna ulaşıyor; basit anahtar kelime kuralları ise sadece **0,56**.
Bir dil yanlılığı da bulduk: model İspanyolcada daha zayıf. Bunu açıkça raporluyoruz.
Model yeni haberlerden de öğrenebiliyor. İlk güncellemeden sonra doğruluk aynı kaldı, bu yüzden güncelleme kabul edildi.

### Slayt 10 — Prototip (30 sn + demo)
Çalışan bir prototip de geliştirdik.
Solda örnek bir STK için sıralama var; Filistin 88 puanla ilk sırada.
Haritanın üç görünümü var: öncelik, sessizlik ve kötüleşme. Örneğin Yemen'de şiddet üç ayda dokuz kat arttı.
Sağda ülke dosyası var: puanın nedeni, eğilim, kişi başı yardım ve doğrulanmış yerel ortak.
Her il için de proje öneriyor: Herat'ta safran, nar ve badem; Kabil'de ise güvenlik nedeniyle acil yardım.
Hızlıca canlı göstereyim. *(Demo: haritayı aç → Filistin'e tıkla → Afganistan'da "Project ideas" sekmesi.)*

### Slayt 11 — Etik (45 sn)
Etik bizim için çok önemliydi.
Sonuçlarımızı defalarca kontrol ettik ve gerçek hatalar bulduk.
Örneğin ilk versiyonda Gazze çok düşük sıralanıyordu, çünkü eksik veri sıfır sayılıyordu.
Ayrıca gönderilen paranın her zaman sahaya ulaşmadığını öğrendik; örneğin abluka altında.
Bu sorunların hepsini düzelttik. Ve her kampanyayı bir insan onaylıyor.

### Slayt 12 — Sonraki adımlar (25 sn)
Ödev 2'de modelimizi bir transformer modeli ve bir LLM ile karşılaştıracağız.
Ödev 3'te aracı farklı STK profilleriyle test edeceğiz ve daha fazla Afrika haber kaynağı ekleyeceğiz.
Kodumuz GitHub'da.
Dinlediğiniz için teşekkürler. Sorularınızı almaktan memnuniyet duyarız.

---

## Olası sorular — kısa cevaplar

**Neden BM verisi kullanmadınız?**
Bağımsız kaynaklar istedik. İlk versiyonda tek bir kurumsal veri kaynağı, bazı nüfuslar sayılmadığı için Gazze'yi çok düşük sıralıyordu.

**LLM çalışıyor mu?**
Kod hazır. Şu an araç şablon kullanıyor; canlı LLM'i Ödev 2'de test edeceğiz.

**Sıralamanın doğru olduğunu nasıl biliyorsunuz?**
Alan bilgisiyle kontrol ediyoruz. Her hata bulduğumuzda nedenini bulup düzelttik. Ödev 3'te STK profilleriyle test edeceğiz.

**Neden TF-IDF, neden BERT değil?**
Hızlı yeniden eğitiliyor, açıklanabilir ve GPU gerektirmiyor. Transformer ile karşılaştırmayı Ödev 2'de yapacağız.

**Macro-F1 ile micro-F1 farkı ne?**
Micro tüm tahminleri birlikte sayar, büyük sektörler baskın olur. Macro her sektörü eşit sayar; küçük sektörlere karşı daha adildir.

**İsrail haritada neden gri?**
Bu, STK'nın kendi politikası olarak ayarlanan "hariç tutulan ülkeler" ayarı. Kullanıcı değiştirebilir; veriyi değiştirmedik.
