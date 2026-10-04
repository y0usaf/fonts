#!/usr/bin/env python3
"""Build Moono: Departure Mono redrawn on the pixel grid of its 22px rendering.

At 22px one Departure pixel is 2x2 screen pixels. Moono works in half-columns
(25 units, one screen pixel at 22px): every letter's 10 half-columns of ink
drop to 8, removing the half-columns that least change it (never thinning a
2px stroke or closing a counter when another choice exists, and keeping
symmetric letters symmetric), and letters sit 1px apart in a 9px cell.
Letters whose diagonals cannot survive column removal are drawn by hand in
DRAWN. Box drawing loses the same columns everywhere so lines still meet;
blocks and powerline shapes are resampled. Rows are untouched, so Moono is
sharp at exactly 22px and 44px and soft at other sizes.

The output is reproducible: head timestamps come from the source font.

Usage:
  ./scripts/build_moono.py fonts/departure-mono/DepartureMono-Regular.ttf \
      --out fonts/moono/Moono-Regular.ttf
"""

from __future__ import annotations

import argparse
import sys
from itertools import combinations
from pathlib import Path

from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from condense_departure import bitmap, parts  # noqa: E402
from pixelize import pixels_to_contours  # noqa: E402

HALF, ROW, SRC_CELL, LETTER = 25, 50, 14, 8
LINES = (0x2500, 0x257F)
FILLS = [(0x2580, 0x259F), (0xE0A0, 0xE0FF)]
VERSION = "Version 1.000; Departure Mono Regular redrawn on its 22px pixel grid"

Pixels = set[tuple[int, int]]

DRAWN = {
    "A": (7, ["...##...", ".##..##.", "##....##", "##....##", "########", "##....##", "##....##", "##....##"]),
    "V": (7, ["##....##", "##....##", "##....##", "##....##", "##....##", ".##..##.", ".##..##.", "...##..."]),
    "W": (7, ["##....##", "##....##", "##....##", "##.##.##", "##.##.##", ".##..##.", ".##..##.", ".##..##."]),
    "X": (7, ["##....##", "##....##", ".##..##.", "...##...", ".##..##.", "##....##", "##....##", "##....##"]),
    "Y": (7, ["##....##", "##....##", "##....##", ".##..##.", "...##...", "...##...", "...##...", "...##..."]),
    "m": (5, ["######..", "##.##.##", "##.##.##", "##.##.##", "##.##.##", "##.##.##"]),
    "w": (5, ["##.##.##", "##.##.##", "##.##.##", "##.##.##", "##.##.##", "..######"]),
    "v": (5, ["##....##", "##....##", "##....##", ".##..##.", ".##..##.", "...##..."]),
    "x": (5, ["##....##", ".##..##.", "...##...", ".##..##.", "##....##", "##....##"]),
    "y": (5, ["##....##", "##....##", "##....##", ".##..##.", ".##..##.", "...##...", "...##...", "####...."]),
    "f": (7, ["....####", "..##....", "########", "..##....", "..##....", "..##....", "..##....", "######.."]),
    "t": (7, ["..##....", "..##....", "########", "..##....", "..##....", "..##....", "..##..##", "...####."]),
    "k": (7, ["##......", "##......", "##....##", "##..##..", "##.##...", "#####...", "##..##..", "##....##"]),
    "K": (7, ["##....##", "##..##..", "##.##...", "#####...", "##..##..", "##..##..", "##....##", "##....##"]),
    "2": (7, ["..####..", "##....##", "......##", "....##..", "...##...", "..##....", "##......", "########"]),
    "4": (7, ["....####", "...##.##", "..##..##", "##....##", "##....##", "########", "......##", "......##"]),
    "Z": (7, ["########", "......##", "....##..", "...##...", "..##....", "##......", "##......", "########"]),
    "/": (8, ["......##", "......##", "....##..", "....##..", "...##...", "...##...", "..##....", "..##....", "##......", "##......"]),
    "\\": (8, ["##......", "##......", "..##....", "..##....", "...##...", "...##...", "....##..", "....##..", "......##", "......##"]),
    "#": (7, ["...##.##", "...##.##", "########", "..##.##.", "..##.##.", "########", ".##.##..", ".##.##.."]),
    "&": (7, ["..###...", "##..##..", "##......", "..##..##", "##..####", "##..##..", "##..##..", "..###..."]),
    "%": (7, ["##....##", "##....##", ".....##.", "....##..", "...##...", "..##....", ".##...##", "##....##"]),
    "@": (7, ["..####..", "##....##", "......##", "..###.##", "##.##.##", "##.##.##", "##.##.##", "..##.##."]),
    "~": (4, ["..##....", "##.##.##", "....##.."]),
}


def double(pixels: Pixels) -> Pixels:
    return {(2 * x + d, y) for x, y in pixels for d in (0, 1)}


def row_cost(seq: list[bool], removed: set[int]) -> float:
    inked = [j for j, b in enumerate(seq) if b]
    cost = 0.0
    i = 0
    while i < len(seq):
        j = i
        while j < len(seq) and seq[j] == seq[i]:
            j += 1
        k = sum(1 for p in range(i, j) if p in removed)
        length = j - i
        if seq[i]:
            cost += 50 if length - k <= 0 else 10 if length >= 2 and length - k == 1 else 0.3 * k
        elif inked and inked[0] < i and j - 1 < inked[-1]:
            cost += 50 if length - k <= 0 else 1 if length >= 2 and length - k == 1 else 0.2 * k
        i = j
    return cost


def topology(pixels: Pixels) -> tuple[int, int]:
    xs = [x for x, _ in pixels]
    ys = [y for _, y in pixels]
    blank = {(x, y) for x in range(min(xs) - 1, max(xs) + 2)
             for y in range(min(ys) - 1, max(ys) + 2)} - pixels
    return parts(pixels, True), parts(blank, False) - 1


