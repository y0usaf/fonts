#!/usr/bin/env python3
"""Condense and compact a monospace outline font.

Instances a variable font at one weight, scales every outline horizontally to
the new advance (a heavier weight puts back the vertical stems the squeeze
thins), and clamps the vertical metrics to the given ascent and descent so
the line holds the font's ASCII ink and nothing else. Box drawing, blocks and
powerline glyphs are also rescaled vertically onto the new line, so they still
fill the cell and meet across rows. A glyph drawn two cells wide for a
character Unicode gives one cell is squeezed into one, as a terminal shows it.
The output is reproducible.

Usage:
  ./scripts/condense_outline.py RysanaMono-Variable.ttf --wght 550 \
      --advance 454 --ascent 878 --descent 183 \
      --family "Lath Mono Condensed Compact" \
      --out fonts/lath-mono/LathMonoCondensedCompact-Regular.ttf
"""

from __future__ import annotations

import argparse
import unicodedata
from pathlib import Path

from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

CONNECTOR_RANGES = [(0x2500, 0x259F), (0x1FB00, 0x1FBFF), (0xE0A0, 0xE0FF)]
KEEP_NAMES = {0, 7, 8, 9, 11, 12, 13, 14}


def decompose(font: TTFont, names: set[str]) -> None:
    glyph_set = font.getGlyphSet()
    glyf = font["glyf"]
    built = {}
    for name in names:
        rec = DecomposingRecordingPen(glyph_set)
        glyph_set[name].draw(rec)
        pen = TTGlyphPen(None)
        rec.replay(pen)
        built[name] = pen.glyph()
    for name, glyph in built.items():
        glyf[name] = glyph


def needs_decompose(glyph, connectors: set[str]) -> bool:
    for comp in glyph.components:
        if not hasattr(comp, "x") or comp.glyphName in connectors:
            return True
        t = getattr(comp, "transform", None)
        if t is not None and (t[0][1] or t[1][0]):
            return True
    return False


def cells_wanted(font: TTFont, cell: int) -> dict[str, int]:
    """Cell count each two-cell glyph should take, from its characters' East Asian Width."""
    hmtx, wide = font["hmtx"], {}
    for cp, name in font.getBestCmap().items():
        if hmtx[name][0] == 2 * cell:
            two = unicodedata.east_asian_width(chr(cp)) in ("W", "F")
            wide[name] = max(wide.get(name, 1), 2 if two else 1)
    return wide


def transform(glyph, sx: float, y_map) -> None:
    if glyph.isComposite():
        for comp in glyph.components:
            comp.x = round(comp.x * sx)
    elif glyph.numberOfContours > 0:
        coords = glyph.coordinates
        for i, (x, y) in enumerate(coords):
            coords[i] = (round(x * sx), round(y_map(y)) if y_map else y)
        glyph.program.fromBytecode(b"")


def scale_gpos(font: TTFont, sx: float) -> None:
    if "GPOS" not in font:
        return
    seen: set[int] = set()

    def walk(obj) -> None:
        if id(obj) in seen or not hasattr(obj, "__dict__"):
            return
        seen.add(id(obj))
        for field in ("XCoordinate", "XPlacement", "XAdvance"):
            if isinstance(getattr(obj, field, None), int):
                setattr(obj, field, round(getattr(obj, field) * sx))
        for value in vars(obj).values():
            for item in value if isinstance(value, list) else [value]:
                walk(item)

    walk(font["GPOS"].table)


def rename(font: TTFont, family: str, wght: float) -> None:
    table = font["name"]
    version = (f"Version 1.000; condensed and compacted from {table.getDebugName(4)} "
               f"{table.getDebugName(5).split(';')[0].removeprefix('Version ')} at wght {wght:g}")
    ps = family.replace(" ", "") + "-Regular"
    for record in list(table.names):
        if record.nameID not in KEEP_NAMES:
            table.removeNames(nameID=record.nameID)
    names = {1: family, 2: "Regular", 3: f"{family};condensed-compact", 4: family, 5: version, 6: ps}
    for nid, value in names.items():
        table.setName(value, nid, 1, 0, 0)
        table.setName(value, nid, 3, 1, 0x409)


def generate(src: Path, out: Path, family: str, wght: float, advance: int,
             ascent: int, descent: int) -> None:
    font = TTFont(src, recalcTimestamp=False)
    if "fvar" in font:
        font = instantiateVariableFont(font, {"wght": wght}, updateFontNames=False)
    for tag in ("STAT",):
        if tag in font:
            del font[tag]
    hmtx, glyf = font["hmtx"], font["glyf"]
    cells = {aw for aw, _ in hmtx.metrics.values() if aw > 0}
    cell = min(cells)
    if any(aw % cell for aw in cells):
        raise SystemExit(f"advances {sorted(cells)} are not multiples of {cell}")
    sx = advance / cell
    hhea = font["hhea"]
    old_top, old_bottom = hhea.ascent, hhea.descent
    new_bottom = -descent
    ky = (ascent - new_bottom) / (old_top - old_bottom)
    y_map = lambda y: new_bottom + (y - old_bottom) * ky
    connectors = {name for cp, name in font.getBestCmap().items()
                  if any(lo <= cp <= hi for lo, hi in CONNECTOR_RANGES)}
    squeezed = {name for name, n in cells_wanted(font, cell).items() if n == 1}
    order = font.getGlyphOrder()
    decompose(font, {n for n in order if glyf[n].isComposite()
                     and (n in connectors or n in squeezed or needs_decompose(glyf[n], connectors | squeezed))})
    for name in order:
        transform(glyf[name], sx / 2 if name in squeezed else sx, y_map if name in connectors else None)
    for name in order:
        aw, _ = hmtx[name]
        glyf[name].recalcBounds(glyf)
        cells = 1 if name in squeezed else aw // cell
        hmtx[name] = (cells * advance, getattr(glyf[name], "xMin", 0) if glyf[name].numberOfContours else 0)
    scale_gpos(font, sx)
    os2 = font["OS/2"]
    hhea.ascent = os2.sTypoAscender = os2.usWinAscent = ascent
    hhea.descent = os2.sTypoDescender = -descent
    os2.usWinDescent = descent
    hhea.lineGap = os2.sTypoLineGap = 0
    os2.fsSelection |= 1 << 7
    os2.usWeightClass = 400
    os2.usWidthClass = 3
    os2.xAvgCharWidth = advance
    font["post"].isFixedPitch = 1
    rename(font, family, wght)
    out.parent.mkdir(parents=True, exist_ok=True)
    font.save(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("src", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--family", required=True)
    parser.add_argument("--wght", type=float, default=400)
    parser.add_argument("--advance", type=int, required=True, help="one-cell advance, font units")
    parser.add_argument("--ascent", type=int, required=True)
    parser.add_argument("--descent", type=int, required=True, help="positive, font units")
    args = parser.parse_args()
    generate(args.src, args.out, args.family, args.wght, args.advance, args.ascent, args.descent)


if __name__ == "__main__":
    main()
