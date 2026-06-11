# KKTC Kolejlere Giris Sinavi (KGS) - Gecmis Yillar Arsivi ve Online Deneme Uygulamasi

Kuzey Kibris Turk Cumhuriyeti (KKTC) Milli Egitim Bakanligi tarafindan yapilan **Kolejlere Giris Sinavi (KGS)** gecmis yil sorulari ve cevap anahtarlari. Tum ogrencilerin ucretsiz erisimine acik bir kaynak olarak duzenlenmistir.

## Online Deneme Uygulamasi

Bu depo ayni zamanda gecmis yil sinavlarini **orijinal kitapciklariyla online cozme** uygulamasi icerir ([index.html](index.html)):

- Orijinal soru kitapcigi tarayicida goruntulenir (sekiller/resimler aynen korunur, PDF.js).
- Gercek optik form duzeninde dijital cevap kagidi (1. Oturum: Turkce 27 + Fen 14 + Sosyal 10; 2. Oturum: Ingilizce 22 + Matematik 27).
- 90 dakikalik geri sayim, otomatik kaydetme (tarayici localStorage), yarim kalan sinava devam etme.
- Sinav sonunda ders bazinda dogru/yanlis/bos dokumu, soru soru inceleme modu.
- Tamamen statik site: GitHub Pages uzerinde dogrudan yayinlanabilir (Settings > Pages > main branch / root).

Cevap anahtarlari [data/exams.json](data/exams.json) dosyasindadir; taranmis optik formlardan [tools/](tools/) altindaki OMR betikleriyle cikarilmis, tamami gorsel olarak ve otomatik capraz kontrol ile dogrulanmistir (`python tools/check_dataset.py`). Tek eksik anahtar: 2018 2. Basamak 2. Oturum (resmi anahtar yayinlanmamis).

Yerel calistirma:

```bash
python -m http.server 8000
# http://localhost:8000
```

## Sinav Yapisi

- **1. Basamak** - her yil **Ocak** ayinda, **2 oturum** halinde yapilir.
- **2. Basamak** - her yil **Haziran** ayinda, **2 oturum** halinde yapilir.

Her oturum icin, mevcut oldugunda hem **Sorular** hem de **Cevap Anahtari** dosyasi bulunur.

## Klasor Yapisi

```
YIL / BASAMAK / KGS_<yil>_<basamak>_<oturum>_<Sorular|Cevap>.<uzanti>
```

## Icerik

### 2016

**1. Basamak (Ocak)**

| Oturum | Sorular | Cevap Anahtari |
|--------|---------|----------------|
| 1. Oturum | [KGS_2016_1.Basamak_1.Oturum_Sorular.pdf](2016/1.Basamak/KGS_2016_1.Basamak_1.Oturum_Sorular.pdf) | [KGS_2016_1.Basamak_1.Oturum_Cevap.jpg](2016/1.Basamak/KGS_2016_1.Basamak_1.Oturum_Cevap.jpg) |
| 2. Oturum | [KGS_2016_1.Basamak_2.Oturum_Sorular.pdf](2016/1.Basamak/KGS_2016_1.Basamak_2.Oturum_Sorular.pdf) | [KGS_2016_1.Basamak_2.Oturum_Cevap.jpg](2016/1.Basamak/KGS_2016_1.Basamak_2.Oturum_Cevap.jpg) |

### 2017

**1. Basamak (Ocak)**

| Oturum | Sorular | Cevap Anahtari |
|--------|---------|----------------|
| 1. Oturum | [KGS_2017_1.Basamak_1.Oturum_Sorular.pdf](2017/1.Basamak/KGS_2017_1.Basamak_1.Oturum_Sorular.pdf) | [KGS_2017_1.Basamak_1.Oturum_Cevap.jpg](2017/1.Basamak/KGS_2017_1.Basamak_1.Oturum_Cevap.jpg) |
| 2. Oturum | [KGS_2017_1.Basamak_2.Oturum_Sorular.pdf](2017/1.Basamak/KGS_2017_1.Basamak_2.Oturum_Sorular.pdf) | [KGS_2017_1.Basamak_2.Oturum_Cevap.jpg](2017/1.Basamak/KGS_2017_1.Basamak_2.Oturum_Cevap.jpg) |

**2. Basamak (Haziran)**

| Oturum | Sorular | Cevap Anahtari |
|--------|---------|----------------|
| 2. Oturum | [KGS_2017_2.Basamak_2.Oturum_Sorular.pdf](2017/2.Basamak/KGS_2017_2.Basamak_2.Oturum_Sorular.pdf) | [KGS_2017_2.Basamak_2.Oturum_Cevap.pdf](2017/2.Basamak/KGS_2017_2.Basamak_2.Oturum_Cevap.pdf) |

### 2018

**1. Basamak (Ocak)**