def mirrored(pixels: Pixels) -> bool:
    xs = [x for x, _ in pixels]
    return {(min(xs) + max(xs) - x, y) for x, y in pixels} == pixels


def squeeze(pixels: Pixels) -> Pixels:
    xs = [x for x, _ in pixels]
    lo, hi = min(xs), max(xs)
    need = hi - lo + 1 - LETTER
    if need <= 0:
        return pixels
    rows = sorted({y for _, y in pixels})
    grid = {y: [(x, y) in pixels for x in range(lo, hi + 1)] for y in rows}
    base = topology(pixels)
    symmetric = mirrored(pixels)
    best: tuple[float, Pixels] | None = None
    for removed in combinations(range(hi - lo + 1), need):
        gone = set(removed)
        cost = sum(row_cost(grid[y], gone) for y in rows)
        if best is not None and cost >= best[0]:
            continue
        index = {c: i for i, c in enumerate(c for c in range(hi - lo + 1) if c not in gone)}
        result = {(index[x - lo], y) for x, y in pixels if x - lo in index}
        if topology(result) != base:
            cost += 30
        if symmetric and not mirrored(result):
            cost += 6
        if best is None or cost < best[0]:
            best = (cost, result)
    assert best is not None
    return best[1]


def place(pixels: Pixels, source_lo: int, source_hi: int) -> Pixels:
    xs = [x for x, _ in pixels]
    width = max(xs) - min(xs) + 1
    free = 10 - (source_hi - source_lo + 1)
    if width >= LETTER:
        start = 0
    elif free > 0:
        start = round(max(0, min(free, source_lo - 2)) * (LETTER - width) / free)
    else:
        start = (LETTER - width) // 2
    return {(x + start - min(xs), y) for x, y in pixels}


def resample(pixels: Pixels, cell: int) -> Pixels:
    return {(c, y) for y in {y for _, y in pixels} for c in range(cell)
            if (int((c + 0.5) * SRC_CELL / cell), y) in pixels}


def build(glyph_set, pixels: Pixels):
    pen = TTGlyphPen(glyph_set)
    for contour in pixels_to_contours(pixels):
        pen.moveTo((contour[0][0] * HALF, contour[0][1] * ROW))
        for x, y in contour[1:]:
            pen.lineTo((x * HALF, y * ROW))
        pen.closePath()
    return pen.glyph()


def rename(font: TTFont, family: str) -> None:
    ps = family.replace(" ", "") + "-Regular"
    table = font["name"]
    for nid in (1, 2, 3, 4, 5, 6, 16, 17):
        table.removeNames(nameID=nid)
    names = {1: family, 2: "Regular", 3: f"1.000;{ps}", 4: f"{family} Regular", 5: VERSION, 6: ps}
    for nid, value in names.items():
        table.setName(value, nid, 1, 0, 0)
        table.setName(value, nid, 3, 1, 0x409)


def scale_anchors(font: TTFont, cell: int) -> None:
    if "GPOS" not in font:
        return
    seen: set[int] = set()

    def walk(obj) -> None:
        if id(obj) in seen or not hasattr(obj, "__dict__"):
            return
        seen.add(id(obj))
        if type(obj).__name__ == "Anchor" and hasattr(obj, "XCoordinate"):
            obj.XCoordinate = round(obj.XCoordinate * cell / SRC_CELL / HALF) * HALF
            return
        for value in vars(obj).values():
            for item in value if isinstance(value, list) else [value]:
                walk(item)

    walk(font["GPOS"].table)


def generate(src: Path, out: Path, family: str, cell: int) -> None:
    font = TTFont(src, recalcTimestamp=False)
    glyf, hmtx = font["glyf"], font["hmtx"]
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    lines = {n for cp, n in cmap.items() if LINES[0] <= cp <= LINES[1]}
    fills = {n for cp, n in cmap.items() if any(lo <= cp <= hi for lo, hi in FILLS)}
    drawn = {cmap[ord(ch)]: {(x, top - i) for i, line in enumerate(rows)
                             for x, c in enumerate(line) if c == "#"}
             for ch, (top, rows) in DRAWN.items()}
    cut = set(range(SRC_CELL - cell - 2)) | {SRC_CELL - 2, SRC_CELL - 1}
    keep = {c: i for i, c in enumerate(c for c in range(SRC_CELL) if c not in cut)}
    for name in font.getGlyphOrder():
        if hmtx[name][0] != SRC_CELL * HALF:
            continue
        pixels = bitmap(glyph_set, glyf, name)
        if not pixels:
            hmtx[name] = (cell * HALF, 0)
            continue
        half = double(pixels)
        if name in drawn:
            result = drawn[name]
        elif name in lines:
            result = {(keep[x], y) for x, y in half if x in keep}
        elif name in fills:
            result = resample(half, cell)
        else:
            xs = [x for x, _ in half]
            result = place(squeeze(half), min(xs), max(xs))
        glyf[name] = build(glyph_set, result)
        glyf[name].recalcBounds(glyf)
        hmtx[name] = (cell * HALF, glyf[name].xMin)
    scale_anchors(font, cell)
    font["OS/2"].xAvgCharWidth = cell * HALF
    font["OS/2"].usWidthClass = 3
    font["post"].isFixedPitch = 1
    rename(font, family)
    font.save(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("src", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--family", default="Moono")
    parser.add_argument("--cell", type=int, default=9, help="advance in half-columns (1px each at 22px)")
    args = parser.parse_args()
    generate(args.src, args.out, args.family, args.cell)


if __name__ == "__main__":
    main()
