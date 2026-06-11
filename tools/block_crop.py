# -*- coding: utf-8 -*-
"""Crop one detected block of an answer sheet at 2x zoom with detected
letters drawn, for detailed visual verification.
Usage: block_crop.py <file-substring> <block-index 0..2>"""
import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))

import glob
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from detect_keys import detect_best

OUT = _os.path.join(ROOT, r"_work\blockcrops")

def main(substr, bi):
    paths = []
    for pat in (_os.path.join(ROOT, r"20*\*\*Cevap*.pdf"),
                _os.path.join(ROOT, r"20*\*\*Cevap*.jpg")):
        paths.extend(sorted(glob.glob(pat)))
    path = next(p for p in paths if substr in p)
    arr, results, rings, rotated = detect_best(path)
    blk = results[bi]
    img = Image.fromarray(arr.astype(np.uint8)).convert("RGB")
    scale = img.width / 1653.0
    bcols = blk["pts"][0][0]
    ys = [p[1] for p in blk["pts"]]
    pad = int(45 * scale)
    x0, x1 = int(min(bcols) - pad), int(max(bcols) + 2.4 * pad)
    y0, y1 = int(min(ys) - pad), int(max(ys) + pad)
    crop = img.crop((max(x0, 0), max(y0, 0), x1, y1))
    f = 2.0 if scale < 1.2 else 1.4
    crop = crop.resize((int(crop.width * f), int(crop.height * f)), Image.LANCZOS)
    d = ImageDraw.Draw(crop)
    try:
        font = ImageFont.truetype("arialbd.ttf", int(20 * scale * f))
    except Exception:
        font = None
    for j, (bc, ry, dx, letter) in enumerate(blk["pts"]):
        d.text(((max(bc) - x0 + 26 * scale) * f, (ry - y0) * f - 12 * scale * f),
               f"{j+1}{letter}", fill=(0, 120, 0), font=font)
    os.makedirs(OUT, exist_ok=True)
    name = os.path.splitext(os.path.basename(path))[0]
    out = os.path.join(OUT, f"{name}_b{bi}.png")
    crop.save(out)
    print(out, crop.size)

if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]))
