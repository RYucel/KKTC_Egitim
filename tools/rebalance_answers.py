# -*- coding: utf-8 -*-
"""Seçenek sıralarını karıştırarak doğru cevap harfini A-D arasında dengeler.

Çoktan seçmeli soru bankasında doğru cevaplar tek bir harfte (ör. A) toplanırsa
öğrenci ezbere o harfi işaretleyip yüksek puan alabilir. Bu betik her sorunun
seçeneklerini (içeriği koruyarak) yeniden sıralar ve 'answer' alanını günceller.
'Hiçbiri/Hepsi' içeren sorular dokunulmadan bırakılır.

Kullanım: python tools/rebalance_answers.py   (dosyaları yerinde günceller)
Tekrar çalıştırılabilir; sonuç seed'e bağlı olduğundan kararlıdır.
"""
import json
import os
import random
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUBJECTS = ["matematik", "fen", "sosyal", "turkce"]
LETTERS = "ABCD"
SKIP = re.compile(r"hi[çc]biri|hepsi", re.I)


def rebalance(questions, rnd):
    for q in questions:
        opts = q["options"]
        if SKIP.search(" ".join(opts)):
            continue
        correct_text = opts[LETTERS.index(q["answer"])]
        order = opts[:]
        rnd.shuffle(order)
        q["options"] = order
        q["answer"] = LETTERS[order.index(correct_text)]


def main():
    # dağılım dengeli olana kadar farklı seed dene
    for seed in range(1, 200):
        data = {}
        rnd = random.Random(seed)
        counts = {l: 0 for l in LETTERS}
        for s in SUBJECTS:
            with open(os.path.join(ROOT, "data", "questions", s + ".json"), encoding="utf-8") as f:
                data[s] = json.load(f)
            rebalance(data[s]["questions"], rnd)
            for q in data[s]["questions"]:
                counts[q["answer"]] += 1
        total = sum(counts.values())
        # her harf %20-%30 arasında olsun
        if all(0.20 * total <= counts[l] <= 0.30 * total for l in LETTERS):
            for s in SUBJECTS:
                path = os.path.join(ROOT, "data", "questions", s + ".json")
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data[s], f, ensure_ascii=False, indent=2)
                    f.write("\n")
            print(f"seed={seed} ile dengelendi. Dağılım:",
                  "  ".join(f"{l}:{counts[l]}" for l in LETTERS), f"(toplam {total})")
            return
    print("Dengeli dağılım bulunamadı (seed 1-199).")
    sys.exit(1)


if __name__ == "__main__":
    main()
