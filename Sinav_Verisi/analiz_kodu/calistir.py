#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
calistir.py — Tüm analiz boru hattını sırayla çalıştırır.

Kullanım:
    python calistir.py

Repo başka bir konumdaysa:
    KKTC_REPO=/yol/KKTC_Egitim python calistir.py

Çıktılar cikti/ klasörüne yazılır: veri/ (JSON), grafikler/ (PNG) ve Excel dosyası.
"""
import runpy, sys
from pathlib import Path
import ortak

ADIMLAR = [
    "01_metrikler.py",
    "02_kelime_cesitliligi.py",
    "03_okunabilirlik.py",
    "04_matematik_vs_ingilizce.py",
    "05_sonuc_korelasyon.py",
    "06_grafikler.py",
    "07_excel.py",
]

def main():
    print(f"Repo kökü: {ortak.REPO_KOK}")
    kitapcik = len(ortak.pdf_listesi("*/*/KGS_*_Sorular.pdf"))
    if kitapcik == 0:
        print("HATA: Soru kitapçığı bulunamadı. KKTC_REPO yolunu kontrol edin.")
        sys.exit(1)
    print(f"{kitapcik} soru kitapçığı bulundu.\n" + "-" * 50)
    here = Path(__file__).resolve().parent
    for adim in ADIMLAR:
        print(f"\n▶ {adim}")
        runpy.run_path(str(here / adim), run_name="__main__")
    print("\n" + "=" * 50)
    print("✓ Tamamlandı. Çıktılar: cikti/")

if __name__ == "__main__":
    main()
