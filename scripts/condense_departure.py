#!/usr/bin/env python3
"""Narrow Departure Mono from a 7px to a 6px cell on whole pixels.

Departure Mono draws 5px letters with a blank pixel column on each side.
Dropping the left column keeps every letter exactly as drawn and sets text at
6px per character. Glyphs that already ink the left column (#, Æ, ½ and
similar) instead lose the one column whose deletion, or merge with a
neighbour, best preserves their strokes per row, parts, counters and stroke
edges. Box drawing, blocks and powerline glyphs all lose the same column, so
their lines still meet across cells. Rows are untouched.

The output is reproducible: head timestamps come from the source font.

Usage:
  ./scripts/condense_departure.py fonts/departure-mono/DepartureMono-Regular.ttf \
      --out fonts/departure-mono/DepartureMonoSemiCondensed-Regular.ttf
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterator
from pathlib import Path

from fontTools.pens.pointInsidePen import PointInsidePen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pixelize import pixels_to_contours  # noqa: E402

UNIT, SRC, DST = 50, 7, 6
CONNECTOR_RANGES = [(0x2500, 0x259F), (0xE0A0, 0xE0FF)]
VERSION = "Version 1.500; generated from Departure Mono Regular on whole pixels"

Pixels = set[tuple[int, int]]
Groups = list[tuple[int, ...]]


def bitmap(glyph_set, glyf, name: str) -> Pixels:
    glyph = glyf[name]
    if glyph.numberOfContours == 0:
        return set()
    glyph.recalcBounds(glyf)
    pixels = set()
    for y in range(glyph.yMin // UNIT, -(-glyph.yMax // UNIT)):
        for x in range(glyph.xMin // UNIT, -(-glyph.xMax // UNIT)):
            pen = PointInsidePen(glyph_set, (x * UNIT + UNIT / 2, y * UNIT + UNIT / 2))
            glyph_set[name].draw(pen)
            if pen.getResult():
                pixels.add((x, y))
    return pixels


def groupings() -> Iterator[Groups]:
    """Every way to turn SRC columns into DST: one deletion or one adjacent merge."""
    for c in range(SRC):
        yield [(i,) for i in range(SRC) if i != c]
    for c in range(SRC - 1):
        yield [(i,) for i in range(c)] + [(c, c + 1)] + [(i,) for i in range(c + 2, SRC)]


def apply(pixels: Pixels, groups: Groups) -> Pixels:
    column = {src: out for out, group in enumerate(groups) for src in group}
    return {(column[x], y) for x, y in pixels if x in column}


def parts(cells: Pixels, diagonal: bool) -> int:
    steps = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    if diagonal:
        steps += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    seen: Pixels = set()
    count = 0
    for start in cells:
        if start in seen:
            continue
        count += 1
        stack = [start]
        seen.add(start)
        while stack:
            x, y = stack.pop()
            for dx, dy in steps:
                n = (x + dx, y + dy)
                if n in cells and n not in seen:
                    seen.add(n)
                    stack.append(n)
    return count


def profile(pixels: Pixels) -> tuple[dict[int, int], int, int, set[int]]:
    """Strokes per row, connected parts, counters and stroke edge positions."""
    runs: dict[int, int] = {}
    edges: set[int] = set()
    for y in {y for _, y in pixels}:
        xs = sorted(x for x, row in pixels if row == y)
        for i, x in enumerate(xs):
            if i == 0 or xs[i - 1] != x - 1:
                runs[y] = runs.get(y, 0) + 1
                edges.add(x)
            if i == len(xs) - 1 or xs[i + 1] != x + 1:
                edges.add(x + 1)
    xs = [x for x, _ in pixels]
    ys = [y for _, y in pixels]
    blank = {(x, y) for x in range(min(xs) - 1, max(xs) + 2)
             for y in range(min(ys) - 1, max(ys) + 2)} - pixels
    return runs, parts(pixels, True), parts(blank, False) - 1, edges


def cost(pixels: Pixels, groups: Groups) -> float:
    runs, ink_parts, counters, edges = profile(pixels)
    result = apply(pixels, groups)
    if not result:
        return float("inf")
    r_runs, r_parts, r_counters, _ = profile(result)
    mapped = {sum(1 for group in groups if group[-1] < e) for e in edges}
    grown = sum(len({y for x, y in pixels if x in group})
                - max(len({y for x, y in pixels if x == i}) for i in group)
                for group in groups if len(group) == 2)
    total = 8 * sum(abs(runs.get(y, 0) - r_runs.get(y, 0)) for y in set(runs) | set(r_runs))
    total += 20 * abs(ink_parts - r_parts) + 20 * abs(counters - r_counters)
    total += 6 * (len(edges) - len(mapped)) + 1.5 * grown
    inked = {x for x, _ in pixels}
    kept = {i for group in groups for i in group}
    total += 3 * len(inked - kept) + 3 * sum(1 for group in groups if len(group) == 2 and set(group) <= inked)
    if any(x == 0 for x, _ in pixels) and not any(x == 0 for x, _ in result):
        total += 30
    right = any(x == SRC - 1 for x, _ in pixels)
    if right and not any(x == DST - 1 for x, _ in result):
        total += 30
    if not right and any(x == DST - 1 for x, _ in result):
        total += 100
    return total


def narrow(pixels: Pixels) -> Pixels:
    if not any(x == 0 for x, _ in pixels):
        return {(x - 1, y) for x, y in pixels}
    return apply(pixels, min(groupings(), key=lambda groups: cost(pixels, groups)))


def build(glyph_set, pixels: Pixels):
    pen = TTGlyphPen(glyph_set)
    for contour in pixels_to_contours(pixels):
        pen.moveTo((contour[0][0] * UNIT, contour[0][1] * UNIT))
        for x, y in contour[1:]:
            pen.lineTo((x * UNIT, y * UNIT))
        pen.closePath()
    return pen.glyph()


def rename(font: TTFont, family: str) -> None:
    ps = family.replace(" ", "") + "-Regular"
    table = font["name"]
    for nid in (1, 2, 3, 4, 5, 6, 16, 17):
        table.removeNames(nameID=nid)
    names = {1: family, 2: "Regular", 3: f"{family};whole-pixels", 4: family, 5: VERSION, 6: ps}
    for nid, value in names.items():
        table.setName(value, nid, 1, 0, 0)
        table.setName(value, nid, 3, 1, 0x409)


def scale_anchors(font: TTFont) -> None:
    if "GPOS" not in font:
        return
    seen: set[int] = set()

    def walk(obj) -> None:
        if id(obj) in seen or not hasattr(obj, "__dict__"):
            return
        seen.add(id(obj))
        if type(obj).__name__ == "Anchor" and hasattr(obj, "XCoordinate"):
            obj.XCoordinate = round(obj.XCoordinate * DST / SRC / UNIT) * UNIT
            return
        for value in vars(obj).values():
            for item in value if isinstance(value, list) else [value]:
                walk(item)

    walk(font["GPOS"].table)


def generate(src: Path, out: Path, family: str) -> None:
    font = TTFont(src, recalcTimestamp=False)
    glyf, hmtx = font["glyf"], font["hmtx"]
    glyph_set = font.getGlyphSet()
    connectors = {name for cp, name in font.getBestCmap().items()
                  if any(lo <= cp <= hi for lo, hi in CONNECTOR_RANGES)}
    cells = {name: bitmap(glyph_set, glyf, name) for name in font.getGlyphOrder()
             if hmtx[name][0] == SRC * UNIT}
    for name, pixels in cells.items():
        if pixels and (min(x for x, _ in pixels) < 0 or max(x for x, _ in pixels) >= SRC):
            raise SystemExit(f"{name} has ink outside its cell")
    shared = min(
        (groups for groups in groupings() if len(groups[0]) == 1 and len(groups[-1]) == 1),
        key=lambda groups: sum(cost(cells[n], groups) for n in connectors if cells.get(n)),
    )
    for name, pixels in cells.items():
        if pixels:
            narrowed = apply(pixels, shared) if name in connectors else narrow(pixels)
            glyf[name] = build(glyph_set, narrowed)
            glyf[name].recalcBounds(glyf)
            hmtx[name] = (DST * UNIT, glyf[name].xMin)
        else:
            hmtx[name] = (DST * UNIT, 0)
    scale_anchors(font)
    font["OS/2"].xAvgCharWidth = DST * UNIT
    font["OS/2"].usWidthClass = 4
    font["post"].isFixedPitch = 1
    rename(font, family)
    font.save(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("src", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--family", default="Departure Mono Semi Condensed")
    args = parser.parse_args()
    generate(args.src, args.out, args.family)


if __name__ == "__main__":
    main()
