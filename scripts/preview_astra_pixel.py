#!/usr/bin/env python3
"""Embed measured fonts and an offline comparison UI into one HTML file."""
import base64
import html
import json
from fontTools.ttLib import TTFont
from build_astra_pixel import ROOT, SOURCE


def main():
    directory = ROOT / "assets/previews/astra-pixel"
    metrics = json.loads((directory / "metrics.json").read_text())
    items = metrics["fonts"]
    for i, item in enumerate(items):
        path = ROOT / item["file"]
        font = TTFont(path)
        item["name"] = font["name"].getDebugName(1)
        item["id"] = f"proof{i}"
        item["ascent"] = round(font["hhea"].ascent * item["ppem"] / font["head"].unitsPerEm)
        item["cmap"] = list(font.getBestCmap())
        item["data"] = base64.b64encode(path.read_bytes()).decode()
    template = (SOURCE / "comparison.html").read_text()
    directory.mkdir(parents=True, exist_ok=True)
    license_text = (ROOT / "fonts/pixel-mono/LICENSE").read_text()
    template = template.replace("<!-- REFERENCE_LICENSE -->", html.escape(license_text))
    (directory / "comparison.html").write_text(template.replace("/* FONT_DATA */[]", json.dumps(items)))


if __name__ == "__main__":
    main()
