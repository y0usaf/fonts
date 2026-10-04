#!/usr/bin/env python3
"""Condense Departure Mono from a 7px to a 5px cell on whole pixels.

Each glyph loses two of its seven pixel columns. Every combination of two
column deletions or adjacent-column merges is scored against the original
bitmap (strokes per row, connected parts, counters, stroke-edge positions,
symmetry, spacing column, position), and the cheapest wins. Rows are
untouched. Characters in OVERRIDES are drawn by hand; their accented forms
keep the drawn base and condense only the accent. Box drawing and
powerline glyphs keep ink in their edge columns so they still connect.

The output is reproducible: head timestamps come from the source font.

Usage:
  ./scripts/condense_departure.py fonts/departure-mono/DepartureMono-Regular.ttf \
      --out fonts/departure-mono/DepartureMonoUltraCondensed-Regular.ttf
"""

from __future__ import annotations

import argparse
import sys
import unicodedata
from collections.abc import Iterator
from pathlib import Path

from fontTools.pens.pointInsidePen import PointInsidePen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pixelize import pixels_to_contours  # noqa: E402

UNIT, SRC, DST = 50, 7, 5
CONNECTOR_RANGES = [(0x2500, 0x259F), (0xE0A0, 0xE0FF)]
VERSION = "Version 1.500-condensed; generated from Departure Mono Regular on whole pixels"

Columns = list[frozenset[int]]

OVERRIDES = {
    "A": (7, [".##.", "#..#", "#..#", "#..#", "####", "#..#", "#..#", "#..#"]),
    "M": (7, ["#..#", "####", "####", "#..#", "#..#", "#..#", "#..#", "#..#"]),
    "V": (7, ["#..#", "#..#", "#..#", "#..#", "#..#", "#..#", ".##.", ".#.."]),
    "W": (7, ["#..#", "#..#", "#..#", "#..#", "#..#", "####", "####", "#..#"]),
    "X": (7, ["#..#", "#..#", "#..#", ".##.", ".##.", "#..#", "#..#", "#..#"]),
    "Y": (7, [".#.#", ".#.#", ".#.#", ".#.#", "..#.", "..#.", "..#.", "..#."]),
    "m": (5, ["###.", "####", "#..#", "#..#", "#..#", "#..#"]),
    "v": (5, ["#..#", "#..#", "#..#", "#..#", ".##.", ".#.."]),
    "w": (5, ["#..#", "#..#", "#..#", "#..#", "####", ".##."]),
    "x": (5, ["#..#", "#..#", ".##.", ".##.", "#..#", "#..#"]),
    "y": (5, ["#..#", "#..#", "#..#", "#..#", ".##.", ".#..", ".#..", "#..."]),
    "$": (7, [".#..", ".###", "#.#.", "#.#.", ".##.", "..##", "###.", ".#.."]),
    "%": (7, ["#..#", "#..#", "...#", "..#.", ".#..", "#...", "#..#", "#..#"]),
    "*": (7, ["#..#", ".##.", "####", ".##.", "#..#"]),
    "@": (7, [".##.", "#..#", "#.##", "#.##", "#.##", "#...", "#...", ".###"]),
}


def drawn(top: int, lines: list[str]) -> Columns:
    columns: list[set[int]] = [set() for _ in range(DST)]
    for i, line in enumerate(lines):
        for x, pixel in enumerate(line):
            if pixel == "#":
                columns[x].add(top - i)
    return [frozenset(c) for c in columns]


