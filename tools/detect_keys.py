# -*- coding: utf-8 -*-
"""OMR detector for KGS optical answer-key sheets (v3).

Printed bubble rings are red/orange. A pencil-filled bubble OBSCURES its
ring, so per row the answer is the option column whose ring is missing —
cross-checked by darkness sampling at the expected spot.
Outputs JSON + overlay PNGs for visual verification.
"""
import os as _os
ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))

import json
import os
import sys

import numpy as np
import pymupdf
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

DPI = 200

def load_page(path):
    if path.lower().endswith((".jpg", ".jpeg", ".png")):
        img = Image.open(path).convert("RGB")
        return np.asarray(img)
    doc = pymupdf.open(path)
    pix = doc[0].get_pixmap(dpi=DPI)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    return np.asarray(img)

def cluster_1d(vals, tol):
    vals = sorted(vals)
    groups = [[vals[0]]]
    for v in vals[1:]:
        if v - groups[-1][-1] <= tol:
            groups[-1].append(v)
        else:
            groups.append([v])
    return groups

def detect(path, x_max_frac=0.74, y_min_frac=0.15, rot180=False):
    arr = load_page(path).astype(int)
    if rot180:
        arr = arr[::-1, ::-1].copy()
    h, w, _ = arr.shape
    scale = w / 1653.0
    R, G, B = arr[..., 0], arr[..., 1], arr[..., 2]
    gray = arr.mean(axis=2)

    redish = (R > 150) & (R - G > 45) & (R - B > 45)
    lab, n = ndimage.label(redish)
    objs = ndimage.find_objects(lab)
    rings = []
    for i, sl in enumerate(objs):
        ys, xs = sl
        bh, bw = ys.stop - ys.start, xs.stop - xs.start
        if not (13 * scale <= bw <= 32 * scale and 13 * scale <= bh <= 32 * scale):
            continue
        if not (0.7 <= bw / bh <= 1.45):
            continue
        area = int((lab[sl] == i + 1).sum())
        fr = area / (bw * bh)
        if not (0.08 <= fr <= 0.85):
            continue
        cy, cx = ys.start + bh / 2.0, xs.start + bw / 2.0
        if cx > w * x_max_frac or cy < h * y_min_frac:
            continue
        rings.append((cx, cy))

    if len(rings) < 20:
        return arr, [], rings

    # option columns from ring x positions
    xg = cluster_1d([r[0] for r in rings], 12 * scale)
    cols = [sum(g) / len(g) for g in xg if len(g) >= 5]
    if not cols:
        return arr, [], rings

    blocks_x = [[cols[0]]]
    for c in cols[1:]:
        if c - blocks_x[-1][-1] <= 100 * scale:
            blocks_x[-1].append(c)
        else:
            blocks_x.append([c])

    rad = int(round(7 * scale))
    yy, xx = np.mgrid[-rad:rad + 1, -rad:rad + 1]
    disk = (yy ** 2 + xx ** 2) <= rad * rad

    def disk_mean(iy, ix):
        best = 255.0
        for dy in (-5, 0, 5):
            for dx in (-5, 0, 5):
                py, px = int(round(iy + dy * scale)), int(round(ix + dx * scale))
                patch = gray[py - rad:py + rad + 1, px - rad:px + rad + 1]
                if patch.shape == disk.shape:
                    best = min(best, float(patch[disk].mean()))
        return best

    results = []
    for bcols in blocks_x:
        if len(bcols) != 4:
            continue
        x_lo, x_hi = min(bcols) - 16 * scale, max(bcols) + 16 * scale
        brings = [r for r in rings if x_lo <= r[0] <= x_hi]
        rowgroups = [g for g in cluster_1d([r[1] for r in brings], 14 * scale)
                     if len(g) >= 2]
        if len(rowgroups) < 9:
            continue
        rowys = [sum(g) / len(g) for g in rowgroups]
        # fill gaps where a whole row went undetected (filled mark + noise)
        med0 = float(np.median(np.diff(rowys)))
        filled_rows = list(rowys)
        for a, b in zip(rowys, rowys[1:]):
            k = round((b - a) / med0)
            for j in range(1, k):
                filled_rows.append(a + (b - a) * j / k)
        filled_rows.sort()

        # background darkness = median over unfilled rings of this block
        ring_means = []
        for cx, cy in brings[:60]:
            ring_means.append(disk_mean(cy, cx))
        bg = float(np.median(ring_means))
        thr = bg - max(40, 0.25 * bg)

        # probe for undetected edge rows (first/last row entirely missed)
        for direction in (-1, 1):
            for _ in range(3):
                y_probe = (filled_rows[0] - med0) if direction < 0 else (filled_rows[-1] + med0)
                if not (h * y_min_frac < y_probe < h - 2 * rad):
                    break
                m = [disk_mean(y_probe, c) for c in bcols]
                ndark = sum(1 for v in m if v < thr)
                nbg = sum(1 for v in m if v > bg - 25)
                if ndark == 1 and nbg == 3:
                    filled_rows.insert(0 if direction < 0 else len(filled_rows), y_probe)
                else:
                    break
        rowgroups = [[y] for y in filled_rows]

        answers, warns = [], []
        for qi, g in enumerate(rowgroups):
            ry = sum(g) / len(g)
            rrings = [r for r in brings if abs(r[1] - ry) <= 14 * scale]
            # which columns have a visible ring; track x drift for skew
            matched = {}
            drift = []
            for rx, ryy in rrings:
                ci = min(range(4), key=lambda i: abs(bcols[i] - rx))
                if abs(bcols[ci] - rx) < 25 * scale:
                    matched[ci] = (rx, ryy)
                    drift.append(rx - bcols[ci])
            dx = float(np.median(drift)) if drift else 0.0
            missing = [i for i in range(4) if i not in matched]
            means = [disk_mean(ry, bcols[i] + dx) for i in range(4)]
            dark = [i for i in range(4) if means[i] < thr]

            letter = "?"
            if len(missing) == 1:
                if missing[0] in dark:
                    letter = "ABCD"[missing[0]]
                elif len(dark) == 1:
                    letter = "ABCD"[dark[0]]
                    warns.append((qi + 1, f"ring missing at {'ABCD'[missing[0]]} "
                                  f"but dark at {letter}; chose dark",
                                  [round(m) for m in means]))
                else:
                    letter = "ABCD"[missing[0]]
                    warns.append((qi + 1, f"missing-ring {letter} not dark",
                                  [round(m) for m in means]))
            elif len(missing) == 0:
                if len(dark) == 1:
                    # marker pen leaves the printed ring visible: trust darkness
                    letter = "ABCD"[dark[0]]
                else:
                    warns.append((qi + 1, "no missing ring, no unique dark",
                                  [round(m) for m in means]))
            else:  # >=2 missing rings: use darkness to disambiguate
                cand = [i for i in missing if i in dark]
                if len(cand) == 1:
                    letter = "ABCD"[cand[0]]
                elif len(dark) == 1:
                    letter = "ABCD"[dark[0]]
                else:
                    warns.append((qi + 1, f"unresolved missing={missing}",
                                  [round(m) for m in means]))
            answers.append((ry, dx, letter))

        # row spacing sanity
        ys_ = [a[0] for a in answers]
        gaps = np.diff(ys_)
        med = float(np.median(gaps)) if len(gaps) else 0
        for i, gp in enumerate(gaps):
            if med and not (0.7 * med < gp < 1.45 * med):
                warns.append((i + 2, f"row gap {round(gp)} vs {round(med)}", []))

        results.append({
            "x_cols": [round(c) for c in bcols],
            "n": len(answers),
            "key": "".join(a[2] for a in answers),
            "warnings": warns,
            "pts": [(bcols, ry, dx, letter) for ry, dx, letter in answers],
        })
    return arr, results, rings