| Oturum | Sorular | Cevap Anahtari |
|--------|---------|----------------|
| 2. Oturum | [KGS_2018_1.Basamak_2.Oturum_Sorular.pdf](2018/1.Basamak/KGS_2018_1.Basamak_2.Oturum_Sorular.pdf) | [KGS_2018_1.Basamak_2.Oturum_Cevap.jpg](2018/1.Basamak/KGS_2018_1.Basamak_2.Oturum_Cevap.jpg) |

**2. Basamak (Haziran)**

| Oturum | Sorular | Cevap Anahtari |
|--------|---------|----------------|
| 2. Oturum | [KGS_2018_2.Basamak_2.Oturum_Sorular.pdf](2018/2.Basamak/KGS_2018_2.Basamak_2.Oturum_Sorular.pdf) | - |

### 2019

**2. Basamak (Haziran)**

| Oturum | Sorular | Cevap Anahtari |
|--------|---------|----------------|
| 1. Oturum | [KGS_2019_2.Basamak_1.Oturum_Sorular.pdf](2019/2.Basamak/KGS_2019_2.Basamak_1.Oturum_Sorular.pdf) | [KGS_2019_2.Basamak_1.Oturum_Cevap.jpg](2019/2.Basamak/KGS_2019_2.Basamak_1.Oturum_Cevap.jpg) |
| 2. Oturum | [KGS_2019_2.Basamak_2.Oturum_Sorular.pdf](2019/2.Basamak/KGS_2019_2.Basamak_2.Oturum_Sorular.pdf) | [KGS_2019_2.Basamak_2.Oturum_Cevap.jpg](2019/2.Basamak/KGS_2019_2.Basamak_2.Oturum_Cevap.jpg) |

### 2020

**1. Basamak (Ocak)**

| Oturum | Sorular | Cevap Anahtari |
|--------|---------|----------------|
| 2. Oturum | [KGS_2020_1.Basamak_2.Oturum_Sorular.pdf](2020/1.Basamak/KGS_2020_1.Basamak_2.Oturum_Sorular.pdf) | [KGS_2020_1.Basamak_2.Oturum_Cevap.pdf](2020/1.Basamak/KGS_2020_1.Basamak_2.Oturum_Cevap.pdf) |

**2. Basamak (Haziran)**

| Oturum | Sorular | Cevap Anahtari |
|--------|---------|----------------|
| 1. Oturum | [KGS_2020_2.Basamak_1.Oturum_Sorular.pdf](2020/2.Basamak/KGS_2020_2.Basamak_1.Oturum_Sorular.pdf) | [KGS_2020_2.Basamak_1.Oturum_Cevap.jpg](2020/2.Basamak/KGS_2020_2.Basamak_1.Oturum_Cevap.jpg) |
| 2. Oturum | [KGS_2020_2.Basamak_2.Oturum_Sorular.pdf](2020/2.Basamak/KGS_2020_2.Basamak_2.Oturum_Sorular.pdf) | [KGS_2020_2.Basamak_2.Oturum_Cevap.jpg](2020/2.Basamak/KGS_2020_2.Basamak_2.Oturum_Cevap.jpg) |

### 2021

**1. Basamak (Ocak)**

| Oturum | Sorular | Cevap Anahtari |
|--------|---------|----------------|
| 1. Oturum | [KGS_2021_1.Basamak_1.Oturum_Sorular.pdf](2021/1.Basamak/KGS_2021_1.Basamak_1.Oturum_Sorular.pdf) | [KGS_2021_1.Basamak_1.Oturum_Cevap.pdf](2021/1.Basamak/KGS_2021_1.Basamak_1.Oturum_Cevap.pdf) |
| 2. Oturum | [KGS_2021_1.Basamak_2.Oturum_Sorular.pdf](2021/1.Basamak/KGS_2021_1.Basamak_2.Oturum_Sorular.pdf) | [KGS_2021_1.Basamak_2.Oturum_Cevap.pdf](2021/1.Basamak/KGS_2021_1.Basamak_2.Oturum_Cevap.pdf) |

### 2022

**1. Basamak (Ocak)**

| Oturum | Sorular | Cevap Anahtari |
|--------|---------|----------------|
| 1. Oturum | [KGS_2022_1.Basamak_1.Oturum_Sorular.pdf](2022/1.Basamak/KGS_2022_1.Basamak_1.Oturum_Sorular.pdf) | [KGS_2022_1.Basamak_1.Oturum_Cevap.pdf](2022/1.Basamak/KGS_2022_1.Basamak_1.Oturum_Cevap.pdf) |
| 2. Oturum | [KGS_2022_1.Basamak_2.Oturum_Sorular.pdf](2022/1.Basamak/KGS_2022_1.Basamak_2.Oturum_Sorular.pdf) | [KGS_2022_1.Basamak_2.Oturum_Cevap.pdf](2022/1.Basamak/KGS_2022_1.Basamak_2.Oturum_Cevap.pdf) |

