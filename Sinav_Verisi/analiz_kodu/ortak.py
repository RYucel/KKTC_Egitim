#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ortak.py — Tüm analiz betiklerinin paylaştığı yardımcı işlevler.

İçerik:
  - PDF metin çıkarımı (PyMuPDF)
  - Karakter normalizasyonu (ligatür + eski PDF'lerdeki bozuk kodlama/mojibake)
  - Bölüm izolasyonu (TÜRKÇE / İNGİLİZCE / MATEMATİK bölümlerini ayırma)
  - Kelime tokenizasyonu

Repo kökü, betiklerin konumuna göre otomatik bulunur:
  analiz_kodu/ -> Sinav_Verisi/ -> KKTC_Egitim/  (üç üst klasör)
İstenirse KKTC_REPO ortam değişkeniyle elle belirtilebilir.
"""
from pathlib import Path
import os, re
import fitz  # PyMuPDF

# --- Yollar ---
REPO_KOK = Path(os.environ.get("KKTC_REPO", Path(__file__).resolve().parents[2]))
GIRDI   = Path(__file__).resolve().parent / "girdi"     # elle girilen veri (ör. sonuç CSV'si)
CIKTI   = Path(__file__).resolve().parent / "cikti"     # üretilen çıktılar
VERI    = CIKTI / "veri"                                 # ara JSON dosyaları
GRAFIK  = CIKTI / "grafikler"                            # üretilen grafikler
for _d in (CIKTI, VERI, GRAFIK):
    _d.mkdir(parents=True, exist_ok=True)

# --- Karakter düzeltmeleri ---
# Ligatürler tek karaktere indirgenir (kelime bütünlüğü korunur).
# 2018-2020 PDF'lerinde Türkçe karakterler bozuk (mojibake); bu harfler doğru
# Türkçe metinde geçmediğinden düzeltmeyi evrensel uygulamak güvenlidir.
_DUZELT = {
    "\ufb01": "fi", "\ufb02": "fl", "\ufb00": "ff", "\ufb03": "ffi", "\ufb04": "ffl",
    "Ý": "İ", "ý": "ı", "þ": "ş", "Þ": "Ş", "ð": "ğ", "Ð": "Ğ",
    "\u2019": "'", "\u2018": "'",
}
def normalize(t: str) -> str:
    for k, v in _DUZELT.items():
        t = t.replace(k, v)
    return t

# --- Bölüm işaretçileri (regex) ---
ING_BAS = re.compile(r"İNGİLİZCE\s*TESTİ")
ING_BIT = re.compile(r"İNGİLİZCE\s*TEST.*BİTMİŞ")
TUR_BAS = re.compile(r"TÜRKÇE\s*TESTİ")
TUR_BIT = re.compile(r"TÜRKÇE\s*TEST.*BİTMİŞ")
MAT_BAS = re.compile(r"MATEMATİK\s*TESTİ")
MAT_BIT = re.compile(r"BİTMİŞ")                  # Matematik için: başlangıçtan SONRA aranır
H_ING = re.compile(r"^\s*İNGİLİZCE\s*TESTİ\s*$", re.I)
H_TUR = re.compile(r"^\s*TÜRKÇE\s*TESTİ\s*$", re.I)
H_MAT = re.compile(r"^\s*MATEMATİK\s*TESTİ.*$", re.I)

_SAYFA = re.compile(r"^\s*\d{1,3}\s*$")           # tek başına sayfa numarası
_ENUM  = re.compile(r"^\s*(\d{1,2}|[A-Da-d])\s*[\)\.]\s*")  # satır başı "1)" "A)" işaretçileri

def pdf_satirlar(pdf) -> list:
    """PDF'in tüm metnini normalize edip satırlara böler."""
    d = fitz.open(pdf)
    s = normalize("\n".join(p.get_text() for p in d))
    d.close()
    return s.split("\n")

def bolum_metni(pdf, bas_re, bit_re, baslik_re, bas_sonra=False):
    """
    bas_re (bölüm başlığı) ile bit_re (bölüm bitişi) arasındaki gövdeyi döndürür.
    Tekrarlayan sayfa başlıkları, sayfa numaraları ve şık/soru işaretçileri temizlenir.
    bas_sonra=True ise bitiş, başlangıçtan SONRA aranır (Matematik bölümü için gerekli,
    çünkü İngilizce bitişi Matematik başlangıcından öncedir).
    """
    lines = pdf_satirlar(pdf)
    s = e = None
    for i, l in enumerate(lines):
        if s is None and bas_re.search(l):
            s = i
        if s is not None and (not bas_sonra or i > s) and bit_re.search(l):
            e = i
            break
    if s is None:
        return None
    if e is None:
        e = len(lines)
    govde = [l.replace("\f", " ") for l in lines[s + 1:e]
             if not baslik_re.match(l) and not _SAYFA.match(l)]
    return "\n".join(_ENUM.sub("", x) for x in govde)

def pdf_listesi(desen: str) -> list:
    """Repo kökünden glob deseniyle PDF'leri sıralı döndürür."""
    return sorted(REPO_KOK.glob(desen))

def yil_basamak(pdf):
    """Dosya adından (yıl, basamak, oturum) çıkarır."""
    m = re.search(r"KGS_(\d{4})_(\d)\.Basamak_(\d)\.Oturum", str(pdf))
    return int(m.group(1)), int(m.group(2)), int(m.group(3))

# --- Kelime tokenizasyonu ---
# En az bir harf içeren diziler; tek harflik A-D şık etiketleri elenir.
KELIME_RE = re.compile(r"[A-Za-zÇĞİıÖŞÜçğöşüâîûÂÎÛ]+(?:'[A-Za-zÇĞİıÖŞÜçğöşüâîû]+)?")
def kelimeler(metin: str) -> list:
    return [w for w in KELIME_RE.findall(metin) if not (len(w) == 1 and w.upper() in "ABCD")]

# Sabit soru sayıları (kapak sayfaları ve exams.json ile teyitli)
SORU_SAYISI = {"İngilizce": 22, "Türkçe": 27, "Matematik": 27}

if __name__ == "__main__":
    print("Repo kökü:", REPO_KOK)
    print("Bulunan soru kitapçığı sayısı:", len(pdf_listesi("*/*/KGS_*_Sorular.pdf")))
