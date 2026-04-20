#!/usr/bin/env python3
"""
Pixelize a monospace font: supersample-rasterize each glyph via grayscale
FreeType rendering, downsample to a low-res pixel grid, apply consistency
post-processing (symmetry, alignment, centering, mirror pairs), then
rebuild vector outlines from square pixels.

Grid maps to sTypoAscender→sTypoDescender so descenders and bracket
bottoms are never clipped. Includes GASP table for crisp rendering.
"""

import argparse
import sys
from collections import Counter
import numpy as np
import freetype
from fontTools.ttLib import TTFont, newTable
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fix_font_names import normalize_font_metadata


# ── rasterization ──────────────────────────────────────────────────────

def rasterize_glyph_coverage(face, char_code, grid_w, grid_h, ss=8,
                              asc_rows=None):
    """Rasterize → float coverage map (grid_h × grid_w), values 0.0–1.0.

    Grid spans sTypoAscender→sTypoDescender. Baseline at asc_rows.
    Renders at ppem=hi_h for maximum quality.
    """
    hi_w = grid_w * ss
    hi_h = grid_h * ss
    asc_px = asc_rows * ss

    face.set_pixel_sizes(0, hi_h)
    try:
        face.load_char(char_code, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_NORMAL)
    except freetype.FT_Exception:
        return None

    bm = face.glyph.bitmap
    top, left = face.glyph.bitmap_top, face.glyph.bitmap_left
    ft_asc = face.size.ascender >> 6

    hi = np.zeros((hi_h, hi_w), dtype=np.float32)
    if bm.rows > 0 and bm.width > 0:
        buf = np.array(bm.buffer, dtype=np.uint8).reshape(bm.rows, bm.pitch)[:, :bm.width]
        y0 = asc_px - top
        sy0, dy0 = max(0, -y0), max(0, y0)
        sx0, dx0 = max(0, -left), max(0, left)
        ch = min(bm.rows - sy0, hi_h - dy0)
        cw = min(bm.width - sx0, hi_w - dx0)
        if ch > 0 and cw > 0:
            hi[dy0:dy0+ch, dx0:dx0+cw] = buf[sy0:sy0+ch, sx0:sx0+cw] / 255.0

    return hi.reshape(grid_h, ss, grid_w, ss).mean(axis=(1, 3))


# ── post-processing on coverage maps ───────────────────────────────────

SYMMETRIC_CHARS = set("AHIMOTUVWXYovwx08*=+^|!:\"")

MIRROR_PAIRS = [
    ('b', 'd'), ('p', 'q'), ('(', ')'), ('[', ']'), ('{', '}'),
    ('<', '>'), ('/', '\\'),
]


def center_glyph(cov):
    col_mass = cov.sum(axis=0)
    ink_cols = np.where(col_mass > 0.01)[0]
    if len(ink_cols) == 0:
        return cov
    left, right = ink_cols[0], ink_cols[-1]
    ideal_left = (cov.shape[1] - (right - left + 1)) // 2
    shift = ideal_left - left
    return np.roll(cov, shift, axis=1) if shift else cov


def enforce_symmetry(cov):
    return (cov + np.fliplr(cov)) / 2.0


def align_top(cov, target_row):
    ink_rows = np.where(cov.sum(axis=1) > 0.05)[0]
    if len(ink_rows) == 0:
        return cov
    shift = target_row - ink_rows[0]
    return np.roll(cov, shift, axis=0) if shift else cov


def detect_reference_lines(coverages, cmap_inv):
    def vote_top(chars):
        rows = []
        for ch in chars:
            gn = cmap_inv.get(ord(ch))
            if gn and gn in coverages:
                ink = np.where(coverages[gn].sum(axis=1) > 0.05)[0]
                if len(ink):
                    rows.append(ink[0])
        return Counter(rows).most_common(1)[0][0] if rows else None

    return {
        'cap_top': vote_top("ABCDEFGHIKLMNPRTUVWXYZ"),
        'x_top': vote_top("acemnorsuvwxz"),
        'digit_top': vote_top("0123456789"),
    }


