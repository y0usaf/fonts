#!/usr/bin/env python3
"""
fix_font_names.py — normalize font naming metadata.

Writes nameIDs 1, 2, 3, 4, 5, 6, 16, 17, 18, 21, 22, syncs fsSelection
(OS/2), macStyle (head), and italicAngle (post).

Supports both RIBBI styles and non-RIBBI weights like Light/Light Italic.
For non-RIBBI styles, nameIDs 1/2 are generated as compatible family/style
names, while nameIDs 16/17 and 21/22 carry the typographic family/style.

Usage:
  fix_font_names.py <font.ttf> --family "Fast Go Mono" --subfamily Regular
  fix_font_names.py <font.ttf> --family "Fast Iosevka Term Slab Compact" --subfamily Italic
  fix_font_names.py <font.ttf> --family "Iosevka Term Slab Compact" --subfamily "Light Italic"
  fix_font_names.py <font.ttf> --family "Pixel Iosevka Slab 24" --subfamily Regular --version 1.000
"""
from argparse import ArgumentParser
from fontTools.ttLib import TTFont
import re
import sys


WIN_RECORD = (3, 1, 0x0409)   # Windows, Unicode BMP, en-US
MAC_RECORD = (1, 0, 0)        # Macintosh Roman, English
NAME_RECORDS = (WIN_RECORD, MAC_RECORD)

RIBBI = {"Regular", "Italic", "Bold", "Bold Italic"}
VALID = {
    "Thin", "Thin Italic",
    "Extra Light", "Extra Light Italic",
    "Light", "Light Italic",
    "Regular", "Italic",
    "Medium", "Medium Italic",
    "Semi Bold", "Semi Bold Italic",
    "Bold", "Bold Italic",
    "Extra Bold", "Extra Bold Italic",
    "Black", "Black Italic",
}
MANAGED_NAME_IDS = {1, 2, 3, 4, 5, 6, 16, 17, 18, 21, 22}


def best_name(name_table, name_id: int) -> str | None:
    """Get the best available value for name_id, preferring Windows en-US."""
    preferred = [
        lambda r: r.nameID == name_id and (r.platformID, r.platEncID, r.langID) == WIN_RECORD,
        lambda r: r.nameID == name_id and r.platformID == 3,
        lambda r: r.nameID == name_id and (r.platformID, r.platEncID, r.langID) == MAC_RECORD,
        lambda r: r.nameID == name_id,
    ]
    for want in preferred:
        for record in name_table.names:
            if want(record):
                try:
                    return record.toUnicode()
                except Exception:
                    return str(record.string)
    return None


def normalize_style_text(value: str) -> str:
    value = " ".join(value.strip().replace("_", " ").replace("-", " ").split())
    if not value:
        raise ValueError("Subfamily must be non-empty")
    parts = value.split()
    titled = []
    for part in parts:
        low = part.lower()
        if low == "semibold":
            titled.extend(["Semi", "Bold"])
        elif low == "extralight":
            titled.extend(["Extra", "Light"])
        elif low == "ultralight":
            titled.extend(["Ultra", "Light"])
        elif low == "extrabold":
            titled.extend(["Extra", "Bold"])
        elif low == "ultrabold":
            titled.extend(["Ultra", "Bold"])
        else:
            titled.append(part[0].upper() + part[1:].lower())
    return " ".join(titled)


def style_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def is_italic_style(subfamily: str) -> bool:
    key = style_key(subfamily)
    return "italic" in key or "oblique" in key


def italicless_subfamily(subfamily: str) -> str:
    return re.sub(r"\s+(Italic|Oblique)$", "", subfamily).strip()


def weight_class(subfamily: str) -> int:
    key = style_key(subfamily)
    for needles, value in [
        (("extrablack", "ultrablack"), 950),
        (("black", "heavy"), 900),
        (("extrabold", "ultrabold"), 800),
        (("semibold", "demibold"), 600),
        (("bold",), 700),
        (("medium",), 500),
        (("book", "regular", "normal"), 400),
        (("extralight", "ultralight"), 200),
        (("light",), 300),
        (("thin",), 100),
    ]:
        if any(needle in key for needle in needles):
            return value
    return 400


def compatibility_names(family: str, subfamily: str) -> tuple[str, str]:
    if subfamily in RIBBI:
        return family, subfamily

    base = italicless_subfamily(subfamily)
    compat_family = family if not base or base == "Regular" else f"{family} {base}"
    compat_subfamily = "Italic" if is_italic_style(subfamily) else "Regular"
    return compat_family, compat_subfamily


def normalize_version_text(value: str | None) -> str:
    text = " ".join((value or "").strip().split())
    if not text:
        return "Version 1.000"
    return text if text.lower().startswith("version ") else f"Version {text}"


def version_name(font, override: str | None = None) -> str:
    if override is not None:
        return normalize_version_text(override)

    existing = best_name(font["name"], 5) if "name" in font else None
    if existing:
        return normalize_version_text(existing)

    revision = getattr(font["head"], "fontRevision", 1.0) if "head" in font else 1.0
    return f"Version {revision:.3f}"


