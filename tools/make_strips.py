# -*- coding: utf-8 -*-
"""Build one verification strip per answer sheet: each detected block is
cropped and pasted side by side with the detected letters drawn next to
each row, for fast visual checking."""
import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))

import glob
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from detect_keys import detect

OUT = _os.path.join(ROOT, r"_work\strips")

def strip_for(path):
    arr, results, rings = detect(path)
    if not results:
        return None
    img = Image.fromarray(arr.astype(np.uint8))
    scale = img.width / 1653.0
    pads = int(40 * scale)
    crops = []
    for blk in results:
        bcols = blk["pts"][0][0]
        ys = [p[1] for p in blk["pts"]]
        x0 = int(min(bcols) - pads)
        x1 = int(max(bcols) + 2.6 * pads)
        y0 = int(min(ys) - pads)
        y1 = int(max(ys) + pads)
        crop = img.crop((max(x0, 0), max(y0, 0), x1, y1)).convert("RGB")
        d = ImageDraw.Draw(crop)
        try:
            font = ImageFont.truetype("arialbd.ttf", int(26 * scale))
        except Exception:
            font = None
        for j, (bc, ry, dx, letter) in enumerate(blk["pts"]):
            d.text((max(bc) - x0 + int(28 * scale), ry - y0 - int(14 * scale)),
                   f"{j+1}{letter}", fill=(200, 0, 0), font=font)
        crops.append(crop)
    hmax = max(c.height for c in crops)
    wtot = sum(c.width for c in crops) + 10 * len(crops)
    sheet = Image.new("RGB", (wtot, hmax), (255, 255, 255))
    x = 0
    for c in crops:
        sheet.paste(c, (x, 0))
        x += c.width + 10
    # normalize height ~1500 for readability
    if hmax > 1600:
        f = 1600.0 / hmax
        sheet = sheet.resize((int(sheet.width * f), 1600), Image.LANCZOS)
    return sheet

def main():
    os.makedirs(OUT, exist_ok=True)
    paths = []
    for pat in (_os.path.join(ROOT, r"20*\*\*Cevap*.pdf"),
                _os.path.join(ROOT, r"20*\*\*Cevap*.jpg")):
        paths.extend(sorted(glob.glob(pat)))
    if len(sys.argv) > 1:
        paths = [p for p in paths if any(a in p for a in sys.argv[1:])]
    for p in paths:
        name = os.path.splitext(os.path.basename(p))[0]
        s = strip_for(p)
        if s is None:
            print(name, "NO BLOCKS")
            continue
        s.save(os.path.join(OUT, name + "_strip.png"))
        print(name, s.size)

if __name__ == "__main__":
    main()
