# -*- coding: utf-8 -*-
"""Decoder for the 2026-style pale KGS answer sheets (no printed rings):
detect dark pencil marks, cluster x into option columns, group into
4-column blocks, rows = sorted mark positions."""
import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))

import glob
import os
import sys

import numpy as np
import pymupdf
from PIL import Image
from scipy import ndimage

def decode(path):
    doc = pymupdf.open(path)
    pix = doc[0].get_pixmap(dpi=200)
    arr = np.asarray(Image.frombytes("RGB", (pix.width, pix.height), pix.samples)).astype(int)
    h, w, _ = arr.shape
    scale = w / 1653.0
    gray = arr.mean(axis=2)
    dark = gray < 185
    lab, n = ndimage.label(dark)
    objs = ndimage.find_objects(lab)
    blobs = []
    for i, sl in enumerate(objs):
        ys, xs = sl
        bh, bw = ys.stop - ys.start, xs.stop - xs.start
        if not (13 * scale <= bw <= 36 * scale and 13 * scale <= bh <= 36 * scale):
            continue
        if not (0.6 <= bw / bh <= 1.6):
            continue
        area = int((lab[sl] == i + 1).sum())
        if area / (bw * bh) < 0.5 or area < 110 * scale * scale:
            continue
        cy, cx = ys.start + bh / 2.0, xs.start + bw / 2.0
        if cx > w * 0.735 or cy < h * 0.15:
            continue
        blobs.append((cx, cy))

    # cluster x into option columns
    xs_ = sorted(b[0] for b in blobs)
    cols = [[xs_[0]]]
    for x in xs_[1:]:
        if x - np.mean(cols[-1]) <= 16 * scale:
            cols[-1].append(x)
        else:
            cols.append([x])
    centers = [float(np.mean(c)) for c in cols]
    # column spacing = median small gap
    gaps = np.diff(centers)
    small = [g for g in gaps if 20 * scale < g < 90 * scale]
    s = float(np.median(small)) if small else 67 * scale
    # group into blocks: gap > 1.8*s starts new block
    blocks = [[centers[0]]]
    for c in centers[1:]:
        if c - blocks[-1][-1] <= 1.8 * s:
            blocks[-1].append(c)
        else:
            blocks.append([c])

    out = []
    for bc in blocks:
        bb = [b for b in blobs if bc[0] - s <= b[0] <= bc[-1] + s]
        if len(bb) < 8:
            continue
        # reconstruct 4-col lattice: try anchoring so all cols snap
        # candidate lattices: start at bc[0] - k*s for k in 0..3
        best = None
        for k in range(4):
            lat = [bc[0] + (i - k) * s for i in range(4)]
            err = 0.0
            ok = True
            for c in bc:
                d = min(abs(c - L) for L in lat)
                err += d
                if d > 0.35 * s:
                    ok = False
            if ok and (best is None or err < best[1]):
                best = (lat, err)
        if best is None:
            out.append({"cols": bc, "n": len(bb), "key": "?", "note": "no lattice"})
            continue
        lat = best[0]
        ys2 = sorted(b[1] for b in bb)
        rows = [[ys2[0]]]
        for y in ys2[1:]:
            if y - rows[-1][-1] <= 14 * scale:
                rows[-1].append(y)
            else:
                rows.append([y])
        key = []
        warns = []
        for ri, g in enumerate(rows):
            ry = float(np.mean(g))
            rmarks = [b for b in bb if abs(b[1] - ry) <= 14 * scale]
            if len(rmarks) != 1:
                warns.append((ri + 1, f"{len(rmarks)} marks"))
            ci = min(range(4), key=lambda i: abs(lat[i] - rmarks[0][0]))
            key.append("ABCD"[ci])
        gaps2 = np.diff([float(np.mean(g)) for g in rows])
        med = float(np.median(gaps2)) if len(gaps2) else 0
        for i, gp in enumerate(gaps2):
            if med and gp > 1.5 * med:
                warns.append((i + 2, f"row gap {round(gp)} vs {round(med)}"))
        out.append({"cols": [round(c) for c in lat], "n": len(rows),
                    "key": "".join(key), "warns": warns,
                    "rows": [float(np.mean(g)) for g in rows]})
    return out

def make_crops(outdir):
    from PIL import ImageDraw, ImageFont
    os.makedirs(outdir, exist_ok=True)
    for f in sorted(glob.glob(_os.path.join(ROOT, r"2026\*\*Cevap*.pdf"))):
        doc = pymupdf.open(f)
        pix = doc[0].get_pixmap(dpi=200)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        name = os.path.splitext(os.path.basename(f))[0]
        try:
            font = ImageFont.truetype("arialbd.ttf", 40)
        except Exception:
            font = None
        for bi, blk in enumerate(decode(f)):
            cols, rows, key = blk["cols"], blk["rows"], blk["key"]
            x0, x1 = int(cols[0] - 45), int(cols[3] + 100)
            y0, y1 = int(rows[0] - 45), int(rows[-1] + 45)
            c = img.crop((x0, y0, x1, y1))
            c = c.resize((c.width * 2, c.height * 2), Image.LANCZOS)
            d = ImageDraw.Draw(c)
            for j, ry in enumerate(rows):
                d.text(((cols[3] - x0 + 30) * 2, (ry - y0) * 2 - 22),
                       f"{j+1}{key[j]}", fill=(0, 130, 0), font=font)
            out = os.path.join(outdir, f"{name}_b{bi}.png")
            c.save(out)
            print(out.split(os.sep)[-1], c.size)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "crops":
        make_crops(_os.path.join(ROOT, r"_work\blockcrops"))
    else:
        for f in sorted(glob.glob(_os.path.join(ROOT, r"2026\*\*Cevap*.pdf"))):
            print(os.path.basename(f))
            for blk in decode(f):
                print("  ", {k: blk[k] for k in ("cols", "n", "key", "warns")})

