#!/usr/bin/env python3
"""
fix_font_names.py — set all the font-name fields consistently.

Writes nameIDs 1, 2, 4, 6, 16, 17, syncs fsSelection (OS/2), macStyle (head),
and italicAngle (post). Handles Regular / Italic / Bold / Bold Italic.

Usage:
  fix_font_names.py <font.ttf> --family "Fast Go Mono" --subfamily Regular
  fix_font_names.py <font.ttf> --family "Fast Iosevka Term Slab Compact" --subfamily Italic
"""
from argparse import ArgumentParser
from fontTools.ttLib import TTFont
import sys, re


WIN_RECORD = (3, 1, 0x0409)   # Windows, Unicode BMP, en-US
MAC_RECORD = (1, 0, 0)        # Macintosh Roman, English

VALID = {"Regular", "Italic", "Bold", "Bold Italic"}


def postscript_name(family: str, subfamily: str) -> str:
    base = re.sub(r"[^\w]", "", family)
    if subfamily == "Regular":
        return base
    return f"{base}-{subfamily.replace(' ', '')}"


def full_name(family: str, subfamily: str) -> str:
    return family if subfamily == "Regular" else f"{family} {subfamily}"


def set_name(name_table, name_id: int, value: str):
    """Set (or add) a name record for Windows + Mac platforms."""
    for plat, enc, lang in (WIN_RECORD, MAC_RECORD):
        name_table.setName(value, name_id, plat, enc, lang)


def drop_stale(name_table, keep_ids):
    """Remove any name records not in keep_ids, limited to the ids we manage."""
    managed = {1, 2, 3, 4, 6, 16, 17, 18, 21, 22}
    name_table.names = [
        r for r in name_table.names
        if r.nameID not in managed or r.nameID in keep_ids
    ]


def update_os2_head_post(font, subfamily: str):
    italic = "Italic" in subfamily
    bold   = "Bold" in subfamily

    # OS/2 fsSelection
    os2 = font["OS/2"]
    fs = os2.fsSelection
    fs &= ~((1 << 0) | (1 << 5) | (1 << 6))   # clear Italic, Bold, Regular
    if italic: fs |= 1 << 0
    if bold:   fs |= 1 << 5
    if not italic and not bold:
        fs |= 1 << 6   # Regular (mutually exclusive with Italic/Bold)
    fs |= 1 << 7      # UseTypoMetrics (makes TypoFamily/Subfamily authoritative)
    os2.fsSelection = fs
    # Weight class
    os2.usWeightClass = 700 if bold else 400

    # head.macStyle
    head = font["head"]
    ms = head.macStyle
    ms &= ~((1 << 0) | (1 << 1))   # clear Bold, Italic
    if bold:   ms |= 1 << 0
    if italic: ms |= 1 << 1
    head.macStyle = ms

    # post.italicAngle
    post = font["post"]
    post.italicAngle = -9.4 if italic else 0.0


def main():
    ap = ArgumentParser()
    ap.add_argument("font")
    ap.add_argument("--family", required=True,
                    help="Family name (nameID 1 and 16)")
    ap.add_argument("--subfamily", required=True, choices=sorted(VALID),
                    help="Style: Regular, Italic, Bold, or Bold Italic")
    ap.add_argument("-o", "--output",
                    help="Write to this path instead of overwriting")
    args = ap.parse_args()

    if args.subfamily not in VALID:
        print(f"Subfamily must be one of {sorted(VALID)}", file=sys.stderr); sys.exit(2)

    font = TTFont(args.font)
    if "name" not in font:
        print("No name table", file=sys.stderr); sys.exit(2)

    ps = postscript_name(args.family, args.subfamily)
    full = full_name(args.family, args.subfamily)

    nt = font["name"]
    # Drop stale records we're about to overwrite; keep everything else.
    drop_stale(nt, keep_ids=set())

    set_name(nt, 1,  args.family)
    set_name(nt, 2,  args.subfamily)
    set_name(nt, 4,  full)
    set_name(nt, 6,  ps)
    set_name(nt, 16, args.family)    # Typographic Family — same as 1 for 4-style families
    set_name(nt, 17, args.subfamily) # Typographic Subfamily — same as 2

    update_os2_head_post(font, args.subfamily)

    out = args.output or args.font
    font.save(out)
    font.close()

    print(f"✓ {args.font}")
    print(f"    Family       : {args.family}")
    print(f"    Subfamily    : {args.subfamily}")
    print(f"    Full         : {full}")
    print(f"    PostScript   : {ps}")


if __name__ == "__main__":
    main()
