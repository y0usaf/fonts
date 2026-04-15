#!/usr/bin/env bash
# Produce Fast_IosevkaTermSlabCompact.ttf (+ italic) from the Iosevka build,
# then fix naming to OpenType conventions.

set -euo pipefail
cd "$(dirname "$0")"

SRC="../tmp/iosevka/dist/IosevkaTermSlabCompact/TTF"
OUT="../fonts"
BOLD_SCALE_X="${BOLD_SCALE_X:-1.23}"

mkdir -p "$OUT"

echo "== Upright → Fast_IosevkaTermSlabCompact.ttf =="
uv run python make_fast_font.py \
  "$SRC/IosevkaTermSlabCompact-Regular.ttf" \
  "$SRC/IosevkaTermSlabCompact-Bold.ttf" \
  --bold-scale-x "$BOLD_SCALE_X" \
  -o "$OUT/Fast_IosevkaTermSlabCompact.ttf"
uv run python fix_font_names.py "$OUT/Fast_IosevkaTermSlabCompact.ttf" \
  --family "Fast Iosevka Term Slab Compact" --subfamily Regular

echo
echo "== Italic → Fast_IosevkaTermSlabCompact_Italic.ttf =="
uv run python make_fast_font.py \
  "$SRC/IosevkaTermSlabCompact-Italic.ttf" \
  "$SRC/IosevkaTermSlabCompact-BoldItalic.ttf" \
  --bold-scale-x "$BOLD_SCALE_X" \
  -o "$OUT/Fast_IosevkaTermSlabCompact_Italic.ttf"
uv run python fix_font_names.py "$OUT/Fast_IosevkaTermSlabCompact_Italic.ttf" \
  --family "Fast Iosevka Term Slab Compact" --subfamily Italic

echo
echo "== Copy plain (non-Fast) Iosevka TTFs alongside (Iosevka naming is already correct) =="
install -m644 "$SRC/IosevkaTermSlabCompact-Light.ttf"       "$OUT/IosevkaTermSlabCompact-Light.ttf"
install -m644 "$SRC/IosevkaTermSlabCompact-LightItalic.ttf" "$OUT/IosevkaTermSlabCompact-LightItalic.ttf"
install -m644 "$SRC/IosevkaTermSlabCompact-Regular.ttf"     "$OUT/IosevkaTermSlabCompact-Regular.ttf"
install -m644 "$SRC/IosevkaTermSlabCompact-Italic.ttf"      "$OUT/IosevkaTermSlabCompact-Italic.ttf"
install -m644 "$SRC/IosevkaTermSlabCompact-Bold.ttf"        "$OUT/IosevkaTermSlabCompact-Bold.ttf"
install -m644 "$SRC/IosevkaTermSlabCompact-BoldItalic.ttf"  "$OUT/IosevkaTermSlabCompact-BoldItalic.ttf"

echo
ls -lh "$OUT/"*IosevkaTermSlabCompact*.ttf
echo
echo "Done. Don't forget to 'git add fonts/' so the flake picks them up."
