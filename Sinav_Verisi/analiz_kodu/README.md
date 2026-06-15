# 🔬 Analiz Kodu — Yeniden Üretilebilirlik

Bu klasör, [`../README.md`](../README.md) içindeki tüm tablo ve grafikleri **sıfırdan üreten** Python betiklerini içerir. Amaç, analizin tamamen şeffaf ve denetlenebilir olmasıdır: herkes kodu çalıştırıp aynı sonuçlara ulaşabilir.

## Kurulum

Python 3.10+ gerekir.

```bash
# (önerilen) sanal ortam
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## Çalıştırma

Betikler, soru kitapçıklarını deponun kök dizininden okur. Bu klasör repo içindeyse
(`KKTC_Egitim/Sinav_Verisi/analiz_kodu/`) repo kökü otomatik bulunur:

```bash
python calistir.py
```

Repo başka bir konumdaysa yolu belirtin:

```bash
KKTC_REPO=/yol/KKTC_Egitim python calistir.py     # Windows: set KKTC_REPO=...
```

Tüm çıktılar `cikti/` klasörüne yazılır:
- `cikti/veri/*.json` — ara veri (metrikler, çeşitlilik, okunabilirlik, korelasyonlar…)
- `cikti/grafikler/*.png` — 6 grafik
- `cikti/KGS_Ingilizce_Analiz.xlsx` — konsolide çalışma kitabı

> Yayımlanmış grafik/Excel dosyalarını güncellemek isterseniz `cikti/` içeriğini bir üst klasöre kopyalayabilirsiniz.

## Betikler

| Dosya | Ne yapar | Çıktı |
|---|---|---|
| `ortak.py` | Paylaşılan: PDF çıkarımı, karakter düzeltme, bölüm izolasyonu, tokenizasyon | — |
| `01_metrikler.py` | Türkçe & İngilizce: kelime, söz/soru, cümle/kelime uzunluğu, MATTR | `metrikler.json` |
| `02_kelime_cesitliligi.py` | İngilizce: farklı kelime, nadir/ileri kelime (sözlük + wordfreq) | `kelime_cesitliligi.json` |
| `03_okunabilirlik.py` | İngilizce: Flesch, FK, Fog, okuma süresi | `okunabilirlik.json` |
| `04_matematik_vs_ingilizce.py` | Aynı oturumda İng vs Mat yükü (kelime/sayı/sembol/karakter) | `matematik_oturum.json` |
| `05_sonuc_korelasyon.py` | % başarı, kohort-arındırma, korelasyonlar | `korelasyonlar.json` |
| `06_grafikler.py` | 6 grafiği üretir | `grafikler/*.png` |
| `07_excel.py` | Konsolide Excel kitabını üretir | `*.xlsx` |
| `calistir.py` | Hepsini sırayla çalıştırır | — |

Her betik tek başına da çalıştırılabilir (ör. `python 03_okunabilirlik.py`), ancak
`05`, `06` ve `07` kendinden önceki adımların JSON çıktılarına ihtiyaç duyar.

## Girdi verisi

- **Soru kitapçıkları:** deponun kökündeki PDF'ler (`YIL/N.Basamak/KGS_*_Sorular.pdf`).
- **Sınav sonuçları:** [`girdi/tmk_cee2_sonuclari.csv`](girdi/tmk_cee2_sonuclari.csv) — Lefkoşa TMK CEE-2 ders ortalamaları (ham doğru sayısı). Düzenlenebilir; yeni yıl eklemek için bu dosyaya satır ekleyin.

## Yöntem özeti

1. Her bölüm, başlık (`İNGİLİZCE TESTİ` / `TÜRKÇE TESTİ` / `MATEMATİK TESTİ`) ile bitiş ifadesi (`…BİTMİŞTİR`) arasından izole edilir.
2. Tekrarlayan başlıklar, sayfa numaraları ve şık işaretçileri temizlenir; eski PDF'lerdeki bozuk karakter kodlaması ve ligatürler düzeltilir.
3. Metrikler hesaplanır (kelime, çeşitlilik, nadirlik, okunabilirlik).
4. Sınav sonuçları kohort-arındırılır (her yıl diğer derslerin ortalaması çıkarılır).
5. Korelasyonlar hesaplanır.

Ayrıntılar ve sınırlar için ana belgeye bakın: [`../README.md`](../README.md).

## Sınırlar

- Geometri/şekil içeren sorular görsel olduğundan metne yansımaz (özellikle Matematik). Bu, metin/sembol yükünü ölçer, kavramsal zorluğu değil.
- Sonuç verisi tek okula aittir; korelasyon nedensellik değildir; örneklem küçüktür (n = 8–10 yıl).

---
*Açık kaynak eğitim katkısı. Atıf yapılarak paylaşılabilir.*
