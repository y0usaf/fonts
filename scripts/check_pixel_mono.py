#!/usr/bin/env python3
"""Check generated fonts through FreeType and HarfBuzz, not only font tables."""
import hashlib
import json
from pathlib import Path
import tempfile
import tomllib
import unittest

import freetype
from fontTools.ttLib import TTFont
import uharfbuzz as hb

from build_pixel_mono import SOURCE, U, build, masks, resolve
from pixelize import LOAD_FLAGS, bitmap_pixels


class PixelMonoChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = masks(json.loads((SOURCE / 'glyphs.json').read_text()))
        cls.plans = tomllib.loads((SOURCE / 'build-plans.toml').read_text())['plans']

    def test_font_roundtrip_and_rendering(self):
        with tempfile.TemporaryDirectory() as directory:
            for name, plan in self.plans.items():
                with self.subTest(plan=name):
                    glyphs = resolve(self.base, plan)
                    path = Path(directory) / 'font.ttf'
                    build(glyphs, plan, path)
                    first = hashlib.sha256(path.read_bytes()).digest()
                    build(glyphs, plan, path)
                    self.assertEqual(first, hashlib.sha256(path.read_bytes()).digest())
                    font = TTFont(path)
                    advance = (5 + plan['letter_gap']) * U
                    self.assertEqual({a for a, _ in font['hmtx'].metrics.values()}, {advance})
                    self.assertEqual(set(font.getBestCmap()), set(range(32, 127)))
                    self.assertEqual(font['post'].isFixedPitch, 1)
                    self.assertEqual(font['hhea'].ascent-font['hhea'].descent,
                                     (11+plan['line_gap'])*U)
                    self.assertNotIn('kern', font)
                    self.assertNotIn('GPOS', font)
                    self.assertNotIn('GSUB', font)
                    face = freetype.Face(str(path))
                    for scale in (1, 2):
                        face.set_pixel_sizes(0, 11*scale)
                        for char, pixels in glyphs.items():
                            face.load_char(char, LOAD_FLAGS)
                            actual = bitmap_pixels(face.glyph)
                            expected = {(x*scale+dx, y*scale+dy) for x,y in pixels
                                        for dx in range(scale) for dy in range(scale)}
                            self.assertEqual(actual, expected, (name, char, scale))
                            self.assertEqual(face.glyph.advance.x, advance*scale)
                            self.assertTrue(all(0 <= x < (5+plan['letter_gap'])*scale
                                                and -2*scale <= y < (9+plan['line_gap'])*scale
                                                for x,y in actual))
                    shaped_font = hb.Font(hb.Face(path.read_bytes()))
                    shaped_font.scale = (11*U, 11*U)
                    hb.ot_font_set_funcs(shaped_font)
                    buffer = hb.Buffer()
                    buffer.add_str(''.join(map(chr, range(32,127))))
                    buffer.guess_segment_properties()
                    hb.shape(shaped_font, buffer, {'kern': True, 'liga': True})
                    self.assertEqual(len(buffer.glyph_infos), 95)
                    self.assertEqual({(p.x_advance,p.y_advance,p.x_offset,p.y_offset)
                                      for p in buffer.glyph_positions}, {(advance,0,0,0)})
                    for pair in [('0','O'),('1','I'),('I','l'),('l','|')]:
                        self.assertNotEqual(glyphs[pair[0]],glyphs[pair[1]])

    def test_variants_and_rejected_plans(self):
        plan = self.plans['balanced']
        for zero in ('slashed','dotted','plain'):
            for ell in ('serifed','tailed'):
                glyphs = resolve(self.base, dict(plan, zero=zero, ell=ell))
                self.assertTrue(glyphs['0'] and glyphs['l'])
        for change in ({'letter_gap':0},{'letter_gap':1.5},{'line_gap':-1},
                       {'zero':'unknown'},{'ell':'unknown'},{'typo':1},{'line_gap':True}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                resolve(self.base, dict(plan, **change))
        with self.assertRaises(ValueError):
            masks({'A':['#####']})


if __name__ == '__main__':
    unittest.main()