def detect_best(path):
    """Detect in both orientations, return the cleaner result."""
    arr, results, rings = detect(path)
    arr2, results2, rings2 = detect(path, rot180=True)
    def score(res):
        if not res:
            return 10**6
        bad = sum(blk["key"].count("?") * 3 + len(blk["warnings"]) for blk in res)
        return bad - sum(blk["n"] for blk in res)
    if score(results2) < score(results):
        return arr2, results2, rings2, True
    return arr, results, rings, False

def overlay(arr, results, rings, out_png):
    img = Image.fromarray(arr.astype(np.uint8)).convert("RGB")
    d = ImageDraw.Draw(img)
    scale = img.width / 1653.0
    try:
        font = ImageFont.truetype("arialbd.ttf", int(26 * scale))
    except Exception:
        font = None
    for cx, cy in rings:
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], outline=(0, 120, 255), width=2)
    for blk in results:
        for j, (bcols, ry, dx, letter) in enumerate(blk["pts"]):
            d.text((max(bcols) + 30 * scale, ry - 13 * scale), f"{j+1}:{letter}",
                   fill=(180, 0, 0), font=font)
    img.save(out_png)

def main(paths, outdir):
    os.makedirs(outdir, exist_ok=True)
    all_res = {}
    for p in paths:
        name = os.path.splitext(os.path.basename(p))[0]
        try:
            arr, results, rings, rotated = detect_best(p)
            if rotated:
                print(name, "-> using 180-degree rotation")
        except Exception as e:
            print(name, "ERROR", repr(e))
            continue
        all_res[name] = [{k: blk[k] for k in ("x_cols", "n", "key", "warnings")}
                         for blk in results]
        overlay(arr, results, rings, os.path.join(outdir, name + "_overlay.png"))
        print(name, f"(rings={len(rings)}, blocks={len(results)})")
        for blk in results:
            flag = ""
            if blk["warnings"]:
                flag = " !! " + "; ".join(f"q{q} {msg} {m}" for q, msg, m in blk["warnings"])
            print(f"  cols@{blk['x_cols']} n={blk['n']} {blk['key']}{flag}")
    out_json = os.path.join(outdir, "detected.json")
    existing = {}
    if os.path.exists(out_json):
        with open(out_json, encoding="utf-8") as f:
            existing = json.load(f)
    existing.update(all_res)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=1)

if __name__ == "__main__":
    import glob
    pats = sys.argv[1:] or [
        _os.path.join(ROOT, r"20*\*\*Cevap*.pdf"),
        _os.path.join(ROOT, r"20*\*\*Cevap*.jpg"),
    ]
    paths = []
    for pat in pats:
        paths.extend(sorted(glob.glob(pat)))
    main(paths, _os.path.join(ROOT, r"_work\detected"))
