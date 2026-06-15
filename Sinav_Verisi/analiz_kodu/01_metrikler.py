#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
01_metrikler.py — Türkçe (1. Oturum) ve İngilizce (2. Oturum) bölümleri için
temel dilbilimsel metrikler: kelime sayısı, soru başına kelime, ortalama cümle
uzunluğu, ortalama kelime uzunluğu ve MATTR (uzunluktan bağımsız sözcük çeşitliliği).

Çıktı: cikti/veri/metrikler.json
"""
import json, re
import numpy as np
import ortak

DOT  = re.compile(r"\.{2,}|…")     # noktalı doldurma çizgileri / üç nokta
ALT  = re.compile(r"_{2,}")        # boşluk doldurma
SENT = re.compile(r"[.!?]+")       # cümle sonu işaretleri

def metrik(metin, ders):
    kel = ortak.kelimeler(metin)
    n = len(kel)
    # Cümle sayısı: doldurma noktaları/çizgileri temizlenir, sonra cümle-sonu sayılır
    temiz = ALT.sub(" ", DOT.sub(" ", metin))
    nc = max(len([s for s in SENT.split(temiz) if ortak.KELIME_RE.search(s)]), 1)
    ort_kelime_uz = sum(len(w) for w in kel) / n if n else 0
    # MATTR: 100 kelimelik kayan pencere (10 adımla)
    tok = [w.lower() for w in kel]; W = 100
    if len(tok) >= W:
        mattr = float(np.mean([len(set(tok[i:i+W]))/W for i in range(0, len(tok)-W+1, 10)]))
    else:
        mattr = len(set(tok))/len(tok) if tok else 0
    return {
        "kelime": n,
        "soz_soru": round(n / ortak.SORU_SAYISI[ders], 1),
        "cumle_uz": round(n / nc, 1),
        "kelime_uz": round(ort_kelime_uz, 2),
        "mattr": round(mattr, 3),
    }

def main():
    sonuc = []
    for pdf in ortak.pdf_listesi("*/*/KGS_*_Sorular.pdf"):
        yil, bas, otur = ortak.yil_basamak(pdf)
        if otur == 1:  # Türkçe içerir
            t = ortak.bolum_metni(pdf, ortak.TUR_BAS, ortak.TUR_BIT, ortak.H_TUR)
            if t:
                sonuc.append({"yil": yil, "basamak": bas, "ders": "Türkçe", **metrik(t, "Türkçe")})
        if otur == 2:  # İngilizce içerir
            t = ortak.bolum_metni(pdf, ortak.ING_BAS, ortak.ING_BIT, ortak.H_ING)
            if t:
                sonuc.append({"yil": yil, "basamak": bas, "ders": "İngilizce", **metrik(t, "İngilizce")})
    json.dump(sonuc, open(ortak.VERI / "metrikler.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"✓ metrikler.json yazıldı ({len(sonuc)} kayıt).")

if __name__ == "__main__":
    main()
