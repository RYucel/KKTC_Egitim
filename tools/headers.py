# -*- coding: utf-8 -*-
"""Stack the subject-header strip of every detected block into one image."""
import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))

import glob
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from detect_keys import detect_best

def main():
    paths = []
    for pat in (_os.path.join(ROOT, r"20*\*\*Cevap*.pdf"),
                _os.path.join(ROOT, r"20*\*\*Cevap*.jpg")):
        paths.extend(sorted(glob.glob(pat)))
    rows = []
    try:
        font = ImageFont.truetype("arialbd.ttf", 18)
    except Exception:
        font = None
    for p in paths:
        name = os.path.splitext(os.path.basename(p))[0].replace("KGS_", "").replace("_Cevap", "")
        try:
            arr, results, rings, rot = detect_best(p)
        except Exception:
            continue
        if not results:
            continue
        img = Image.fromarray(arr.astype(np.uint8)).convert("RGB")
        scale = img.width / 1653.0
        strips = []
        for blk in results:
            bcols = blk["pts"][0][0]
            y1 = min(pt[1] for pt in blk["pts"])
            x0 = int(min(bcols) - 50 * scale)
            x1 = int(max(bcols) + 40 * scale)
            s = img.crop((max(x0, 0), max(int(y1 - 95 * scale), 0),
                          x1, int(y1 - 18 * scale)))
            f = 300.0 / s.width
            s = s.resize((300, max(int(s.height * f), 24)), Image.LANCZOS)
            strips.append(s)
        hh = max(s.height for s in strips)
        row = Image.new("RGB", (330 + 310 * len(strips), hh + 6), (255, 255, 255))
        d = ImageDraw.Draw(row)
        d.text((4, hh // 2 - 8), f"{name} n={[b['n'] for b in results]}",
               fill=(0, 0, 0), font=font)
        x = 330
        for s in strips:
            row.paste(s, (x, 3))
            x += 310
        rows.append(row)
    wtot = max(r.width for r in rows)
    htot = sum(r.height for r in rows)
    sheet = Image.new("RGB", (wtot, htot), (230, 230, 230))
    y = 0
    for r in rows:
        sheet.paste(r, (0, y))
        y += r.height
    out = _os.path.join(ROOT, r"_work\headers_all.png")
    sheet.save(out)
    print(out, sheet.size)

if __name__ == "__main__":
    main()
