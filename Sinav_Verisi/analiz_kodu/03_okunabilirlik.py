#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
03_okunabilirlik.py — İngilizce (2. Basamak) bölümlerinin okunabilirlik endeksleri:
Flesch Reading Ease, Flesch-Kincaid sınıf seviyesi, Gunning Fog ve tahmini okuma süresi.

Not: Okunabilirlik endeksleri YOĞUNLUK (per-cümle/per-kelime) ölçer; HACİM içermez.
Okuma süresi = kelime / 130 (L2 dikkatli okuma hızı varsayımı) hacmi yansıtan
basit bir bileşik ölçüttür.

Çıktı: cikti/veri/okunabilirlik.json
"""
import json, re
import textstat
import ortak

DOT = re.compile(r"\.{2,}|…|_{2,}")
OKUMA_HIZI = 130  # kelime/dk — varsayım (mutlak süreyi etkiler, yıllar arası ARTIŞI etkilemez)

def main():
    veri = {}
    for pdf in ortak.pdf_listesi("*/2.Basamak/KGS_*_2.Oturum_Sorular.pdf"):
        yil, _, _ = ortak.yil_basamak(pdf)
        t = ortak.bolum_metni(pdf, ortak.ING_BAS, ortak.ING_BIT, ortak.H_ING)
        if not t:
            continue
        t = re.sub(r"[ \t]+", " ", DOT.sub(" ", t))  # doldurma noktaları temizlenir
        wc = textstat.lexicon_count(t, removepunct=True)
        veri[yil] = {
            "flesch_re": round(textstat.flesch_reading_ease(t), 1),   # yüksek = kolay
            "fk_sinif": round(textstat.flesch_kincaid_grade(t), 1),
            "fog": round(textstat.gunning_fog(t), 1),
            "kelime": wc,
            "hece": textstat.syllable_count(t),
            "okuma_dk": round(wc / OKUMA_HIZI, 1),
        }
    json.dump(veri, open(ortak.VERI / "okunabilirlik.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"✓ okunabilirlik.json yazıldı ({len(veri)} yıl).")

if __name__ == "__main__":
    main()
