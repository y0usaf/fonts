#!/usr/bin/env python3
"""Exhaustive spacing validator for monospace pixel fonts.

Renders every cmap glyph at the font's native ppem and checks, pixel-exactly:

  horizontal: does any glyph ink escape its advance cell ([0, adv))?
              For every escaping glyph, test pixel collision against every
              other glyph placed in the neighboring cell.
  vertical:   does any glyph ink escape the line box ([-descent, ascent))?
              For every escaping glyph, test pixel collision against every
              other glyph on the adjacent line (offset by line height).
  box:        do box-drawing verticals/horizontals span the full cell, so
              lines connect across cells and rows?

Because the grid repeats, checking one neighbor in each direction covers
every combination of glyphs in a grid of any size.

Usage: ./scripts/spacing_check.py FONT.ttf --ppem 11 [--ascii-only]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import freetype

LOAD = freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_MONO | freetype.FT_LOAD_NO_HINTING


def glyph_pixels(face, gid):
    face.load_glyph(gid, LOAD)
    g = face.glyph
    bm = g.bitmap
    px = set()
    for row in range(bm.rows):
        base = row * bm.pitch
        for col in range(bm.width):
            if bm.buffer[base + col // 8] >> (7 - (col % 8)) & 1:
                px.add((g.bitmap_left + col, g.bitmap_top - row - 1))
    return px, g.advance.x >> 6


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("font", type=Path)
    parser.add_argument("--ppem", type=int, required=True, help="native pixel size")
    parser.add_argument("--ascii-only", action="store_true")
    parser.add_argument("--examples", type=int, default=8)
    args = parser.parse_args()

    face = freetype.Face(str(args.font))
    face.set_pixel_sizes(0, args.ppem)
    asc = face.size.ascender >> 6
    desc = -(face.size.descender >> 6)
    line = asc + desc

    chars = {}
    cp, gid = face.get_first_char()
    while gid:
        if not args.ascii_only or 0x20 <= cp < 0x7F:
            chars.setdefault(gid, cp)
        cp, gid = face.get_next_char(cp, gid)

    pixels, advances = {}, {}
    for gid, cp in chars.items():
        pixels[gid], advances[gid] = glyph_pixels(face, gid)
    adv = max(set(advances.values()) - {0}, key=lambda a: sum(v == a for v in advances.values()))
    print(f"{args.font.name}: {len(chars)} glyphs, adv {adv}px, line {line}px (asc {asc}, desc {desc})")

    def label(gid):
        cp = chars[gid]
        c = chr(cp)
        return f"U+{cp:04X}({c})" if c.isprintable() and not c.isspace() else f"U+{cp:04X}"

    # cells this glyph is allowed to occupy (n advance cells for wide glyphs)
    def cells(gid):
        return max(1, round(advances[gid] / adv))

    # --- horizontal ---
    h_escape = {g for g, px in pixels.items()
                if any(x < 0 or x >= cells(g) * adv for x, _ in px)}
    h_pairs = []
    for a in h_escape:
        right = {(x - cells(a) * adv, y) for x, y in pixels[a] if x >= cells(a) * adv}
        left = {(x + adv, y) for x, y in pixels[a] if x < 0}
        for b, bpx in pixels.items():
            if right & bpx:
                h_pairs.append((a, b, "right"))
            if left and {(x - adv, y) for x, y in bpx if x >= (cells(b) - 1) * adv} & \
                    {(x, y) for x, y in left}:
                h_pairs.append((b, a, "right"))
    print(f"\nhorizontal: {len(h_escape)} glyphs escape their cell")
    for g in sorted(h_escape, key=chars.get)[: args.examples]:
        xs = [x for x, _ in pixels[g]]
        print(f"  {label(g)} ink cols {min(xs)}..{max(xs)} (cell 0..{cells(g) * adv - 1})")
    print(f"horizontal pixel collisions: {len(h_pairs)} ordered pairs")
    for a, b, side in h_pairs[: args.examples]:
        print(f"  {label(a)} then {label(b)}: overlapping pixels")

    # --- vertical ---
    v_top = {g for g, px in pixels.items() if any(y >= asc for _, y in px)}
    v_bot = {g for g, px in pixels.items() if any(y < -desc for _, y in px)}
    v_pairs = []
    for b in v_top:  # b on the lower line pokes up into the line of t
        up = {(x, y - line) for x, y in pixels[b] if y >= asc}
        for t, tpx in pixels.items():
            if up & tpx:
                v_pairs.append((t, b))
    for t in v_bot:  # t on the upper line pokes down into the line of b
        down = {(x, y + line) for x, y in pixels[t] if y < -desc}
        for b, bpx in pixels.items():
            if down & bpx:
                v_pairs.append((t, b))
    print(f"\nvertical: {len(v_top)} glyphs poke above ascent, {len(v_bot)} below descent")
    for g in sorted(v_top | v_bot, key=chars.get)[: args.examples]:
        ys = [y for _, y in pixels[g]]
        print(f"  {label(g)} ink rows {min(ys)}..{max(ys)} (box {-desc}..{asc - 1})")
    seen = sorted({(chars[t], chars[b]) for t, b in v_pairs})
    print(f"vertical pixel collisions: {len(seen)} (top,bottom) pairs")
    for ct, cb in seen[: args.examples]:
        print(f"  U+{ct:04X}({chr(ct)}) over U+{cb:04X}({chr(cb)})")

    # --- box drawing continuity ---
    def gid_of(cp):
        g = face.get_char_index(cp)
        return g if g and g in pixels else None
    issues = []
    for cp, kind in ((0x2500, "h"), (0x2502, "v"), (0x2588, "hv")):
        g = gid_of(cp)
        if g is None:
            continue
        px = pixels[g]
        if "h" in kind:
            missing = [x for x in range(adv) if not any(p[0] == x for p in px)]
            if missing:
                issues.append(f"U+{cp:04X} missing columns {missing} -> horizontal gaps")
        if "v" in kind:
            missing = [y for y in range(-desc, asc) if not any(p[1] == y for p in px)]
            if missing:
                issues.append(f"U+{cp:04X} missing rows {missing} -> vertical gaps between lines")
    print(f"\nbox drawing: {'OK' if not issues else ''}")
    for i in issues:
        print(f"  {i}")


if __name__ == "__main__":
    main()