def bitmap(glyph_set, glyf, name: str) -> dict[int, set[int]]:
    g = glyf[name]
    if g.numberOfContours == 0:
        return {}
    g.recalcBounds(glyf)
    cols: dict[int, set[int]] = {}
    for cy in range(g.yMin // UNIT, -(-g.yMax // UNIT)):
        for cx in range(g.xMin // UNIT, -(-g.xMax // UNIT)):
            pen = PointInsidePen(glyph_set, (cx * UNIT + UNIT / 2, cy * UNIT + UNIT / 2))
            glyph_set[name].draw(pen)
            if pen.getResult():
                cols.setdefault(cx, set()).add(cy)
    return cols


def grid(columns: Columns, rows: list[int]) -> list[list[bool]]:
    return [[r in col for col in columns] for r in rows]


def runs(row: list[bool]) -> int:
    return sum(1 for i, b in enumerate(row) if b and (i == 0 or not row[i - 1]))


def parts(cells: set[tuple[int, int]], diagonal: bool) -> int:
    seen: set[tuple[int, int]] = set()
    count = 0
    steps = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    if diagonal:
        steps += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
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


def shape(g: list[list[bool]]) -> tuple[list[int], int, int]:
    h, w = len(g), len(g[0])
    ink = {(x, y) for y in range(h) for x in range(w) if g[y][x]}
    blank = {(x, y) for y in range(-1, h + 1) for x in range(-1, w + 1) if (x, y) not in ink}
    return [runs(row) for row in g], parts(ink, True), parts(blank, False) - 1


def symmetric(g: list[list[bool]]) -> bool:
    cols = [x for x in range(len(g[0])) if any(row[x] for row in g)]
    if not cols:
        return True
    lo, hi = cols[0], cols[-1]
    return all(row[lo + i] == row[hi - i] for row in g for i in range(hi - lo + 1))


def ink_span(columns: Columns) -> tuple[int, int] | None:
    used = [i for i, c in enumerate(columns) if c]
    return (used[0], used[-1]) if used else None


def candidates(width: int) -> Iterator[list[tuple[int, ...]]]:
    def ops(n: int) -> Iterator[tuple[str, int]]:
        for c in range(n):
            yield ("del", c)
        for c in range(n - 1):
            yield ("merge", c)

    def apply(groups: list[tuple[int, ...]], op: tuple[str, int]) -> list[tuple[int, ...]]:
        kind, c = op
        if kind == "del":
            return groups[:c] + groups[c + 1:]
        return groups[:c] + [groups[c] + groups[c + 1]] + groups[c + 2:]

    start = [(i,) for i in range(width)]
    for a in ops(width):
        once = apply(start, a)
        for b in ops(len(once)):
            yield apply(once, b)


def edges(columns: Columns, rows: list[int]) -> set[int]:
    used: set[int] = set()
    for r in rows:
        row = [r in c for c in columns] + [False]
        for x in range(len(columns)):
            if row[x] and (x == 0 or not row[x - 1]):
                used.add(x)
            if row[x] and not row[x + 1]:
                used.add(x + 1)
    return used


def condense(columns: Columns, rows: list[int], connector: bool) -> tuple[Columns, float]:
    original = grid(columns, rows)
    o_runs, o_parts, o_holes = shape(original)
    o_sym = symmetric(original)
    o_edges = edges(columns, rows)
    span = ink_span(columns)
    left_edge, right_edge = bool(columns[0]), bool(columns[-1])
    centre = (span[0] + span[1] + 1) / 2 * DST / SRC if span else DST / 2
    best: tuple[float, Columns] | None = None
    for groups in candidates(len(columns)):
        result = [frozenset().union(*(columns[i] for i in group)) for group in groups]
        grown = sum(len(col) - max(len(columns[i]) for i in group) for col, group in zip(result, groups))
        mapped = {sum(1 for group in groups if group[-1] < e) for e in o_edges}
        g = grid(result, rows)
        r_runs, r_parts, r_holes = shape(g)
        cost = 8 * sum(abs(a - b) for a, b in zip(o_runs, r_runs))
        cost += 20 * abs(o_parts - r_parts) + 20 * abs(o_holes - r_holes)
        cost += 100 * sum(1 for row in g if not any(row))
        cost += 6 * (len(o_edges) - len(mapped))
        cost += 1.5 * grown
        cost += 3 * sum(sum(1 for i in group if columns[i]) - (1 if any(columns[i] for i in group) else 0)
                        for group in groups)
        cost += 3 * sum(1 for i in range(len(columns)) if columns[i] and not any(i in group for group in groups))
        if o_sym and not symmetric(g):
            cost += 6
        if left_edge and not result[0]:
            cost += 30
        if right_edge and not result[-1]:
            cost += 30
        if not connector and not right_edge and result[-1]:
            cost += 100
        new_span = ink_span(result)
        if new_span and not connector:
            cost += 2 * abs((new_span[0] + new_span[1] + 1) / 2 - centre)
        if best is None or cost < best[0]:
            best = (cost, result)
    assert best is not None
    return best[1], best[0]


def build(glyph_set, columns: Columns):
    pixels = {(x, y) for x, col in enumerate(columns) for y in col}
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
    names = {1: family, 2: "Regular", 3: f"{family};condensed", 4: family, 5: VERSION, 6: ps}
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
            for item in (value if isinstance(value, list) else [value]):
                walk(item)

    walk(font["GPOS"].table)


def accented(font: TTFont) -> dict[str, str]:
    out = {}
    cmap = font.getBestCmap()
    for cp, name in cmap.items():
        decomposition = unicodedata.decomposition(chr(cp)).split()
        if not decomposition or decomposition[0].startswith("<"):
            continue
        base = int(decomposition[0], 16)
        if base in cmap and cmap[base] != name:
            out[name] = cmap[base]
    return out


def generate(src: Path, out: Path, family: str) -> None:
    font = TTFont(src, recalcTimestamp=False)
    glyf, hmtx = font["glyf"], font["hmtx"]
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    connectors = {name for cp, name in cmap.items()
                  if any(lo <= cp <= hi for lo, hi in CONNECTOR_RANGES)}
    drawn_names = {cmap[ord(ch)]: drawn(*spec) for ch, spec in OVERRIDES.items() if ord(ch) in cmap}
    bases = accented(font)
    report: list[tuple[float, str]] = []
    results: dict[str, Columns | None] = {}
    kept: list[str] = []

    def solve(name: str) -> Columns | None:
        if name in results:
            return results[name]
        results[name] = None
        cols = bitmap(glyph_set, glyf, name)
        if hmtx[name][0] != SRC * UNIT or not cols:
            return None
        if min(cols) < 0 or max(cols) >= SRC:
            raise SystemExit(f"{name} has ink outside its cell")
        columns = [frozenset(cols.get(x, ())) for x in range(SRC)]
        rows = sorted({r for c in columns for r in c})
        if name in drawn_names:
            results[name] = drawn_names[name]
            return results[name]
        if name in bases and (base_result := solve(bases[name])):
            base = bitmap(glyph_set, glyf, bases[name])
            base_rows = {r for c in base.values() for r in c}
            if all(frozenset(r for r in columns[x] if r in base_rows) == frozenset(base.get(x, ()))
                   for x in range(SRC)):
                accent = [frozenset(r for r in c if r not in base_rows) for c in columns]
                accent_rows = sorted({r for c in accent for r in c})
                accent_result = condense(accent, accent_rows, False)[0] if accent_rows else [frozenset()] * DST
                results[name] = [a | b for a, b in zip(accent_result, base_result)]
                kept.append(name)
                return results[name]
        result, cost = condense(columns, rows, name in connectors)
        report.append((cost, name))
        results[name] = result
        return result

    built = {}
    for name in font.getGlyphOrder():
        if (result := solve(name)) is not None:
            built[name] = build(glyph_set, result)
    for name in font.getGlyphOrder():
        if hmtx[name][0] == SRC * UNIT:
            if name in built:
                glyf[name] = built[name]
                glyf[name].recalcBounds(glyf)
                hmtx[name] = (DST * UNIT, glyf[name].xMin)
            else:
                hmtx[name] = (DST * UNIT, 0)
    scale_anchors(font)
    font["OS/2"].xAvgCharWidth = DST * UNIT
    font["OS/2"].usWidthClass = 1
    font["post"].isFixedPitch = 1
    rename(font, family)
    out.parent.mkdir(parents=True, exist_ok=True)
    font.save(out)
    print(f"wrote {out}: {len(drawn_names)} drawn, {len(kept)} accented from condensed bases, "
          f"{len(report)} condensed")
    report.sort(reverse=True)
    for cost, name in report[:10]:
        print(f"{cost:6.1f} {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("src", type=Path)
    parser.add_argument("--family", default="Departure Mono Ultra Condensed")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    generate(args.src, args.out, args.family)


if __name__ == "__main__":
    main()
