#!/usr/bin/env python3
"""Build fixed-pitch pixel fonts from editable masks and a TOML build plan."""
from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
import re
import tomllib

from fontTools.fontBuilder import FontBuilder
from fontTools.ttLib.tables.O_S_2f_2 import Panose

from pixelize import UNITS_PER_PIXEL as U, build_glyph

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'sources/pixel-mono'
COPYRIGHT = 'Copyright 2022–2024 Helena Zhang. Modifications copyright 2026 y0usaf.'


def masks(data):
    if set(data) != set(map(chr, range(32, 127))):
        raise ValueError('Glyph source must contain exactly printable ASCII (32–126)')
    result = {}
    for char, rows in data.items():
        if (len(rows) != 11 or any(len(row) != 5 or set(row) - {'.', '#'} for row in rows)):
            raise ValueError(f'{char!r}: expected eleven rows of five . or # pixels')
        pixels = {(x, 8 - row) for row, line in enumerate(rows)
                  for x, value in enumerate(line) if value == '#'}
        if bool(pixels) != (char != ' '):
            raise ValueError(f'{char!r}: only space may be empty')
        result[char] = pixels
    return result


def resolve(base, plan):
    expected = {'family', 'letter_gap', 'line_gap', 'zero', 'ell'}
    if set(plan) != expected:
        raise ValueError(f'Plan keys must be {sorted(expected)}')
    if not isinstance(plan['family'], str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9 ]{0,60}', plan['family']):
        raise ValueError('Family must be 1–61 ASCII letters, digits or spaces, starting with a letter')
    for key, low, high in [('letter_gap', 1, 3), ('line_gap', 0, 4)]:
        if type(plan[key]) is not int or not low <= plan[key] <= high:
            raise ValueError(f'{key} must be an integer in {low}..{high}')
    if plan['zero'] not in {'slashed', 'dotted', 'plain'}:
        raise ValueError('zero must be slashed, dotted or plain')
    if plan['ell'] not in {'serifed', 'tailed'}:
        raise ValueError('ell must be serifed or tailed')
    glyphs = {c: set(p) for c, p in base.items()}
    # Preserve the bowl; replace only the interior of the zero.
    if plan['zero'] != 'slashed':
        glyphs['0'] -= {(x, y) for x in range(1, 4) for y in range(1, 7)}
        if plan['zero'] == 'dotted':
            glyphs['0'].add((2, 3))
    if plan['ell'] == 'tailed':
        glyphs['l'] = {(2, y) for y in range(1, 8)} | {(3, 0), (4, 0)}
    return glyphs


def build(glyphs, plan, output):
    advance = (5 + plan['letter_gap']) * U
    ascent, descent = (9 + plan['line_gap']) * U, 2 * U
    names = {c: f'uni{ord(c):04X}' for c in glyphs}
    notdef = {(x, y) for x in range(5) for y in range(8)
              if x in (0, 4) or y in (0, 7)}
    all_glyphs = {'.notdef': notdef, **{names[c]: p for c, p in glyphs.items()}}
    fb = FontBuilder(11 * U, isTTF=True)
    fb.setupGlyphOrder(list(all_glyphs))
    fb.setupCharacterMap({ord(c): n for c, n in names.items()})
    fb.setupGlyf({n: build_glyph(p, advance // U, None) for n, p in all_glyphs.items()})
    fb.setupHorizontalMetrics({n: (advance, min((x for x, y in p), default=0) * U)
                               for n, p in all_glyphs.items()})
    fb.setupHorizontalHeader(ascent=ascent, descent=-descent, lineGap=0)
    family = plan['family']
    ps = family.replace(' ', '') + '-Regular'
    fb.setupNameTable(dict(familyName=family, styleName='Regular',
                          fullName=family + ' Regular', psName=ps,
                          uniqueFontIdentifier=ps + ';0.100', version='Version 0.100',
                          copyright=COPYRIGHT,
                          licenseDescription='SIL Open Font License, Version 1.1',
                          licenseInfoURL='https://openfontlicense.org'))
    panose = Panose()
    panose.bFamilyType, panose.bProportion = 2, 9
    fb.setupOS2(version=4, sTypoAscender=ascent, sTypoDescender=-descent, sTypoLineGap=0,
                usWinAscent=ascent, usWinDescent=descent, xAvgCharWidth=advance,
                panose=panose, fsSelection=0xC0, usWeightClass=400, usWidthClass=5)
    fb.setupPost(isFixedPitch=1)
    fb.font['head'].lowestRecPPEM = 11
    # Stable output, independent of the build clock.
    fb.font['head'].created = fb.font['head'].modified = 3850416000
    fb.font.recalcTimestamp = False
    output.parent.mkdir(parents=True, exist_ok=True)
    fb.save(output)


def specimen(entries, output):
    """Standalone interactive specimen: real fonts plus exact pixel construction."""
    fonts = []
    for item in entries:
        item = dict(item)
        item['data'] = base64.b64encode(item.pop('path').read_bytes()).decode()
        fonts.append(item)
    template = (SOURCE / 'specimen.html').read_text()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(template.replace('/* FONT_DATA */', json.dumps(fonts)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plans', type=Path, default=SOURCE / 'build-plans.toml')
    parser.add_argument('--glyphs', type=Path, default=SOURCE / 'glyphs.json')
    parser.add_argument('--out', type=Path, default=ROOT / 'fonts/pixel-mono')
    parser.add_argument('--specimen', type=Path, default=ROOT / 'assets/previews/pixel-mono/specimen.html')
    args = parser.parse_args()
    try:
        config = tomllib.loads(args.plans.read_text())
        if set(config) != {'plans'} or not config['plans']:
            raise ValueError('Expected a nonempty [plans] table')
        base = masks(json.loads(args.glyphs.read_text()))
        resolved = []
        for name, plan in config['plans'].items():
            if not re.fullmatch('[a-z][a-z0-9_-]*', name):
                raise ValueError(f'Invalid plan identifier: {name}')
            resolved.append((name, plan, resolve(base, plan)))
        families = [plan['family'].replace(' ', '') for _, plan, _ in resolved]
        if len(set(families)) != len(families):
            raise ValueError('Plans must have distinct font family/PostScript names')
    except (ValueError, TypeError, KeyError) as error:
        parser.error(str(error))
    entries = []
    for name, plan, glyphs in resolved:
        path = args.out / (plan['family'].replace(' ', '') + '-Regular.ttf')
        build(glyphs, plan, path)
        entries.append(dict(label=plan['family'], path=path,
                            advance=5 + plan['letter_gap'], line=11 + plan['line_gap']))
    entries.insert(0, dict(label='Departure Mono · original',
                          path=ROOT / 'fonts/departure-mono/DepartureMono-Regular.ttf',
                          advance=7, line=14))
    entries.insert(1, dict(label='Departure Mono · existing ultra compact',
                          path=ROOT / 'fonts/departure-mono/DepartureMonoUltraCondensedCompact-Regular.ttf',
                          advance=5, line=11))
    specimen(entries, args.specimen)


if __name__ == '__main__':
    main()
