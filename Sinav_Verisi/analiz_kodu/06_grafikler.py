#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
06_grafikler.py — Üretilen JSON verilerinden 6 grafik oluşturur (cikti/grafikler/).
01-05 numaralı betikler önce çalıştırılmış olmalıdır.
"""
import json, csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import defaultdict
import ortak

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.titlesize": 14, "axes.titleweight": "bold",
    "axes.edgecolor": "#888", "axes.grid": True, "grid.color": "#E5E5E5",
    "figure.dpi": 150, "savefig.dpi": 150, "savefig.bbox": "tight",
})
EN, TR, MAT, FEN, SOS, GREY = "#1F6FB2", "#C0392B", "#E67E22", "#27AE60", "#8E44AD", "#9AA0A6"
SRC = "Kaynak: KKTC_Egitim deposu · KGS soru kitapçıkları (2016–2026)"
YEARS = list(range(2016, 2027))

def footer(fig, txt=SRC):
    fig.text(0.01, -0.02, txt, fontsize=8, color="#888", ha="left")

def yukle():
    metr = json.load(open(ortak.VERI / "metrikler.json", encoding="utf-8"))
    oku = {int(k): v for k, v in json.load(open(ortak.VERI / "okunabilirlik.json", encoding="utf-8")).items()}
    mat = json.load(open(ortak.VERI / "matematik_oturum.json", encoding="utf-8"))
    rows = list(csv.DictReader(open(ortak.GIRDI / "tmk_cee2_sonuclari.csv", encoding="utf-8")))
    return metr, oku, mat, rows

def yillik(metr, ders, alan):
    ag = defaultdict(list)
    for r in metr:
        if r["ders"] == ders:
            ag[r["yil"]].append(r[alan])
    return {y: float(np.mean(v)) for y, v in ag.items()}

def main():
    metr, oku, mat, rows = yukle()

    # --- 1. Okuma yükü trendi (TR vs EN, yıllık ortalama kelime) ---
    tr = yillik(metr, "Türkçe", "kelime"); en = yillik(metr, "İngilizce", "kelime")
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(YEARS, [tr.get(y, np.nan) for y in YEARS], "o-", color=TR, lw=2.5, ms=6, label="Türkçe (27 soru)")
    ax.plot(YEARS, [en.get(y, np.nan) for y in YEARS], "s-", color=EN, lw=2.5, ms=6, label="İngilizce (22 soru)")
    ax.set_title("Sınav Bölümlerinde Kelime Sayısı (Okuma Yükü), 2016–2026")
    ax.set_xlabel("Yıl"); ax.set_ylabel("Bölümdeki kelime sayısı")
    ax.set_ylim(0, 2100); ax.set_xticks(YEARS); ax.tick_params(axis="x", rotation=45)
    ax.legend(frameon=False, loc="center right")
    footer(fig); fig.savefig(ortak.GRAFIK / "01_okuma_yuku.png"); plt.close()

    # --- 2. İngilizce zorluk bileşenleri (endeks 2016=100) ---
    fig, ax = plt.subplots(figsize=(9, 5))
    baz = {k: yillik(metr, "İngilizce", k)[2016] for k in ("soz_soru", "cumle_uz", "mattr", "kelime_uz")}
    def idx(k):
        s = yillik(metr, "İngilizce", k)
        return [s.get(y, np.nan) / baz[k] * 100 for y in YEARS]
    ax.plot(YEARS, idx("soz_soru"), "o-", color=EN, lw=3, ms=6, label="Okuma hacmi (söz/soru)")
    ax.plot(YEARS, idx("cumle_uz"), "^--", color="#5B9BD5", lw=1.6, ms=5, label="Cümle uzunluğu")
    ax.plot(YEARS, idx("mattr"), "d--", color="#27AE60", lw=1.6, ms=5, label="Sözcük çeşitliliği (MATTR)")
    ax.plot(YEARS, idx("kelime_uz"), "v--", color=GREY, lw=1.6, ms=5, label="Kelime uzunluğu")
    ax.axhline(100, color="#bbb", lw=1, ls=":")
    ax.set_title("İngilizce: Zorluk Bileşenleri (2016 = 100)")
    ax.set_xlabel("Yıl"); ax.set_ylabel("2016'ya göre endeks")
    ax.set_xticks(YEARS); ax.tick_params(axis="x", rotation=45)
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    footer(fig); fig.savefig(ortak.GRAFIK / "02_ingilizce_neden.png"); plt.close()

    # Sonuç verileri (% başarı)
    MAKS = {"fen": 14, "matematik": 27, "sosyal": 10, "ingilizce": 22, "turkce": 27}
    yy = [int(r["yil"]) for r in rows]
    pct = {d: [float(r[d]) / MAKS[d] * 100 for r in rows] for d in MAKS}

    # --- 3. Ders bazında % başarı ---
    fig, ax = plt.subplots(figsize=(9, 5))
    for d, c, ad in [("fen", FEN, "Fen"), ("matematik", MAT, "Matematik"),
                     ("sosyal", SOS, "Sosyal"), ("turkce", TR, "Türkçe")]:
        ax.plot(yy, pct[d], "-", color=c, lw=1.4, alpha=0.55, label=ad)
    ax.plot(yy, pct["ingilizce"], "o-", color=EN, lw=3, ms=7, label="İngilizce", zorder=5)
    ax.set_title("Lefkoşa TMK CEE-2: Ders Bazında Başarı Oranı (%)")
    ax.set_xlabel("Yıl"); ax.set_ylabel("Doğru cevap oranı (%)")
    ax.set_xticks(yy); ax.tick_params(axis="x", rotation=45); ax.set_ylim(55, 95)
    ax.legend(frameon=False, ncol=5, fontsize=9, loc="lower center")
    footer(fig, "Kaynak: Lefkoşa TMK CEE-2 sonuçları · 2023 verisi yok")
    fig.savefig(ortak.GRAFIK / "03_ders_basari.png"); plt.close()

    # --- 4. Okuma yükü ↔ İngilizce başarısı (çift eksen) ---
    digerleri = np.mean([np.array(pct[d]) for d in ["fen", "matematik", "sosyal", "turkce"]], axis=0)
    rel = {yy[i]: np.array(pct["ingilizce"])[i] - digerleri[i] for i in range(len(yy))}
    wpq2 = {r["yil"]: r["soz_soru"] for r in metr if r["ders"] == "İngilizce" and r["basamak"] == 2}
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(YEARS, [wpq2.get(y, np.nan) for y in YEARS], "o-", color=EN, lw=2.8, ms=6, label="İngilizce okuma yükü (söz/soru)")
    ax.set_xlabel("Yıl"); ax.set_ylabel("Okuma yükü (söz/soru)", color=EN)
    ax.tick_params(axis="y", labelcolor=EN); ax.set_xticks(YEARS); ax.tick_params(axis="x", rotation=45)
    ax2 = ax.twinx(); ax2.grid(False)
    ax2.plot(YEARS, [rel.get(y, np.nan) for y in YEARS], "s--", color=TR, lw=2.8, ms=6, label="Kohort-arındırılmış başarı")
    ax2.set_ylabel("Kohort-arındırılmış İng. başarısı (puan)", color=TR); ax2.tick_params(axis="y", labelcolor=TR)
    ax.set_title("Okuma Yükü ↑  ↔  İngilizce Başarısı ↓   (r = −0,60)")
    l1, la1 = ax.get_legend_handles_labels(); l2, la2 = ax2.get_legend_handles_labels()
    ax.legend(l1 + l2, la1 + la2, frameon=False, fontsize=9, loc="lower left")
    footer(fig, "Kaynak: KGS 2. Basamak kitapçıkları + Lefkoşa TMK CEE-2 sonuçları")
    fig.savefig(ortak.GRAFIK / "04_yuk_vs_basari.png"); plt.close()

    # --- 5. Okunabilirlik: yapısal sabit, hacim arttı ---
    yrs = sorted(oku)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(yrs, [oku[y]["flesch_re"] for y in yrs], "o-", color="#27AE60", lw=2.6, ms=6, label="Flesch okunabilirlik (yüksek = kolay)")
    ax.set_ylim(0, 100); ax.set_ylabel("Flesch Reading Ease", color="#27AE60"); ax.tick_params(axis="y", labelcolor="#27AE60")
    ax.set_xlabel("Yıl"); ax.set_xticks(yrs); ax.tick_params(axis="x", rotation=45)
    ax.axhspan(80, 90, color="#27AE60", alpha=0.06)
    ax2 = ax.twinx(); ax2.grid(False)
    ax2.plot(yrs, [oku[y]["okuma_dk"] for y in yrs], "s--", color=EN, lw=2.6, ms=6, label="Tahmini okuma süresi")
    ax2.set_ylabel("Okuma süresi (dk)", color=EN); ax2.tick_params(axis="y", labelcolor=EN); ax2.set_ylim(0, 11)
    ax.set_title("Metnin Okunması Kolay Kaldı — Ama Miktarı Arttı")
    l1, la1 = ax.get_legend_handles_labels(); l2, la2 = ax2.get_legend_handles_labels()
    ax.legend(l1 + l2, la1 + la2, frameon=False, fontsize=9, loc="center left")
    footer(fig, "Kaynak: KGS 2. Basamak İngilizce bölümleri · okuma süresi = kelime/130")
    fig.savefig(ortak.GRAFIK / "05_okunabilirlik.png"); plt.close()

    # --- 6. Matematik vs İngilizce (aynı oturum) ---
    ag = defaultdict(lambda: defaultdict(list))
    for r in mat:
        ag[r["yil"]]["en"].append(r["ing_soz_soru"]); ag[r["yil"]]["mt"].append(r["mat_soz_soru"])
    ys = sorted(ag)
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(ys, [np.mean(ag[y]["en"]) for y in ys], "s-", color=EN, lw=3, ms=7, label="İngilizce (22 soru)")
    ax.plot(ys, [np.mean(ag[y]["mt"]) for y in ys], "o-", color=MAT, lw=3, ms=7, label="Matematik (27 soru)")
    ax.set_title("Aynı 2. Oturum: İngilizce Şişti, Matematik Şişmedi")
    ax.set_xlabel("Yıl"); ax.set_ylabel("Soru başına kelime"); ax.set_xticks(ys)
    ax.tick_params(axis="x", rotation=45); ax.set_ylim(20, 55)
    ax.legend(frameon=False, loc="upper left")
    footer(fig, "Kaynak: KGS 2. Oturum kitapçıkları · aynı kitapçıkta her iki ders aynı yöntemle ölçüldü")
    fig.savefig(ortak.GRAFIK / "06_matematik_vs_ingilizce.png"); plt.close()

    print("✓ 6 grafik üretildi (cikti/grafikler/).")

if __name__ == "__main__":
    main()
