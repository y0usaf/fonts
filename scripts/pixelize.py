#!/usr/bin/env python3
"""Pixelize a hinted vector font into a pixel (bitmap-look) vector TTF.

Renders every cmap-reachable glyph with FreeType in monochrome mode at a
fixed ppem (the font's own TrueType hinting does the pixel-fitting), then
rebuilds each glyph as rectilinear outlines where one pixel = a square of
font units. The result is a scalable TTF that looks like a bitmap font,
in the spirit of Departure Mono.

Pixels are always square in the output; --ppem-y compresses the *design*
vertically (FreeType hints each axis independently), which is how you get
squarish Departure-like proportions out of a tall font like Iosevka.

Usage:
  ./scripts/pixelize.py SRC.ttf --ppem 16 --family "Iosevka Pixel Slab" \
      --out fonts/iosevka-pixel-slab/IosevkaPixelSlab-Regular.ttf
  ./scripts/pixelize.py SRC.ttf --ppem 16 --ppem-y 13 --family "... Squat" ...
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

import freetype
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.O_S_2f_2 import Panose

LOAD_FLAGS = freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_MONO
UNITS_PER_PIXEL = 64


def bitmap_pixels(glyph) -> set[tuple[int, int]]:
    """Extract lit pixels as (x, y) with y-up font coordinates.

    Each pixel occupies the unit square from (x, y) to (x + 1, y + 1).
    """
    bm = glyph.bitmap
    left, top = glyph.bitmap_left, glyph.bitmap_top
    pixels = set()
    for row in range(bm.rows):
        base = row * bm.pitch
        for col in range(bm.width):
            if bm.buffer[base + col // 8] >> (7 - (col % 8)) & 1:
                pixels.add((left + col, top - row - 1))
    return pixels


def pixels_to_contours(pixels: set[tuple[int, int]]) -> list[list[tuple[int, int]]]:
    """Union pixel squares into rectilinear contours via edge cancellation.

    Each pixel contributes its four edges counter-clockwise; edges shared by
    adjacent pixels cancel, leaving only the boundary. Holes come out with
    opposite winding automatically (correct for TrueType non-zero fill).
    """
    edges: set[tuple[tuple[int, int], tuple[int, int]]] = set()

    def add(a, b):
        if (b, a) in edges:
            edges.discard((b, a))
        else:
            edges.add((a, b))

    for x, y in pixels:
        add((x, y), (x + 1, y))
        add((x + 1, y), (x + 1, y + 1))
        add((x + 1, y + 1), (x, y + 1))
        add((x, y + 1), (x, y))

    outgoing: dict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)
    for a, b in edges:
        outgoing[a].append(b)

    contours = []
    starts = sorted(outgoing)
    for start in starts:
        while outgoing[start]:
            path = [start]
            prev, cur = start, outgoing[start].pop()
            while cur != start:
                path.append(cur)
                nxts = outgoing[cur]
                if len(nxts) == 1:
                    nxt = nxts.pop()
                else:
                    # Diagonal pixel touch: prefer the sharpest left turn so
                    # loops stay simple and never cross themselves.
                    dx, dy = cur[0] - prev[0], cur[1] - prev[1]
                    nxts.sort(key=lambda n: dx * (n[1] - cur[1]) - dy * (n[0] - cur[0]))
                    nxt = nxts.pop()
                prev, cur = cur, nxt
            contours.append(simplify(path))
    return contours


def simplify(path: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Merge consecutive collinear (axis-aligned) segments."""
    out = []
    n = len(path)
    for i, p in enumerate(path):
        a, b = path[i - 1], path[(i + 1) % n]
        if (a[0] == p[0] == b[0]) or (a[1] == p[1] == b[1]):
            continue
        out.append(p)
    return out


def build_glyph(pixels, advance_px, glyph_set):
    pen = TTGlyphPen(glyph_set)
    for contour in pixels_to_contours(pixels):
        pen.moveTo((contour[0][0] * UNITS_PER_PIXEL, contour[0][1] * UNITS_PER_PIXEL))
        for x, y in contour[1:]:
            pen.lineTo((x * UNITS_PER_PIXEL, y * UNITS_PER_PIXEL))
        pen.closePath()
    return pen.glyph()


