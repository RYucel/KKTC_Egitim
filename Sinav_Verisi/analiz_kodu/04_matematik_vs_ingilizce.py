#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
04_matematik_vs_ingilizce.py — Aynı 2. Oturum kitapçığında İngilizce ve Matematik
yükünü birebir aynı yöntemle ölçer. "İngilizce şişerken Matematik sabit kaldı"
tezinin doğrudan kontrolü.

Matematik için kelime, rakam (sayı), operatör sembolü ve karakter sayısı ölçülür.
DİKKAT: Geometri/şekil soruları görsel olduğundan metne yansımaz; bu, Matematiğin
KAVRAMSAL zorluğunu değil METİN+SEMBOL yükünü ölçer.

Çıktı: cikti/veri/matematik_oturum.json
"""
import json, re
import ortak

NUM  = re.compile(r"\d")
SEMB = set("+-−×÷*/=<>≤≥≠√%²³·∙πø°∠")  # matematik operatörleri (yaklaşık küme)

def yuk(t):
    kel = ortak.kelimeler(t)
    tok = t.split()
    return {
        "kelime": len(kel),
        "sayi": sum(1 for x in tok if NUM.search(x)),
        "sembol": sum(1 for c in t if c in SEMB),
        "karakter": len(re.sub(r"\s", "", t)),
    }

def main():
    satir = []
    for pdf in ortak.pdf_listesi("*/*/KGS_*_2.Oturum_Sorular.pdf"):
        yil, bas, _ = ortak.yil_basamak(pdf)
        en = ortak.bolum_metni(pdf, ortak.ING_BAS, ortak.ING_BIT, ortak.H_ING)
        mt = ortak.bolum_metni(pdf, ortak.MAT_BAS, ortak.MAT_BIT, ortak.H_MAT, bas_sonra=True)
        if en and mt:
            e = yuk(en); m = yuk(mt)
            satir.append({
                "yil": yil, "basamak": bas,
                "ing_soz_soru": round(e["kelime"] / 22, 1),
                "ing_karakter": e["karakter"],
                "mat_soz_soru": round(m["kelime"] / 27, 1),
                "mat_sayi": m["sayi"],
                "mat_sembol": m["sembol"],
                "mat_karakter": m["karakter"],
            })
    json.dump(satir, open(ortak.VERI / "matematik_oturum.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"✓ matematik_oturum.json yazıldı ({len(satir)} kitapçık).")

if __name__ == "__main__":
    main()