def postprocess_coverages(coverages, cmap, grid_w, grid_h):
    cmap_inv = {cp: gn for cp, gn in cmap.items()}

    # Phase 1: Center all
    for gn in coverages:
        coverages[gn] = center_glyph(coverages[gn])

    # Phase 2: Detect reference lines
    refs = detect_reference_lines(coverages, cmap_inv)
    print(f"  Reference lines: {refs}")

    # Phase 3: Align heights
    for chars, ref_key in [
        ("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 'cap_top'),
        ("0123456789", 'digit_top'),
        ("acemnorsuvwxz", 'x_top'),
    ]:
        target = refs.get(ref_key)
        if target is None:
            continue
        for ch in chars:
            gn = cmap_inv.get(ord(ch))
            if gn and gn in coverages:
                ink = np.where(coverages[gn].sum(axis=1) > 0.05)[0]
                if len(ink) and ink[0] != target:
                    coverages[gn] = align_top(coverages[gn], target)

    # Phase 4: Symmetry
    for ch in SYMMETRIC_CHARS:
        gn = cmap_inv.get(ord(ch))
        if gn and gn in coverages:
            coverages[gn] = enforce_symmetry(coverages[gn])

    # Phase 5: Mirror pairs
    for left_ch, right_ch in MIRROR_PAIRS:
        lgn = cmap_inv.get(ord(left_ch))
        rgn = cmap_inv.get(ord(right_ch))
        if lgn and rgn and lgn in coverages and rgn in coverages:
            merged = (coverages[lgn] + np.fliplr(coverages[rgn])) / 2.0
            coverages[lgn] = merged
            coverages[rgn] = np.fliplr(merged)

    # Phase 6: Re-center
    for gn in coverages:
        coverages[gn] = center_glyph(coverages[gn])

    return coverages


# ── contour generation ─────────────────────────────────────────────────

def grid_to_contours(grid, grid_w, grid_h, pixel_w, pixel_h, y_top):
    contours = []
    visited = [[False] * grid_w for _ in range(grid_h)]
    for y in range(grid_h):
        for x in range(grid_w):
            if not grid[y][x] or visited[y][x]:
                continue
            x2 = x
            while x2 + 1 < grid_w and grid[y][x2 + 1] and not visited[y][x2 + 1]:
                x2 += 1
            y2 = y
            while y2 + 1 < grid_h:
                if not all(grid[y2 + 1][cx] and not visited[y2 + 1][cx] for cx in range(x, x2 + 1)):
                    break
                y2 += 1
            for ry in range(y, y2 + 1):
                for rx in range(x, x2 + 1):
                    visited[ry][rx] = True
            fx0, fx1 = x * pixel_w, (x2 + 1) * pixel_w
            fy0 = y_top - y * pixel_h
            fy1 = y_top - (y2 + 1) * pixel_h
            contours.append([(fx0, fy0), (fx1, fy0), (fx1, fy1), (fx0, fy1)])
    return contours


# ── main pipeline ──────────────────────────────────────────────────────

def pixelize_font(input_path, output_path, grid_height=16, grid_width=None,
                  family_name=None, supersample=8, threshold=0.35,
                  square_pixels=False):
    src = TTFont(input_path)
    upem = src['head'].unitsPerEm
    hmtx = src['hmtx']
    cmap = src.getBestCmap()

    if not cmap:
        print("Error: no cmap found", file=sys.stderr)
        sys.exit(1)

    os2 = src['OS/2']
    asc_units = os2.sTypoAscender
    desc_units = os2.sTypoDescender
    total_units = asc_units - desc_units

    asc_frac = asc_units / total_units
    asc_rows = round(grid_height * asc_frac)

    ref_width = None
    for ch in ['M', 'm', '0', 'A', 'space']:
        if ord(ch) in cmap:
            ref_width = hmtx[cmap[ord(ch)]][0]
            break
    if ref_width is None:
        ref_width = upem // 2

    grid_w = grid_width if grid_width is not None else max(4, round(ref_width / upem * grid_height))

    pixel_h = total_units / grid_height

    if square_pixels:
        pixel_w = pixel_h
        ref_width = round(pixel_w * grid_w)
    else:
        pixel_w = ref_width / grid_w

    pixel_h_int = round(pixel_h)
    pixel_w_int = round(pixel_w)

    if family_name is None:
        for record in src['name'].names:
            if record.nameID == 1 and record.platformID == 3:
                family_name = f"Pixel {record.toUnicode()}"
                break
        if family_name is None:
            family_name = "Pixelated Font"

    print(f"Font: {family_name}")
    print(f"Grid: {grid_w}×{grid_height} (baseline at row {asc_rows})")
    print(f"Pixel: {pixel_w_int}×{pixel_h_int} units, UPM: {upem}")
    print(f"Cell: asc={asc_units} desc={desc_units} total={total_units}")
    print(f"Supersample: {supersample}×, threshold: {threshold}")

    # ── Phase 1: Rasterize ──
    face = freetype.Face(input_path)
    coverages = {}
    total = len(cmap)
    skipped = 0

    for i, (cp, gname) in enumerate(sorted(cmap.items())):
        if i % 1000 == 0 and i > 0:
            print(f"  rasterize {i}/{total}...")
        cov = rasterize_glyph_coverage(face, cp, grid_w, grid_height,
                                        ss=supersample, asc_rows=asc_rows)
        if cov is None:
            skipped += 1
            continue
        coverages[gname] = cov

    print(f"Rasterized: {len(coverages)}, skipped: {skipped}")

    # ── Phase 2: Post-process ──
    print("Post-processing...")
    coverages = postprocess_coverages(coverages, cmap, grid_w, grid_height)

    # ── Phase 3: Threshold + contours ──
    y_top = asc_units
    glyph_data = {}
    glyph_widths = {}
    for gname, cov in coverages.items():
        grid = (cov >= threshold).tolist()
        glyph_data[gname] = grid_to_contours(
            grid, grid_w, grid_height,
            pixel_w_int, pixel_h_int, y_top
        )
        glyph_widths[gname] = ref_width

    # ── Phase 4: Build font ──
    glyph_order = [".notdef", "space"] + [n for n in glyph_data if n not in (".notdef", "space")]
    char_map = {cp: gn for cp, gn in cmap.items() if gn in glyph_data or gn == "space"}

    fb = FontBuilder(upem, isTTF=True)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap(char_map)
    fb.setupGlyf({})
    glyf_table = fb.font['glyf']

    for gname in glyph_order:
        pen = TTGlyphPen(None)
        if gname == ".notdef":
            m = pixel_w_int
            pen.moveTo((0, desc_units)); pen.lineTo((ref_width, desc_units))
            pen.lineTo((ref_width, asc_units)); pen.lineTo((0, asc_units)); pen.closePath()
            pen.moveTo((m, desc_units + m)); pen.lineTo((m, asc_units - m))
            pen.lineTo((ref_width - m, asc_units - m)); pen.lineTo((ref_width - m, desc_units + m))
            pen.closePath()
        elif gname == "space":
            pass
        elif gname in glyph_data:
            for contour in glyph_data[gname]:
                pen.moveTo(contour[0])
                for pt in contour[1:]:
                    pen.lineTo(pt)
                pen.closePath()
        glyf_table[gname] = pen.glyph()

    metrics = {gn: (glyph_widths.get(gn, ref_width), 0) for gn in glyph_order}
    fb.setupHorizontalMetrics(metrics)

    fb.setupHorizontalHeader(ascent=asc_units, descent=desc_units)
    fb.setupNameTable({"familyName": family_name, "styleName": "Regular"})
    fb.setupOS2(
        sTypoAscender=asc_units, sTypoDescender=desc_units, sTypoLineGap=0,
        usWinAscent=asc_units, usWinDescent=abs(desc_units),
        sxHeight=upem // 2, sCapHeight=(upem * 700) // 1000,
        xAvgCharWidth=ref_width,
    )
    fb.setupPost(isFixedPitch=1)

    from fontTools.ttLib.tables.O_S_2f_2 import Panose
    panose = Panose()
    panose.bFamilyType = 2; panose.bSerifStyle = 11; panose.bWeight = 5
    panose.bProportion = 9; panose.bContrast = 2
    panose.bStrokeVariation = panose.bArmStyle = panose.bLetterForm = 0
    panose.bMidline = panose.bXHeight = 0
    fb.font['OS/2'].panose = panose

    fb.setupHead(unitsPerEm=upem)
    normalize_font_metadata(fb.font, family_name, "Regular")

    # GASP: crisp pixel rendering (gridfit, no anti-aliasing)
    gasp = newTable('gasp')
    gasp.version = 1
    gasp.gaspRange = {0xFFFF: 0x0008}
    fb.font['gasp'] = gasp

    fb.font.save(output_path)
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Pixelize a monospace font")
    p.add_argument("input", help="Input font file (TTF/OTF)")
    p.add_argument("output", help="Output font file (TTF)")
    p.add_argument("--grid-height", type=int, default=16)
    p.add_argument("--grid-width", type=int, default=None)
    p.add_argument("--threshold", type=float, default=0.35)
    p.add_argument("--supersample", type=int, default=8)
    p.add_argument("--square-pixels", action="store_true")
    p.add_argument("--name", type=str, default=None)
    a = p.parse_args()
    pixelize_font(a.input, a.output,
                  grid_height=a.grid_height, grid_width=a.grid_width,
                  family_name=a.name, supersample=a.supersample,
                  threshold=a.threshold, square_pixels=a.square_pixels)