def postscript_name(family: str, subfamily: str) -> str:
    base = re.sub(r"[^\w]", "", family)
    if subfamily == "Regular":
        return base
    return f"{base}-{subfamily.replace(' ', '')}"


def full_name(family: str, subfamily: str) -> str:
    return family if subfamily == "Regular" else f"{family} {subfamily}"


def unique_name(full: str, version: str) -> str:
    version_tail = re.sub(r"(?i)^version\s+", "", version).strip()
    return full if not version_tail else f"{full} {version_tail}"


def set_name(name_table, name_id: int, value: str):
    """Set (or add) a name record for Windows + Mac platforms."""
    for plat, enc, lang in NAME_RECORDS:
        name_table.setName(value, name_id, plat, enc, lang)


def drop_stale(name_table, keep_ids):
    """Remove managed name records we're about to rewrite."""
    name_table.names = [
        r for r in name_table.names
        if r.nameID not in MANAGED_NAME_IDS or r.nameID in keep_ids
    ]


def update_os2_head_post(font, subfamily: str):
    italic = is_italic_style(subfamily)
    weight = weight_class(subfamily)
    bold = weight >= 700

    if "OS/2" in font:
        os2 = font["OS/2"]
        fs = os2.fsSelection
        fs &= ~((1 << 0) | (1 << 5) | (1 << 6))   # clear Italic, Bold, Regular
        if italic:
            fs |= 1 << 0
        if bold:
            fs |= 1 << 5
        if not italic and not bold:
            fs |= 1 << 6   # non-bold upright face
        if getattr(os2, "version", 0) >= 4:
            fs |= 1 << 7   # UseTypoMetrics
        else:
            fs &= ~((1 << 7) | (1 << 8) | (1 << 9))
        os2.fsSelection = fs
        os2.usWeightClass = weight

    if "head" in font:
        head = font["head"]
        ms = head.macStyle
        ms &= ~((1 << 0) | (1 << 1))   # clear Bold, Italic
        if bold:
            ms |= 1 << 0
        if italic:
            ms |= 1 << 1
        head.macStyle = ms

    if "post" in font:
        post = font["post"]
        current_angle = float(getattr(post, "italicAngle", 0.0) or 0.0)
        post.italicAngle = current_angle if italic and current_angle != 0.0 else (-9.0 if italic else 0.0)


def normalize_font_metadata(font, family: str, subfamily: str, *, version: str | None = None):
    if not family or not family.strip():
        raise ValueError("Family must be non-empty")
    if "name" not in font:
        raise KeyError("No name table")

    family = " ".join(family.strip().split())
    subfamily = normalize_style_text(subfamily)

    compat_family, compat_subfamily = compatibility_names(family, subfamily)
    resolved_version = version_name(font, override=version)
    ps = postscript_name(family, subfamily)
    full = full_name(family, subfamily)
    unique = unique_name(full, resolved_version)

    nt = font["name"]
    drop_stale(nt, keep_ids=set())

    values = {
        1: compat_family,
        2: compat_subfamily,
        3: unique,
        4: full,
        5: resolved_version,
        6: ps,
        16: family,
        17: subfamily,
        18: full,
        21: family,
        22: subfamily,
    }
    for name_id, value in values.items():
        set_name(nt, name_id, value)

    update_os2_head_post(font, subfamily)

    return {
        "family": compat_family,
        "subfamily": compat_subfamily,
        "typographic_family": family,
        "typographic_subfamily": subfamily,
        "full": full,
        "version": resolved_version,
        "unique": unique,
        "postscript": ps,
    }


def main():
    ap = ArgumentParser()
    ap.add_argument("font")
    ap.add_argument("--family", required=True,
                    help="Typographic family name (nameID 16/21; also 1 for RIBBI styles)")
    ap.add_argument("--subfamily", required=True,
                    help="Typographic style/subfamily, e.g. Regular, Italic, Light, Light Italic")
    ap.add_argument("--version",
                    help="Version string for nameID 5; accepts '1.000' or 'Version 1.000'")
    ap.add_argument("-o", "--output",
                    help="Write to this path instead of overwriting")
    args = ap.parse_args()

    font = TTFont(args.font)
    if "name" not in font:
        print("No name table", file=sys.stderr)
        sys.exit(2)

    try:
        meta = normalize_font_metadata(font, args.family, args.subfamily, version=args.version)
    except (KeyError, ValueError) as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)

    out = args.output or args.font
    font.save(out)
    font.close()

    print(f"✓ {args.font}")
    print(f"    Family       : {meta['family']}")
    print(f"    Subfamily    : {meta['subfamily']}")
    print(f"    Typographic  : {meta['typographic_family']} / {meta['typographic_subfamily']}")
    print(f"    Full         : {meta['full']}")
    print(f"    Version      : {meta['version']}")
    print(f"    Unique       : {meta['unique']}")
    print(f"    PostScript   : {meta['postscript']}")


if __name__ == "__main__":
    main()
