#!/usr/bin/env python3
"""Build original editable pixel drawings; no upstream glyphs are imported.

Native size is config ppem; each source pixel is 64 font units. Tracking and
leading add whole pixels. Box arms adapt to the resulting cell dimensions.
"""
import argparse
import json
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.ttLib.tables.O_S_2f_2 import Panose
from pixelize import build_glyph

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "sources/astra-pixel"


def drawings(config):
    result = {}
    for filename in config["sources"]:
        for line in (SOURCE / filename).read_text().splitlines():
            if not line or line.startswith("#"):
                continue
            cp, pattern = line.split()
            rows = pattern.split("/")
            if any(len(row) != config["width"] or set(row) - {".", "#"} for row in rows):
                raise ValueError(f"Invalid drawing: {filename}: {line}")
            if len(rows) > config["cap"] + config["descent"]:
                raise ValueError(f"Drawing outside line: {line}")
            result[int(cp, 16)] = {(x, config["cap"] - y - 1)
                                  for y, row in enumerate(rows)
                                  for x, ink in enumerate(row) if ink == "#"}
    if not set(range(32, 127)) <= result.keys():
        raise ValueError("Missing printable ASCII")
    return result


def boxes(advance, ascent, descent):
    # Light terminal box set, including half arms; ends deliberately join.
    arms = {"─": "LR", "│": "UD", "┌": "RD", "┐": "LD", "└": "RU",
            "┘": "LU", "├": "URD", "┤": "ULD", "┬": "LRD", "┴": "LRU",
            "┼": "LRUD", "╴": "L", "╵": "U", "╶": "R", "╷": "D"}
    cx, cy = (advance - 1) // 2, 3
    directions = {"L": {(x, cy) for x in range(cx + 1)},
                  "R": {(x, cy) for x in range(cx, advance)},
                  "U": {(cx, y) for y in range(cy, ascent)},
                  "D": {(cx, y) for y in range(-descent, cy + 1)}}
    return {ord(char): set().union(*(directions[a] for a in arm)) for char, arm in arms.items()}


def build(name, config, out, tracking=0, leading=0):
    width = config["width"]
    advance = config["advance"] + tracking
    ascent, descent = config["ascent"] + leading, config["descent"]
    if advance <= width or ascent <= config["cap"]:
        raise ValueError("ASCII requires one blank column and one blank row")
    pixels = drawings(config) | boxes(advance, ascent, descent)
    names = {cp: f"uni{cp:04X}" for cp in pixels}
    glyphs = {names[cp]: build_glyph(px, advance, None) for cp, px in pixels.items()}
    missing = {(x, y) for x in range(width) for y in range(7)
               if x in (0, width - 1) or y in (0, 6)}
    glyphs[".notdef"] = build_glyph(missing, advance, None)
    metrics = {names[cp]: (advance * 64, min((x for x, _ in px), default=0) * 64)
               for cp, px in pixels.items()}
    metrics[".notdef"] = (advance * 64, 0)
    fb = FontBuilder(config["ppem"] * 64, isTTF=True)
    fb.setupGlyphOrder([".notdef"] + [names[cp] for cp in sorted(names)])
    fb.setupCharacterMap(names)
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=ascent * 64, descent=-descent * 64, lineGap=0)
    family = "Astra Pixel" if name == "Text" else f"Astra Pixel {name}"
    if tracking or leading:
        family += f" T{tracking} L{leading}"
    fb.setupNameTable({"familyName": family, "styleName": "Regular",
                       "fullName": family + " Regular", "psName": family.replace(" ", "") + "-Regular",
                       "uniqueFontIdentifier": family + ";1.000", "version": "Version 1.000",
                       "copyright": "Original Astra Pixel drawings, 2026. AGPL-3.0-or-later.",
                       "licenseDescription": "GNU Affero General Public License v3.0 or later; see repository LICENSE."})
    panose = Panose()
    panose.bFamilyType, panose.bProportion = 2, 9
    fb.setupOS2(version=4, sTypoAscender=ascent * 64, sTypoDescender=-descent * 64,
                sTypoLineGap=0, usWinAscent=ascent * 64, usWinDescent=descent * 64,
                sxHeight=(config["cap"] - 2) * 64, sCapHeight=config["cap"] * 64,
                xAvgCharWidth=advance * 64, panose=panose, fsSelection=0xC0)
    fb.setupPost(isFixedPitch=1)
    fb.font["head"].lowestRecPPEM = config["ppem"]
    fb.font["head"].created = fb.font["head"].modified = 3860870400
    fb.font.recalcTimestamp = False
    out.parent.mkdir(parents=True, exist_ok=True)
    fb.save(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tracking", type=int, default=0)
    parser.add_argument("--leading", type=int, default=0)
    parser.add_argument("--out", type=Path, default=ROOT / "fonts/astra-pixel")
    parser.add_argument("--config", type=Path, default=SOURCE / "families.json")
    parser.add_argument("--family", help="Build one named design only")
    parser.add_argument("--alternate", action="append", default=[],
                        help="Named glyph overlay from the selected family's config; repeatable")
    args = parser.parse_args()
    if args.tracking < 0 or args.leading < 0:
        parser.error("Tracking and leading must be nonnegative")
    families = json.loads(args.config.read_text())
    if args.family and args.family not in families:
        parser.error(f"Unknown family: {args.family}")
    if args.alternate and not args.family:
        parser.error("Choose --family when selecting character alternatives")
    for name, config in families.items():
        if args.family and args.family != name:
            continue
        for alternate in args.alternate:
            if alternate not in config.get("alternates", {}):
                parser.error(f"Unknown {name} alternate: {alternate}")
            config["sources"].append(config["alternates"][alternate])
            name += " " + alternate
        build(name, config, args.out / ("AstraPixel-Regular.ttf" if name == "Text" else f"AstraPixel{name.replace(' ', '')}-Regular.ttf"), args.tracking, args.leading)


if __name__ == "__main__":
    main()