**2. Basamak (Haziran)**

| Oturum | Sorular | Cevap Anahtari |
|--------|---------|----------------|
| 1. Oturum | [KGS_2022_2.Basamak_1.Oturum_Sorular.pdf](2022/2.Basamak/KGS_2022_2.Basamak_1.Oturum_Sorular.pdf) | [KGS_2022_2.Basamak_1.Oturum_Cevap.pdf](2022/2.Basamak/KGS_2022_2.Basamak_1.Oturum_Cevap.pdf) |
| 2. Oturum | [KGS_2022_2.Basamak_2.Oturum_Sorular.pdf](2022/2.Basamak/KGS_2022_2.Basamak_2.Oturum_Sorular.pdf) | [KGS_2022_2.Basamak_2.Oturum_Cevap.pdf](2022/2.Basamak/KGS_2022_2.Basamak_2.Oturum_Cevap.pdf) |

### 2023

**1. Basamak (Ocak)**

| Oturum | Sorular | Cevap Anahtari |
|--------|---------|----------------|
| 1. Oturum | [KGS_2023_1.Basamak_1.Oturum_Sorular.pdf](2023/1.Basamak/KGS_2023_1.Basamak_1.Oturum_Sorular.pdf) | [KGS_2023_1.Basamak_1.Oturum_Cevap.pdf](2023/1.Basamak/KGS_2023_1.Basamak_1.Oturum_Cevap.pdf) |
| 2. Oturum | [KGS_2023_1.Basamak_2.Oturum_Sorular.pdf](2023/1.Basamak/KGS_2023_1.Basamak_2.Oturum_Sorular.pdf) | [KGS_2023_1.Basamak_2.Oturum_Cevap.pdf](2023/1.Basamak/KGS_2023_1.Basamak_2.Oturum_Cevap.pdf) |

**2. Basamak (Haziran)**

| Oturum | Sorular | Cevap Anahtari |
|--------|---------|----------------|
| 1. Oturum | [KGS_2023_2.Basamak_1.Oturum_Sorular.pdf](2023/2.Basamak/KGS_2023_2.Basamak_1.Oturum_Sorular.pdf) | [KGS_2023_2.Basamak_1.Oturum_Cevap.pdf](2023/2.Basamak/KGS_2023_2.Basamak_1.Oturum_Cevap.pdf) |
| 2. Oturum | [KGS_2023_2.Basamak_2.Oturum_Sorular.pdf](2023/2.Basamak/KGS_2023_2.Basamak_2.Oturum_Sorular.pdf) | [KGS_2023_2.Basamak_2.Oturum_Cevap.pdf](2023/2.Basamak/KGS_2023_2.Basamak_2.Oturum_Cevap.pdf) |

### 2024

**1. Basamak (Ocak)**

| Oturum | Sorular | Cevap Anahtari |
|--------|---------|----------------|
| 1. Oturum | [KGS_2024_1.Basamak_1.Oturum_Sorular.pdf](2024/1.Basamak/KGS_2024_1.Basamak_1.Oturum_Sorular.pdf) | [KGS_2024_1.Basamak_1.Oturum_Cevap.pdf](2024/1.Basamak/KGS_2024_1.Basamak_1.Oturum_Cevap.pdf) |
| 2. Oturum | [KGS_2024_1.Basamak_2.Oturum_Sorular.pdf](2024/1.Basamak/KGS_2024_1.Basamak_2.Oturum_Sorular.pdf) | [KGS_2024_1.Basamak_2.Oturum_Cevap.pdf](2024/1.Basamak/KGS_2024_1.Basamak_2.Oturum_Cevap.pdf) |

**2. Basamak (Haziran)**

| Oturum | Sorular | Cevap Anahtari |
|--------|---------|----------------|
| 1. Oturum | [KGS_2024_2.Basamak_1.Oturum_Sorular.pdf](2024/2.Basamak/KGS_2024_2.Basamak_1.Oturum_Sorular.pdf) | [KGS_2024_2.Basamak_1.Oturum_Cevap.pdf](2024/2.Basamak/KGS_2024_2.Basamak_1.Oturum_Cevap.pdf) |
| 2. Oturum | [KGS_2024_2.Basamak_2.Oturum_Sorular.pdf](2024/2.Basamak/KGS_2024_2.Basamak_2.Oturum_Sorular.pdf) | [KGS_2024_2.Basamak_2.Oturum_Cevap.pdf](2024/2.Basamak/KGS_2024_2.Basamak_2.Oturum_Cevap.pdf) |

### 2025

**1. Basamak (Ocak)**

