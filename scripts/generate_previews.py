#!/usr/bin/env python3
"""Generate README SVG font previews.

The SVGs contain glyph outlines, so GitHub can render the preview without
loading local fonts or custom CSS.
"""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
import uharfbuzz as hb

PHRASE = "Sphinx of black quartz, judge my vow."
FONT_EXTS = {".ttf", ".otf"}
DEFAULT_README = Path("README.md")
README_SECTION_HEADING = "## Previews"


def safe_id(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", text).strip("-")


def name_record(font: TTFont, name_id: int) -> str | None:
    table = font.get("name")
    if not table:
        return None
    for record in table.names:
        if record.nameID == name_id:
            try:
                value = record.toUnicode().strip()
            except Exception:
                continue
            if value:
                return value
    return None


def font_label(font: TTFont, fallback: str) -> str:
    family = name_record(font, 1)
    subfamily = name_record(font, 2)
    full = name_record(font, 4)
    if family and subfamily and subfamily.lower() != "regular":
        return f"{family} {subfamily}"
    return full or family or fallback


def glyph_bounds(glyph_set, glyph_name: str):
    pen = BoundsPen(glyph_set)
    glyph_set[glyph_name].draw(pen)
    return pen.bounds


def shape_text(font_path: Path, font: TTFont, text: str):
    """Shape text with HarfBuzz so GSUB/GPOS features like Sonic `calt` apply."""
    font_data = font_path.read_bytes()
    face = hb.Face(font_data)
    hb_font = hb.Font(face)
    units_per_em = font["head"].unitsPerEm
    hb_font.scale = (units_per_em, units_per_em)
    hb.ot_font_set_funcs(hb_font)

    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    hb.shape(hb_font, buffer, {"calt": True, "kern": True, "liga": True})

    glyph_order = font.getGlyphOrder()
    shaped = []
    for info, pos in zip(buffer.glyph_infos, buffer.glyph_positions):
        glyph_name = glyph_order[info.codepoint] if info.codepoint < len(glyph_order) else ".notdef"
        shaped.append((glyph_name, pos.x_advance, pos.y_advance, pos.x_offset, pos.y_offset))
    return shaped


def make_preview(font_path: Path, out_path: Path, text: str, font_size: int) -> tuple[str, str]:
    font = TTFont(font_path)
    glyph_set = font.getGlyphSet()
    units_per_em = font["head"].unitsPerEm
    scale = font_size / units_per_em
    label = font_label(font, font_path.stem)

    x_units = 0
    y_units = 0
    path_parts: list[str] = []
    bounds: list[tuple[float, float, float, float]] = []

    for glyph_name, x_advance, y_advance, x_offset, y_offset in shape_text(font_path, font, text):
        draw_x_units = x_units + x_offset
        draw_y_units = y_units + y_offset
        if glyph_name in glyph_set:
            pen = SVGPathPen(glyph_set)
            transform = (scale, 0, 0, -scale, draw_x_units * scale, -draw_y_units * scale)
            glyph_set[glyph_name].draw(TransformPen(pen, transform))
            commands = pen.getCommands()
            if commands:
                path_parts.append(commands)
                b = glyph_bounds(glyph_set, glyph_name)
                if b:
                    x_min, y_min, x_max, y_max = b
                    bounds.append(
                        (
                            (draw_x_units + x_min) * scale,
                            -(draw_y_units + y_max) * scale,
                            (draw_x_units + x_max) * scale,
                            -(draw_y_units + y_min) * scale,
                        )
                    )
        x_units += x_advance
        y_units += y_advance

    margin_x = 24
    margin_y = 20

    if bounds:
        min_x = min(b[0] for b in bounds)
        min_y = min(b[1] for b in bounds)
        max_x = max(b[2] for b in bounds)
        max_y = max(b[3] for b in bounds)
    else:
        min_x = min_y = 0
        max_x = max(x_units * scale, 1)
        max_y = font_size

    text_width = max(max_x - min_x, 1)
    text_height = max(max_y - min_y, 1)
    width = int(round(text_width + margin_x * 2))
    height = int(round(text_height + margin_y * 2))
    baseline_x = margin_x - min_x
    baseline_y = margin_y - min_y

    d = " ".join(path_parts)
    escaped_label = html.escape(label)
    escaped_text = html.escape(text)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">{escaped_label} preview</title>
  <desc id="desc">{escaped_text}</desc>
  <rect width="100%" height="100%" rx="10" fill="#0d1117"/>
  <g transform="translate({baseline_x:.2f} {baseline_y:.2f})" fill="#f0f6fc">
    <path d="{d}"/>
  </g>
</svg>
'''
    out_path.write_text(svg, encoding="utf-8")
    return label, out_path.as_posix()


def preview_table(rows: list[tuple[str, str, str]], image_width: int) -> str:
    return (
        "| Font | Preview |\n"
        "| --- | --- |\n"
        + "".join(
            f'| `{name}` | <img src="{path}" alt="{html.escape(label)} preview" width="{image_width}"> |\n'
            for name, label, path in rows
        )
    )


def readme_preview_section(rows: list[tuple[str, str, str]], text: str, image_width: int) -> str:
    return f"""{README_SECTION_HEADING}

GitHub README Markdown cannot load arbitrary local fonts for live text, so these previews are generated as standalone SVGs with HarfBuzz-shaped glyph outlines. That applies OpenType features such as the Sonic `calt` substitutions while keeping font names outside the images.

Preview phrase: “{text}”

Regenerate the SVGs and this README section with:

```bash
nix develop -c ./scripts/generate_previews.py
```

{preview_table(rows, image_width).rstrip()}
"""


def update_readme(readme_path: Path, section: str) -> None:
    if readme_path.exists():
        readme = readme_path.read_text(encoding="utf-8")
    else:
        readme = ""

    heading_re = re.compile(r"(?m)^## Previews\s*$")
    match = heading_re.search(readme)
    if match:
        next_heading = re.search(r"(?m)^## ", readme[match.end():])
        end = match.end() + next_heading.start() if next_heading else len(readme)
        updated = readme[:match.start()] + section.rstrip() + "\n\n" + readme[end:].lstrip("\n")
    else:
        separator = "\n\n" if readme and not readme.endswith("\n\n") else ""
        updated = readme + separator + section.rstrip() + "\n"

    readme_path.write_text(updated, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fonts-dir", default="fonts", type=Path)
    parser.add_argument("--out-dir", default="assets/previews", type=Path)
    parser.add_argument("--readme", default=DEFAULT_README, type=Path)
    parser.add_argument("--no-readme", action="store_true", help="Only write SVGs/snippet; do not update README.md")
    parser.add_argument("--text", default=PHRASE)
    parser.add_argument("--font-size", default=34, type=int)
    parser.add_argument("--image-width", default=720, type=int, help="README <img> width")
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    font_paths = sorted(p for p in args.fonts_dir.iterdir() if p.suffix.lower() in FONT_EXTS)
    if not font_paths:
        raise SystemExit(f"No fonts found in {args.fonts_dir}")

    rows = []
    for font_path in font_paths:
        out_path = args.out_dir / f"{safe_id(font_path.stem)}.svg"
        label, svg_path = make_preview(font_path, out_path, args.text, args.font_size)
        rows.append((font_path.name, label, svg_path))
        print(f"wrote {svg_path}")

    manifest = args.out_dir / "README-snippet.md"
    manifest.write_text(preview_table(rows, args.image_width), encoding="utf-8")
    print(f"wrote {manifest.as_posix()}")

    if not args.no_readme:
        update_readme(args.readme, readme_preview_section(rows, args.text, args.image_width))
        print(f"updated {args.readme.as_posix()}")


if __name__ == "__main__":
    main()