def pixelize(
    src: Path,
    out: Path,
    ppem: int,
    ppem_y: int,
    family: str,
    style: str,
    ascent_px: int | None = None,
    descent_px: int | None = None,
) -> None:
    face = freetype.Face(str(src))
    if face.num_fixed_sizes:
        # Bitmap font (BDF/PCF/OTB): use its native strike, ignore --ppem.
        face.select_size(0)
        ppem = face.size.x_ppem
    else:
        face.set_pixel_sizes(ppem, ppem_y)

    # cmap: (codepoint -> glyph name) and (glyph name -> source glyph id).
    if src.suffix.lower() in {".ttf", ".otf"}:
        src_font = TTFont(src)
        src_cmap = src_font.getBestCmap()
        gid_of = {name: gid for gid, name in enumerate(src_font.getGlyphOrder())}
        src_cmap = {cp: n for cp, n in src_cmap.items() if n in gid_of}
    else:
        # No fontTools support (BDF/PCF): enumerate the charmap with FreeType.
        src_cmap, gid_of, name_of_gid = {}, {}, {}
        cp, gid = face.get_first_char()
        while gid:
            name = name_of_gid.setdefault(gid, f"uni{cp:04X}")
            src_cmap[cp] = name
            gid_of[name] = gid
            cp, gid = face.get_next_char(cp, gid)

    # Dedupe: render each source glyph once, even if many codepoints share it.
    used_names = sorted(set(src_cmap.values()))
    glyph_order = [".notdef"] + [n for n in used_names if n != ".notdef"]
    gid_of.setdefault(".notdef", 0)

    glyphs, metrics = {}, {}
    empty = 0
    for name in glyph_order:
        face.load_glyph(gid_of[name], LOAD_FLAGS)
        advance_px = face.glyph.advance.x >> 6
        pixels = bitmap_pixels(face.glyph)
        glyphs[name] = build_glyph(pixels, advance_px, None)
        lsb = min((x for x, _ in pixels), default=0) * UNITS_PER_PIXEL
        metrics[name] = (advance_px * UNITS_PER_PIXEL, lsb)
        if not pixels:
            empty += 1

    upm = ppem * UNITS_PER_PIXEL
    if ascent_px is None:
        ascent_px = face.size.ascender >> 6
    if descent_px is None:
        descent_px = -(face.size.descender >> 6)
    ascent = ascent_px * UNITS_PER_PIXEL
    descent = -descent_px * UNITS_PER_PIXEL  # negative

    fb = FontBuilder(upm, isTTF=True)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap({cp: n for cp, n in src_cmap.items() if n in glyphs and cp <= 0x10FFFF})
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=ascent, descent=descent, lineGap=0)

    full = f"{family} {style}"
    ps = full.replace(" ", "")
    fb.setupNameTable(
        {
            "familyName": family,
            "styleName": style,
            "fullName": full,
            "psName": ps,
            "uniqueFontIdentifier": f"{ps};pixelized@{ppem}ppem",
            "version": "Version 1.000",
        }
    )
    panose = Panose()
    panose.bFamilyType = 2
    panose.bProportion = 9  # monospaced
    advances = {adv for adv, _ in metrics.values() if adv > 0}
    fb.setupOS2(
        sTypoAscender=ascent,
        sTypoDescender=descent,
        sTypoLineGap=0,
        usWinAscent=ascent,
        usWinDescent=-descent,
        xAvgCharWidth=min(advances) if advances else upm // 2,
        panose=panose,
        fsSelection=0x0040,  # REGULAR
        usWeightClass=400,
        usWidthClass=5,
    )
    fb.setupPost(isFixedPitch=1)
    fb.font["head"].macStyle = 0
    fb.font["head"].lowestRecPPEM = ppem

    out.parent.mkdir(parents=True, exist_ok=True)
    fb.save(str(out))
    print(
        f"wrote {out} — {len(glyph_order)} glyphs ({empty} empty), "
        f"ppem {ppem}x{ppem_y}, upm {upm}, line {(ascent - descent) // UNITS_PER_PIXEL}px"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("src", type=Path)
    parser.add_argument("--ppem", type=int, default=16)
    parser.add_argument("--ppem-y", type=int, default=None, help="vertical ppem (default: same as --ppem)")
    parser.add_argument("--ascent-px", type=int, default=None, help="clamp ascent (pixels above baseline)")
    parser.add_argument("--descent-px", type=int, default=None, help="clamp descent (pixels below baseline, positive)")
    parser.add_argument("--family", required=True)
    parser.add_argument("--style", default="Regular")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    pixelize(
        args.src,
        args.out,
        args.ppem,
        args.ppem_y or args.ppem,
        args.family,
        args.style,
        args.ascent_px,
        args.descent_px,
    )


if __name__ == "__main__":
    main()
