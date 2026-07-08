#!/usr/bin/env python3
"""Retune a monospace font's metrics without touching outlines.

Departure-style density surgery: override the mono advance and clamp
vertical metrics (hhea + OS/2 typo/win) to squeeze out dead leading.
Glyphs are untouched; zero-advance glyphs stay zero, and glyphs whose
advance is a multiple of the mono advance scale proportionally.

Usage:
  ./scripts/retune.py SRC.ttf --advance 250 --ascent 450 --descent 100 \
      --family "Departure Mono Ultra Compact" \
      --out fonts/departure-mono/DepartureMonoUltraCompact-Regular.ttf
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from fontTools.ttLib import TTFont


def retune(
    src: Path,
    out: Path,
    family: str | None,
    advance: int | None,
    ascent: int | None,
    descent: int | None,
) -> None:
    font = TTFont(src)
    hmtx = font["hmtx"]

    if advance is not None:
        old = Counter(
            aw for aw, _ in hmtx.metrics.values() if aw > 0
        ).most_common(1)[0][0]
        for name, (aw, lsb) in hmtx.metrics.items():
            if aw > 0:
                hmtx.metrics[name] = (round(aw * advance / old), lsb)
        font["OS/2"].xAvgCharWidth = advance

    hhea, os2 = font["hhea"], font["OS/2"]
    if ascent is not None:
        hhea.ascent = os2.sTypoAscender = ascent
        os2.usWinAscent = ascent
    if descent is not None:
        hhea.descent = os2.sTypoDescender = -descent
        os2.usWinDescent = descent
    if ascent is not None or descent is not None:
        hhea.lineGap = os2.sTypoLineGap = 0

    if family:
        name = font["name"]
        style = name.getDebugName(2) or "Regular"
        full = f"{family} {style}" if style.lower() != "regular" else family
        ps = family.replace(" ", "") + "-" + style.replace(" ", "")
        # Drop ALL platform records for identity name IDs, then write fresh
        # ones; stale Mac records would otherwise keep the old family alive.
        for nid in (1, 3, 4, 6, 16, 17):
            name.removeNames(nameID=nid)
        for nid, val in ((1, family), (3, f"{full};retuned"), (4, full), (6, ps)):
            name.setName(val, nid, 3, 1, 0x409)
            name.setName(val, nid, 1, 0, 0)

    out.parent.mkdir(parents=True, exist_ok=True)
    font.save(out)
    upm = font["head"].unitsPerEm
    print(
        f"wrote {out} — advance {advance}, line {hhea.ascent - hhea.descent} "
        f"({(hhea.ascent - hhea.descent) / upm:.3f}em)"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("src", type=Path)
    parser.add_argument("--advance", type=int, default=None, help="mono advance, font units")
    parser.add_argument("--ascent", type=int, default=None, help="ascent, font units")
    parser.add_argument("--descent", type=int, default=None, help="descent, font units (positive)")
    parser.add_argument("--family", default=None)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    retune(args.src, args.out, args.family, args.advance, args.ascent, args.descent)


if __name__ == "__main__":
    main()
