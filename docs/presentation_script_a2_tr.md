# 2. Ödev sunumu — konuşma metni (Türkçe, ~8 dakika)

Slaytlar İngilizce. İngilizce konuşma notları her slaytın altında (sunum modunda "notes").
Bölüşüm: **Ufuk 1–6**, **Tuna 7–13**. Her slayt ortalama 40 saniye.

---

## Ufuk

**1 · Kapak**
Merhaba, biz 6. grubuz. Projemiz STK Asistanı: STK'ların acil krizleri, özellikle medyanın görmezden geldiklerini bulmasına yardım eden bir araç. Bugün 1. ödevdeki geri bildiriminizden sonra neleri değiştirdiğimizi, neyi ölçtüğümüzü ve ne öğrendiğimizi anlatacağız.

**2 · Yedi geri bildirim**
Bize yedi öneri verdiniz. Beşini tamamladık. STK görüşmelerini zamanında ayarlayamadık; 3. ödevde yerine persona testleri yapacağız ve bunun daha zayıf bir yöntem olduğunu açıkça yazacağız. Sıralama duyarlılığının ilk adımı yapıldı, tamamı 3. ödevde.

**3 · Sessizlik merkezde**
Eskiden sessizlik "ihtiyaç çarpı ilgi eksikliği"ydi. Ama bir felakete 10 haber ile küçük bir krize 10 haber aynı şey değil. Artık her krizi, ihtiyacına göre hak ettiği haber payıyla karşılaştırıyoruz. Sudan hak ettiğinin sadece %10'unu alıyor ve 1. sırada. Ukrayna hak ettiğinin üç katından fazlasını alıyor. Uygulama artık evet/hayır etiketi yerine bu oranı gösteriyor.

**4 · GDELT**
1. ödevde medya örneğimiz küçüktü: 3 kaynaktan yaklaşık 90 haber. Şimdi GDELT kullanıyoruz: 30 günde 7 binden fazla kaynaktan yaklaşık 275 bin haber. Güzel haber şu: sıralama neredeyse değişmedi, ilk 10'un 8'i aynı. Yani ilk bulgumuz küçük örneğin tesadüfü değilmiş.

**5 · Türk ve Batı medyası**
Türk ve Batı medyasını karşılaştırmamızı istediniz. Türk medyası dış haberlerinin %33'ünü yüksek ihtiyaçlı krizlere ayırıyor, Batı medyası %19'unu. Ama grafiğe bakınca Türk medyası çoğunlukla Filistin, Yemen ve Suriye'ye odaklanıyor; Çad veya Madagaskar gibi Afrika krizleri ikisinde de sessiz. Yani Türk medyası "daha iyi" değil, farklı seçiyor.

**6 · ReliefWeb ve FTS**
ReliefWeb ve OCHA FTS'yi kullanmamızı istediniz. Bunları sadece karşılaştırma için kullanıyoruz, sıralamaya sokmuyoruz. ReliefWeb'deki raporlar ihtiyacı medyadan çok daha iyi takip ediyor. Medyanın en sessiz kaldığı 10 krizin 6'sını insani yardım sistemi görüyor. Ama dördü iki kere sessiz: Madagaskar, Timor-Leste, Nijer ve Burundi. Neden sıralamada değil? Bu sayılar ne kadar yazıldığını gösteriyor, nasıl yazıldığını değil. Yayıncılar bağışçılara ve ev sahibi hükümetlere bağımlı, "tarafsız" dilleri çoğu zaman sorumluyu adlandırmıyor. Bu dili 3. ödevde ölçeceğiz.

## Tuna

**7 · Gazze verisi**
Verinin kendisinde bir taraflılık bulduk. Bir haber Gazze hakkındaysa GDELT onu çoğunlukla Filistin'e değil İsrail'e yazıyor. Batı, Türk ve diğer kaynaklarda oran aynı, yani sorun yer belirleme algoritmasında. Ama etkisi gerçek: GDELT'e güvenen her araç Filistin'i eksik sayar. Biz bunu her ülke için aynı kuralla düzeltiyoruz.

**8 · Türkçe ve Arapça**
Modeli Türkçe ve Arapça test etmemizi istediniz. Eğitim verimizde bu diller yok, bu yüzden 300 etiketli metni çevirdik. Eski model Türkçede 0,34, Arapçada 0,20 aldı; yani okuyamıyordu. Çok dilli model 0,70'e çıkıyor. Uygulama artık dili algılayıp doğru modeli seçiyor. Tek kısıt: bunlar makine çevirisi; 3. ödevde gerçek başlıklarla test edeceğiz.

**9 · Yedi model**
Aynı 12 bin test metninde yedi yaklaşım denedik. Basit doğrusal modeller en iyisiydi ve bir dakikada yeniden eğitiliyor. Transformer'ı laptop işlemcisinde eğitmek yetmedi; bunu dürüstçe raporluyoruz. LLM tarafında DeepSeek OpenCode üzerinden çalıştı ama ücretsiz kota 37 metinde bitti; orada 10 puan öndeydi. Testi Claude ile 200 metne tamamladık: fark 1,5 puana düştü. Ders: küçük örnek yanıltır. LLM günde binlerce haber için de çok yavaş, bu yüzden sadece kampanya taslağı yazdırıyoruz.

**10 · Sektör bazlı hatalar (2×2 confusion matrix)**
Bir metin birden fazla sektöre ait olabildiği için tek büyük bir confusion matrix çizemiyoruz. Bunun yerine her sektör için ayrı bir 2×2 tablo var: gerçekte evet/hayır, model evet/hayır dedi. Sağlık ve eğitim güçlü, precision ve recall 0,8'in üstünde. Zayıf olanlar lojistik ve tarım, 0,5–0,6 civarı. Bunlar eğitim verisinde en az bulunan sektörler; macro-F1'in micro-F1'den düşük olmasının sebebi de bu.

**11 · Prototip**
Prototip gerçek veriyle baştan sona çalışıyor: veri topluyor, haberleri sınıflandırıyor, krizleri sessizliğe göre sıralıyor, ülke dosyasını açıyor ve kampanya taslağı yazıyor. LLM sadece bizim doğrulanmış verimizi kullanabiliyor, bir doğrulayıcı her sayıyı kontrol ediyor, her taslak hangi modelin yazdığını gösteriyor. Son onayı her zaman bir insan veriyor.

**12 · Açık kalanlar**
Bazı şeyler hâlâ açık. STK görüşmesi yapamadık; persona testi yapacağız ve bunu daha zayıf bir yöntem olarak adlandıracağız. Türkçe/Arapça testlerimiz çeviriye dayanıyor. Uygulama Arapça okuyabiliyor ama henüz Arapça haber kaynağımız yok; 3. ödevde ekleyeceğiz. Batı medyası listesi bizim seçimimiz. 3. ödevdeki ana sorumuz çerçeveleme: medya bir krize ne kadar değil, nasıl yer veriyor? Kurbanların adı geçiyor mu? Başlık "öldü" mü diyor, "öldürüldü" mü? Kime söz veriliyor?

**13 · Kapanış**
Tek cümleyle: insani yardım sistemi medyanın görmezden geldiği krizlerin çoğunu hâlâ görüyor, ama dört kriz iki kere sessiz: Madagaskar, Timor-Leste, Nijer ve Burundi. Küçük bir STK'nın görünürlük açısından en çok fark yaratabileceği yerler burası. Teşekkürler, sorularınızı alabiliriz.
