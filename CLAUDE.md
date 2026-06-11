# CLAUDE.md

## Proje

KKTC Kolejlere Giris Sinavi (KGS) gecmis yil arsivi + **online deneme uygulamasi**.
Ogrenciler orijinal soru kitapciklarini (PDF) tarayicida acip dijital optik formla
sinavi cozer, sonuc aninda hesaplanir. Tamamen statik site, ucretsiz ve istemci tarafli.

- Canli site: GitHub Pages, `main` / root (repo: https://github.com/RYucel/KKTC_Egitim)
- Yerel test: `python -m http.server 8000` (fetch kullanildigi icin `file://` calismaz)

## Yapi

```
index.html            SPA (ana sayfa + sinav + sonuc gorunumleri)
assets/app.js         Uygulama mantigi (PDF.js CDN, localStorage, puanlama)
assets/style.css      Stiller (turuncu optik form temasi)
data/exams.json       TEK VERI KAYNAGI: 34 oturum, cevap anahtarlari, PDF yollari
YYYY/N.Basamak/       Orijinal sinav PDF'leri ve taranmis cevap anahtarlari
tools/                OMR betikleri (anahtarlarin cikarilmasi/dogrulanmasi)
_work/                Gecici uretilen dosyalar — gitignore'da, silinebilir
_Kaynak_Kilavuz/      Resmi KGS kilavuzu
```

## Sinav yapisi (2016-2026 sabit)

- **1. Oturum (90 dk):** Turkce 27 + Fen ve Teknoloji 14 + Sosyal Bilgiler 10 = 51 soru
- **2. Oturum (90 dk):** Ingilizce 22 + Matematik 27 = 49 soru
- 4 secenek (A-D), ders icinde 1'den baslayan numaralama (optik form duzeni)
- KGS-1 Ocak, KGS-2 Haziran; KGP = KGS-1 x %50 + KGS-2 x %50
- Resmi puanlama formulu yayinlanmiyor; uygulama yalnizca dogru oranini gosterir
  (bu kisitlama UI'da acikca belirtiliyor — kaldirma)

## Cevap anahtarlari — KRITIK

`data/exams.json` icindeki anahtarlar taranmis optik formlardan OMR ile cikarildi ve
**hem gorsel hem otomatik capraz kontrolle dogrulandi**. Eksik tek anahtar: 2018
2.Basamak 2.Oturum (`keys: null`, resmi anahtar hic yayinlanmamis).

Anahtar degisikligi/eklemede ZORUNLU adimlar:

1. Yeni Cevap dosyasini yil klasorune koy (adlandirma: `KGS_<yil>_<N>.Basamak_<N>.Oturum_<Sorular|Cevap>.<pdf|jpg>`)
2. `python tools/detect_keys.py "<dosya yolu>"` ile dene (2026+ soluk formlar icin `tools/decode_2026.py`)
3. `tools/block_crop.py <dosya-adi-parcasi> <blok-no>` ile yuksek cozunurluklu kirpinti uret,
   anahtari GORSEL olarak satir satir dogrula (Read araciyla goruntule)
4. `exams.json`'a ekle, sonra `python tools/check_dataset.py` calistir → "hard mismatches: 0" beklenir

## OMR betikleri ve bilinen tuzaklar

- `tools/detect_keys.py` — ana detektor: turuncu/kirmizi halka izgarasini bulur,
  isaretli secenek = eksik halka + koyuluk ornekleme. `detect_best()` 180° donmus
  taramalari otomatik dener (2025 1.Basamak fotograflari bas asagiydi!).
- Form renkleri yillara gore degisir: turuncu (2021-24 PDF), kirmizi (2016-20 JPG),
  soluk somon (2025-2B), soluk krem-halkasiz (2026+). 2026 formlarinda halka yok →
  `decode_2026.py` koyu isaret kumelemesi kullanir.
- 2024-2B-1O taramasinda zemin bantlari halkalarla birlesik → ring detektoru calismaz,
  `decode_2026.decode()` ile cozulur.
- Bazi formlarda anahtar keceli kalemle isaretli (halka gorunur kalir) → koyuluk sinyali esastir.
- Sahte "blok"lar: KODLAMA ORNEKLERI kutusu ve ogrenci bilgi alani; n<9 bloklar elenir.

## Uygulama (assets/app.js) sozlesmeleri

- `exams.json` semasi: `{id: "YYYY-B-O", year, basamak, oturum, pdf, answerSheet, keys: {DersAdi: "ABCD..."} | null}`
- Ders adlari `keys` nesnesinin anahtarlaridir; siralama = optik formdaki blok sirasi. Degistirme.
- localStorage anahtari: `kgs-state-<id>`; sema degisirse eski kayitlarla uyumlulugu dusun.
- `keys: null` olan sinavlar listelenir ama puanlanamaz ("cevap anahtari yok" rozeti).
- PDF.js 3.11.174 UMD (CDN); 4.x'e gecis ESM gerektirir, gerekmedikce dokunma.

## Test

- E2E: `_work/e2e_test.js` (puppeteer-core + sistem Edge, `%TEMP%\kgs_e2e` icinde calistir;
  once `python -m http.server 8421` baslat). Skor/inceleme/kalicilik asercion'lari var.
- Hizli kontrol: `node --check assets/app.js` + `python tools/check_dataset.py`

## Stil/dil

- UI dili Turkce; README bilincli olarak aksansiz ASCII Turkce ("Gecmis", "Sinavi") — koru.
- Commit mesajlari Turkce, kisa ozet + madde isaretleri.
- Telif notu: dokumanlar KKTC MEB'e ait, yalnizca egitim amacli — footer/README'den kaldirma.
