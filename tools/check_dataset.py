# -*- coding: utf-8 -*-
"""Cross-check data/exams.json against a fresh OMR pass over every sheet."""
import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from detect_keys import detect_best
from decode_2026 import decode

ROOT = ROOT

EXPECT = {1: [27, 14, 10], 2: [22, 27]}

def detected_keys(exam):
    sheet = exam["answerSheet"]
    if not sheet:
        return None
    path = os.path.join(ROOT, sheet)
    if exam["year"] >= 2026:
        blocks = [b for b in decode(path) if b["n"] >= 9]
        return [b["key"] for b in blocks]
    _, results, _, _ = detect_best(path)
    keys = []
    for blk in results:
        k = blk["key"]
        # drop spurious leading rows (above the header) if count overshoots
        want = EXPECT[exam["oturum"]][len(keys)] if len(keys) < len(EXPECT[exam["oturum"]]) else None
        if want and blk["n"] == want + k.count("?") and k.startswith("?"):
            k = k.lstrip("?")
        keys.append(k)
    return keys

def main():
    with open(os.path.join(ROOT, "data", "exams.json"), encoding="utf-8") as f:
        data = json.load(f)
    bad = 0
    for exam in data["exams"]:
        if not exam["keys"]:
            print(exam["id"], "no key (expected)")
            continue
        stored = list(exam["keys"].values())
        if [len(k) for k in stored] != EXPECT[exam["oturum"]]:
            print(exam["id"], "BAD LENGTHS", [len(k) for k in stored])
            bad += 1
            continue
        try:
            det = detected_keys(exam)
        except Exception as e:
            print(exam["id"], "DETECT ERROR", repr(e))
            bad += 1
            continue
        if det is None or len(det) != len(stored):
            print(exam["id"], f"DETECT BLOCKS={len(det) if det else 0} (manual sheet?)")
            continue
        for i, (s, d) in enumerate(zip(stored, det)):
            if s == d:
                continue
            diffs = [(j + 1, a, b) for j, (a, b) in enumerate(zip(s, d)) if a != b]
            if len(s) != len(d):
                print(exam["id"], f"block{i} LENGTH stored={len(s)} det={len(d)}")
                bad += 1
            elif all(b == "?" for _, _, b in diffs):
                print(exam["id"], f"block{i} ok ({len(diffs)} undetected by OMR, stored kept)")
            else:
                print(exam["id"], f"block{i} MISMATCH at {diffs}")
                bad += 1
    print("DONE, hard mismatches:", bad)

if __name__ == "__main__":
    main()
