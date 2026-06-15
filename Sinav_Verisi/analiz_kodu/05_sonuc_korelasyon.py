#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
05_sonuc_korelasyon.py — Lefkoşa TMK CEE-2 sonuçlarını işler:
  - Her dersi % başarıya çevirir, yıl-trendini hesaplar.
  - İngilizceyi KOHORT-ARINDIRIR (her yıl diğer 4 dersin ortalamasını çıkararak,
    o yılki öğrenci kohortunun genel gücünü nötrler).
  - Kohort-arındırılmış İngilizce başarısı ile okuma yükü / kelime çeşitliliği /
    okunabilirlik ölçütleri arasındaki Pearson korelasyonlarını hesaplar.

Girdi: girdi/tmk_cee2_sonuclari.csv  +  cikti/veri/{metrikler,okunabilirlik,kelime_cesitliligi}.json
Çıktı: cikti/veri/korelasyonlar.json
"""
import csv, json
import numpy as np
import ortak

# Maksimum soru sayıları (ham puanları %'ye çevirmek için)
MAKS = {"fen": 14, "matematik": 27, "sosyal": 10, "ingilizce": 22, "turkce": 27}

def main():
    rows = list(csv.DictReader(open(ortak.GIRDI / "tmk_cee2_sonuclari.csv", encoding="utf-8")))
    yil = np.array([int(r["yil"]) for r in rows])
    pct = {d: np.array([float(r[d]) / MAKS[d] * 100 for r in rows]) for d in MAKS}
    digerleri = np.mean([pct[d] for d in ["fen", "matematik", "sosyal", "turkce"]], axis=0)
    kohort = {int(yil[i]): pct["ingilizce"][i] - digerleri[i] for i in range(len(yil))}

    print("Ders bazında % başarı ve yıl-trendi:")
    ders_trend = {}
    for d in MAKS:
        egim = float(np.polyfit(yil, pct[d], 1)[0])
        r = float(np.corrcoef(yil, pct[d])[0, 1])
        ders_trend[d] = {"ort_yuzde": round(float(pct[d].mean()), 1), "egim_yil": round(egim, 2), "r": round(r, 2)}
        print(f"  {d:>10}: ort %{pct[d].mean():5.1f}   eğim {egim:+.2f}/yıl   (r={r:+.2f})")

    # 2. Basamak İngilizce metrikleri (CEE-2 ile eşleşir)
    metr = json.load(open(ortak.VERI / "metrikler.json", encoding="utf-8"))
    wpq2 = {r["yil"]: r["soz_soru"] for r in metr if r["ders"] == "İngilizce" and r["basamak"] == 2}
    oku = {int(k): v for k, v in json.load(open(ortak.VERI / "okunabilirlik.json", encoding="utf-8")).items()}
    voc = {int(k): v for k, v in json.load(open(ortak.VERI / "kelime_cesitliligi.json", encoding="utf-8")).items()}

    eslesen = sorted(set(oku) & set(kohort) & set(wpq2))
    R = np.array([kohort[y] for y in eslesen])
    def kor(deger):
        X = np.array([deger[y] for y in eslesen])
        return round(float(np.corrcoef(X, R)[0, 1]), 2)

    korel = {
        "soz_soru_hacim":      kor(wpq2),
        "okuma_dk_hacim":      kor({y: oku[y]["okuma_dk"] for y in eslesen}),
        "ileri_kelime_oran":   kor({y: voc[y]["ileri_4.0_oran"] for y in eslesen}),
        "flesch_yapisal":      kor({y: oku[y]["flesch_re"] for y in eslesen}),
    }
    print(f"\nKohort-arındırılmış İngilizce başarısı ile korelasyon (n={len(eslesen)}):")
    aciklama = {"soz_soru_hacim": "Söz/Soru (hacim)", "okuma_dk_hacim": "Okuma süresi (hacim)",
                "ileri_kelime_oran": "İleri kelime oranı (normalize)", "flesch_yapisal": "Flesch (yapısal)"}
    for k, v in korel.items():
        print(f"  {aciklama[k]:>34}: r = {v:+.2f}")

    json.dump({
        "ders_trend": ders_trend,
        "kohort_arindirilmis": {str(k): round(v, 1) for k, v in kohort.items()},
        "korelasyonlar": korel,
        "eslesen_yillar": eslesen,
    }, open(ortak.VERI / "korelasyonlar.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("\n✓ korelasyonlar.json yazıldı.")

if __name__ == "__main__":
    main()
