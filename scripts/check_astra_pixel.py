#!/usr/bin/env python3
"""Fail on raster/source differences, cell escapes, aliases or broken box joins.

JSON on stdout is the measurement report. Native grayscale and monochrome
FreeType rasterization must exactly reproduce the editable source at 1/2/3x.
"""
import json
from pathlib import Path
import freetype
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from build_astra_pixel import ROOT, SOURCE, drawings, boxes


def raster(face, cp, mono):
    face.load_char(chr(cp), freetype.FT_LOAD_RENDER | (
        freetype.FT_LOAD_TARGET_MONO if mono else freetype.FT_LOAD_TARGET_NORMAL))
    g = face.glyph
    bm = g.bitmap
    pixels, shades = set(), set()
    for row in range(bm.rows):
        for col in range(bm.width):
            value = ((bm.buffer[row * bm.pitch + col // 8] >> (7 - col % 8)) & 1) * 255 if mono else bm.buffer[row * bm.pitch + col]
            shades.add(value)
            if value:
                pixels.add((g.bitmap_left + col, g.bitmap_top - row - 1))
    return pixels, shades


def measure(path, ppem):
    face = freetype.Face(str(path))
    face.set_pixel_sizes(0, ppem)
    advances = set()
    bounds = set()
    caps = set()
    lower = set()
    for cp in range(32, 127):
        px, _ = raster(face, cp, True)
        advances.add(face.glyph.advance.x / 64)
        bounds |= px
        if cp == ord("H"):
            caps = px
        if cp == ord("x"):
            lower = px
    assert len(advances) == 1, (path, advances)
    advance = advances.pop()
    height = face.size.height / 64
    columns, rows = int(640 // advance), int(330 // height)
    return {"file": str(path.relative_to(ROOT)), "ppem": ppem, "advance": advance,
            "line": height, "columns": columns, "rows": rows, "characters": columns * rows,
            "cap_ink_height": max(y for x, y in caps) - min(y for x, y in caps) + 1,
            "x_ink_height": max(y for x, y in lower) - min(y for x, y in lower) + 1,
            "ascii_ink_y": [min(y for x, y in bounds), max(y for x, y in bounds)]}


def main():
    report = [measure(ROOT / "fonts/departure-mono/DepartureMonoUltraCondensedCompact-Regular.ttf", 11)]
    for preset in ("Tight", "Balanced", "Open"):
        report.append(measure(ROOT / f"fonts/pixel-mono/PixelMono{preset}-Regular.ttf", 11))
    for name, config in json.loads((SOURCE / "families.json").read_text()).items():
        path = ROOT / "fonts/astra-pixel" / ("AstraPixel-Regular.ttf" if name == "Text" else f"AstraPixel{name}-Regular.ttf")
        font = TTFont(path)
        expected = drawings(config) | boxes(config["advance"], config["ascent"], config["descent"])
        assert set(expected) == set(font.getBestCmap())
        assert set(a for a, lsb in font["hmtx"].metrics.values()) == {config["advance"] * 64}
        ascii_pixels = {cp: frozenset(expected[cp]) for cp in range(32, 127)}
        aliases = [(chr(a), chr(b)) for a in ascii_pixels for b in ascii_pixels
                   if a < b and ascii_pixels[a] == ascii_pixels[b]]
        assert not aliases, (name, "ASCII aliases", aliases)
        for cp, px in expected.items():
            assert all(0 <= x < config["advance"] and -config["descent"] <= y < config["ascent"] for x, y in px), (name, cp, "escape")
            if cp < 127:
                assert all(x < config["advance"] - 1 and y < config["ascent"] - 1 for x, y in px), (name, cp, "missing separator")
        # Confinement plus a blank final column/top row proves all ASCII pairs
        # have no ink collision or edge contact, horizontally and vertically.
        for zoom in (1, 2, 3):
            face = freetype.Face(str(path))
            face.set_pixel_sizes(0, config["ppem"] * zoom)
            for mono in (False, True):
                for cp, px in expected.items():
                    actual, shades = raster(face, cp, mono)
                    scaled = {(x * zoom + dx, y * zoom + dy) for x, y in px
                              for dx in range(zoom) for dy in range(zoom)}
                    assert actual == scaled, (name, cp, zoom, mono, "raster differs")
                    assert not shades - {0, 255}, (name, cp, "gray edge")
                    assert face.glyph.advance.x == config["advance"] * zoom * 64
        for cp in (0x2500, 0x2502):
            px = expected[cp]
            if cp == 0x2500:
                assert {x for x, y in px} == set(range(config["advance"]))
            else:
                assert {y for x, y in px} == set(range(-config["descent"], config["ascent"]))
        hfont = hb.Font(hb.Face(path.read_bytes()))
        buffer = hb.Buffer()
        sample = "".join(chr(cp) for cp in expected)
        buffer.add_str(sample)
        buffer.guess_segment_properties()
        hb.shape(hfont, buffer)
        assert len(buffer.glyph_infos) == len(sample)
        assert all(g.codepoint for g in buffer.glyph_infos)
        assert all(p.x_advance == config["advance"] * 64 and p.y_advance == p.x_offset == p.y_offset == 0 for p in buffer.glyph_positions)
        report.append(measure(path, config["ppem"]))
    print(json.dumps({"viewport": [640, 330], "fonts": report}, indent=2))


if __name__ == "__main__":
    main()
