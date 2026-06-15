#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
02_kelime_cesitliligi.py — İngilizce (2. Basamak) bölümlerinde kelime çeşitliliği
ve nadirlik. "Daha çok kelime" mi yoksa "daha çok farklı/zor kelime" mi sorusunu test eder.

Ölçütler: token, farklı kelime (tip), ortalama Zipf sıklığı, ileri/nadir kelime
sayısı ve oranı. Kelimeler pyspellchecker sözlüğüyle doğrulanır (çıkarma
parçacıkları — 'ght', 'rou' vb. — elenir); nadirlik wordfreq Zipf ile ölçülür.

Çıktı: cikti/veri/kelime_cesitliligi.json
"""
import json, re
import numpy as np
from wordfreq import zipf_frequency
from spellchecker import SpellChecker
import ortak

SOZLUK = SpellChecker().word_frequency.dictionary  # gerçek İngilizce kelimeler
EN_RE  = re.compile(r"[a-z]+(?:'[a-z]+)?")

def gecerli(w):
    """Gerçek İngilizce kelime mi? (sözlük) — kesme'li kısaltmalar köküyle denetlenir."""
    if "'" in w:
        return w.split("'")[0] in SOZLUK or w in SOZLUK
    return w in SOZLUK

def tokenize(t):
    return [w for w in EN_RE.findall(t.lower()) if gecerli(w)]

def metrik(t):
    tok = tokenize(t)
    tip = set(tok); T = len(tip)
    z = np.array([zipf_frequency(w.split("'")[0], "en") for w in tip])  # Zipf düşük = nadir
    say = lambda esik: int((z < esik).sum())
    return {
        "token": len(tok),
        "farkli": T,
        "ort_zipf": round(float(z.mean()), 3),
        "ileri_4.0": say(4.0),
        "ileri_4.0_oran": round(say(4.0) / T * 100, 1),
        "nadir_3.5": say(3.5),
        "nadir_3.5_oran": round(say(3.5) / T * 100, 1),
        "cok_nadir_3.0": say(3.0),
    }

def main():
    veri = {}
    for pdf in ortak.pdf_listesi("*/2.Basamak/KGS_*_2.Oturum_Sorular.pdf"):
        yil, _, _ = ortak.yil_basamak(pdf)
        t = ortak.bolum_metni(pdf, ortak.ING_BAS, ortak.ING_BIT, ortak.H_ING)
        if t:
            veri[yil] = metrik(t)
    json.dump(veri, open(ortak.VERI / "kelime_cesitliligi.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"✓ kelime_cesitliligi.json yazıldı ({len(veri)} yıl).")

if __name__ == "__main__":
    main()