| Oturum | Sorular | Cevap Anahtari |
|--------|---------|----------------|
| 1. Oturum | [KGS_2025_1.Basamak_1.Oturum_Sorular.pdf](2025/1.Basamak/KGS_2025_1.Basamak_1.Oturum_Sorular.pdf) | [KGS_2025_1.Basamak_1.Oturum_Cevap.jpg](2025/1.Basamak/KGS_2025_1.Basamak_1.Oturum_Cevap.jpg) |
| 2. Oturum | [KGS_2025_1.Basamak_2.Oturum_Sorular.pdf](2025/1.Basamak/KGS_2025_1.Basamak_2.Oturum_Sorular.pdf) | [KGS_2025_1.Basamak_2.Oturum_Cevap.jpg](2025/1.Basamak/KGS_2025_1.Basamak_2.Oturum_Cevap.jpg) |

**2. Basamak (Haziran)**

| Oturum | Sorular | Cevap Anahtari |
|--------|---------|----------------|
| 1. Oturum | [KGS_2025_2.Basamak_1.Oturum_Sorular.pdf](2025/2.Basamak/KGS_2025_2.Basamak_1.Oturum_Sorular.pdf) | [KGS_2025_2.Basamak_1.Oturum_Cevap.pdf](2025/2.Basamak/KGS_2025_2.Basamak_1.Oturum_Cevap.pdf) |
| 2. Oturum | [KGS_2025_2.Basamak_2.Oturum_Sorular.pdf](2025/2.Basamak/KGS_2025_2.Basamak_2.Oturum_Sorular.pdf) | [KGS_2025_2.Basamak_2.Oturum_Cevap.pdf](2025/2.Basamak/KGS_2025_2.Basamak_2.Oturum_Cevap.pdf) |

### 2026

**1. Basamak (Ocak)**

| Oturum | Sorular | Cevap Anahtari |
|--------|---------|----------------|
| 1. Oturum | [KGS_2026_1.Basamak_1.Oturum_Sorular.pdf](2026/1.Basamak/KGS_2026_1.Basamak_1.Oturum_Sorular.pdf) | [KGS_2026_1.Basamak_1.Oturum_Cevap.pdf](2026/1.Basamak/KGS_2026_1.Basamak_1.Oturum_Cevap.pdf) |
| 2. Oturum | [KGS_2026_1.Basamak_2.Oturum_Sorular.pdf](2026/1.Basamak/KGS_2026_1.Basamak_2.Oturum_Sorular.pdf) | [KGS_2026_1.Basamak_2.Oturum_Cevap.pdf](2026/1.Basamak/KGS_2026_1.Basamak_2.Oturum_Cevap.pdf) |

**2. Basamak (Haziran)**

| Oturum | Sorular | Cevap Anahtari |
|--------|---------|----------------|
| 1. Oturum | [KGS_2026_2.Basamak_1.Oturum_Sorular.pdf](2026/2.Basamak/KGS_2026_2.Basamak_1.Oturum_Sorular.pdf) | [KGS_2026_2.Basamak_1.Oturum_Cevap.pdf](2026/2.Basamak/KGS_2026_2.Basamak_1.Oturum_Cevap.pdf) |
| 2. Oturum | [KGS_2026_2.Basamak_2.Oturum_Sorular.pdf](2026/2.Basamak/KGS_2026_2.Basamak_2.Oturum_Sorular.pdf) | [KGS_2026_2.Basamak_2.Oturum_Cevap.pdf](2026/2.Basamak/KGS_2026_2.Basamak_2.Oturum_Cevap.pdf) |

## Ek Kaynaklar

- [2025 KGS Kilavuz Kitapcigi](_Kaynak_Kilavuz/KGS_2025_Kilavuz_Kitapcigi.pdf)

## Notlar / Eksikler

- Bazi yil ve oturumlara ait dosyalar henuz arsivde bulunmamaktadir (ornegin 1. Basamak 2019, 2. Basamak 2021).
- _Kontrol_Belirsiz/ klasorundeki dosyalar (KGS2024_1.pdf, KGS22024_2.pdf) kaynagi/yili kesin dogrulanamamis tarama dosyalaridir; gorsel olarak teyit edildikten sonra ilgili yil klasorune tasinabilir.
- Eksik dosyalar genellikle [MEB KKTC Duyurular](https://www.mebnet.net/MEBDuyurular) sayfasindan temin edilebilir.

## Kaynak

Dokumanlarin orijinal kaynagi: **KKTC Milli Egitim Bakanligi** - <https://www.mebnet.net/MEBDuyurular>

## Lisans / Sorumluluk Reddi

Bu arsivdeki sinav ve cevap anahtarlari KKTC Milli Egitim Bakanligi'na ait kamuya acik dokumanlardir ve yalnizca **egitim amacli** paylasilmaktadir. Tum telif haklari ilgili kuruma aittir. Bu depo resmi bir kaynak degildir.
