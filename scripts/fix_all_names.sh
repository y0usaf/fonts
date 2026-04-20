#!/usr/bin/env bash
# Rewrite font metadata in fonts/*.ttf to be consistent.
set -euo pipefail
cd "$(dirname "$0")"

F=../fonts
fix() { uv run python fix_font_names.py "$F/$1" --family "$2" --subfamily "$3"; }

fix Fast_AtkinsonHyperlegibleMono.ttf    "Fast Atkinson Hyperlegible Mono" Regular
fix Fast_GoMono.ttf                      "Fast Go Mono"                    Regular
fix Fast_IosevkaSlab.ttf                 "Fast Iosevka Term Slab"          Regular
fix Fast_IosevkaTermSlabCompact.ttf      "Fast Iosevka Term Slab Compact"  Regular
fix Fast_IosevkaTermSlabCompact_Italic.ttf "Fast Iosevka Term Slab Compact" Italic
fix Fast_Terminus.ttf                    "Fast Terminus"                   Regular
fix Pixel_IosevkaSlab_24.ttf             "Pixel Iosevka Slab 24"           Regular
fix IosevkaTermSlabCompact-Light.ttf     "Iosevka Term Slab Compact"       "Light"
fix IosevkaTermSlabCompact-LightItalic.ttf "Iosevka Term Slab Compact"     "Light Italic"
fix IosevkaTermSlabCompact-Regular.ttf   "Iosevka Term Slab Compact"       Regular
fix IosevkaTermSlabCompact-Italic.ttf    "Iosevka Term Slab Compact"       Italic
fix IosevkaTermSlabCompact-Bold.ttf      "Iosevka Term Slab Compact"       Bold
fix IosevkaTermSlabCompact-BoldItalic.ttf "Iosevka Term Slab Compact"      "Bold Italic"
