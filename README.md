<h1 align="center">fonts</h1>

<p align="center">The fonts I use, packaged as a Nix flake with a preview of each.</p>

Each folder in `fonts/` is one family and one Nix package. Most are upstream fonts or remixes; Astra Pixel and Nib are original. "Sonic" variants add a contextual-alternates (`calt`) feature for faster reading.

## Install

```bash
nix profile install github:y0usaf/fonts              # every family
nix profile install github:y0usaf/fonts#commit-mono  # one family
nix flake show github:y0usaf/fonts                   # list families
```

## Astra Pixel

An original monospaced pixel font for dense code: a 5 × 10px cell at 10px, with printable ASCII and light box drawing. The package also holds three alternates: Facet, Loom and Reed.

[Download the TTF](fonts/astra-pixel/AstraPixel-Regular.ttf) ·
[Offline comparison](assets/previews/astra-pixel/comparison.html) ·
[Sources and design notes](sources/astra-pixel/README.md)

<img src="assets/previews/astra-pixel/AstraPixel-Regular.svg" alt="Astra Pixel Regular preview" width="720">

<!-- previews:start -->
<h2 align="center">⚡ Sonic Fonts ⚡</h2>

#### Atkinson Hyperlegible Mono Regular Sonic

<img src="assets/previews/atkinson-hyperlegible-mono/AtkinsonHyperlegibleMono-Regular-Sonic.svg?v=transparent-v2" alt="Atkinson Hyperlegible Mono Regular Sonic preview" width="720">

#### CommitMono 200 Italic Sonic

<img src="assets/previews/commit-mono/CommitMono-200-Italic-Sonic.svg?v=transparent-v2" alt="CommitMono 200 Italic Sonic preview" width="720">

#### CommitMono 200 Regular Sonic

<img src="assets/previews/commit-mono/CommitMono-200-Regular-Sonic.svg?v=transparent-v2" alt="CommitMono 200 Regular Sonic preview" width="720">

#### Go Mono Regular Sonic

<img src="assets/previews/go-mono/GoMono-Regular-Sonic.svg?v=transparent-v2" alt="Go Mono Regular Sonic preview" width="720">

#### Iosevka Term Slab Regular Sonic

<img src="assets/previews/iosevka-term-slab/IosevkaTermSlab-Regular-Sonic.svg?v=transparent-v2" alt="Iosevka Term Slab Regular Sonic preview" width="720">

#### Iosevka Term Slab Condensed Sonic Italic

<img src="assets/previews/iosevka-term-slab/IosevkaTermSlabCondensed-Italic-Sonic.svg?v=transparent-v2" alt="Iosevka Term Slab Condensed Sonic Italic preview" width="720">

#### Iosevka Term Slab Condensed Sonic

<img src="assets/previews/iosevka-term-slab/IosevkaTermSlabCondensed-Regular-Sonic.svg?v=transparent-v2" alt="Iosevka Term Slab Condensed Sonic preview" width="720">

#### RuneScape Regular Sonic

<img src="assets/previews/runescape/RuneScape-Regular-Sonic.svg?v=transparent-v2" alt="RuneScape Regular Sonic preview" width="720">

#### Terminus Regular Sonic

<img src="assets/previews/terminus/Terminus-Regular-Sonic.svg?v=transparent-v2" alt="Terminus Regular Sonic preview" width="720">

<h2 align="center">🍉 Regular Fonts 🍉</h2>

#### my 3x5 tiny mono pixel font Regular

<img src="assets/previews/another-tiny-pixel-font-mono/AnotherTinyPixelFontMono3x5-Regular.svg?v=transparent-v2" alt="my 3x5 tiny mono pixel font Regular preview" width="720">

#### CommitMono 275 Italic

<img src="assets/previews/commit-mono/CommitMono-275-Italic.svg?v=transparent-v2" alt="CommitMono 275 Italic preview" width="720">

#### CommitMono 275 Regular

<img src="assets/previews/commit-mono/CommitMono-275-Regular.svg?v=transparent-v2" alt="CommitMono 275 Regular preview" width="720">

#### Cozette Vector Px Regular

<img src="assets/previews/cozette/CozetteVectorPx-Regular.svg?v=transparent-v2" alt="Cozette Vector Px Regular preview" width="720">

#### Departure Mono Regular

<img src="assets/previews/departure-mono/DepartureMono-Regular.svg?v=transparent-v2" alt="Departure Mono Regular preview" width="720">

#### Departure Mono Condensed Regular

<img src="assets/previews/departure-mono/DepartureMonoCondensed-Regular.svg?v=transparent-v2" alt="Departure Mono Condensed Regular preview" width="720">

#### Departure Mono Semi Condensed

<img src="assets/previews/departure-mono/DepartureMonoSemiCondensed-Regular.svg?v=transparent-v2" alt="Departure Mono Semi Condensed preview" width="720">

#### Departure Mono Ultra Condensed Compact

<img src="assets/previews/departure-mono/DepartureMonoUltraCondensedCompact-Regular.svg?v=transparent-v2" alt="Departure Mono Ultra Condensed Compact preview" width="720">

#### Envy Code B 10pt

<img src="assets/previews/envy-code-b/EnvyCodeB10pt-Regular.svg?v=transparent-v2" alt="Envy Code B 10pt preview" width="720">

#### Envy Code B 10pt Condensed

<img src="assets/previews/envy-code-b/EnvyCodeB10ptCondensed-Regular.svg?v=transparent-v2" alt="Envy Code B 10pt Condensed preview" width="720">

#### Envy Code B 10pt Semi Condensed

<img src="assets/previews/envy-code-b/EnvyCodeB10ptSemiCondensed-Regular.svg?v=transparent-v2" alt="Envy Code B 10pt Semi Condensed preview" width="720">

#### Iosevka Pixel Slab Regular

<img src="assets/previews/iosevka-pixel-slab/IosevkaPixelSlab-Regular.svg?v=transparent-v2" alt="Iosevka Pixel Slab Regular preview" width="720">

#### Iosevka Pixel Slab Compact Regular

<img src="assets/previews/iosevka-pixel-slab/IosevkaPixelSlabCompact-Regular.svg?v=transparent-v2" alt="Iosevka Pixel Slab Compact Regular preview" width="720">

#### Iosevka Pixel Slab Condensed Compact Regular

<img src="assets/previews/iosevka-pixel-slab/IosevkaPixelSlabCondensedCompact-Regular.svg?v=transparent-v2" alt="Iosevka Pixel Slab Condensed Compact Regular preview" width="720">

#### Iosevka Pixel Slab Squat Regular

<img src="assets/previews/iosevka-pixel-slab/IosevkaPixelSlabSquat-Regular.svg?v=transparent-v2" alt="Iosevka Pixel Slab Squat Regular preview" width="720">

#### Iosevka Term Slab Condensed Bold

<img src="assets/previews/iosevka-term-slab/IosevkaTermSlabCondensed-Bold.svg?v=transparent-v2" alt="Iosevka Term Slab Condensed Bold preview" width="720">

#### Iosevka Term Slab Condensed Bold Italic

<img src="assets/previews/iosevka-term-slab/IosevkaTermSlabCondensed-BoldItalic.svg?v=transparent-v2" alt="Iosevka Term Slab Condensed Bold Italic preview" width="720">

#### Iosevka Term Slab Condensed Italic

<img src="assets/previews/iosevka-term-slab/IosevkaTermSlabCondensed-Italic.svg?v=transparent-v2" alt="Iosevka Term Slab Condensed Italic preview" width="720">

#### Iosevka Term Slab Condensed Light

<img src="assets/previews/iosevka-term-slab/IosevkaTermSlabCondensed-Light.svg?v=transparent-v2" alt="Iosevka Term Slab Condensed Light preview" width="720">

#### Iosevka Term Slab Condensed Light Italic

<img src="assets/previews/iosevka-term-slab/IosevkaTermSlabCondensed-LightItalic.svg?v=transparent-v2" alt="Iosevka Term Slab Condensed Light Italic preview" width="720">

#### Iosevka Term Slab Condensed

<img src="assets/previews/iosevka-term-slab/IosevkaTermSlabCondensed-Regular.svg?v=transparent-v2" alt="Iosevka Term Slab Condensed preview" width="720">

#### m3x6 Mono Regular

<img src="assets/previews/m3x6-mono/m3x6Mono-Regular.svg?v=transparent-v2" alt="m3x6 Mono Regular preview" width="720">

#### m5x7 Mono Regular

<img src="assets/previews/m5x7-mono/m5x7Mono-Regular.svg?v=transparent-v2" alt="m5x7 Mono Regular preview" width="720">

#### m5x7 Mono Condensed Regular

<img src="assets/previews/m5x7-mono/m5x7MonoCondensed-Regular.svg?v=transparent-v2" alt="m5x7 Mono Condensed Regular preview" width="720">

#### Monocraft Black Italic

<img src="assets/previews/monocraft/Monocraft-Black-Italic.svg?v=transparent-v2" alt="Monocraft Black Italic preview" width="720">

#### Monocraft Black

<img src="assets/previews/monocraft/Monocraft-Black.svg?v=transparent-v2" alt="Monocraft Black preview" width="720">

#### Monocraft Bold Italic

<img src="assets/previews/monocraft/Monocraft-Bold-Italic.svg?v=transparent-v2" alt="Monocraft Bold Italic preview" width="720">

#### Monocraft Bold

<img src="assets/previews/monocraft/Monocraft-Bold.svg?v=transparent-v2" alt="Monocraft Bold preview" width="720">

#### Monocraft ExtraLight Italic

<img src="assets/previews/monocraft/Monocraft-ExtraLight-Italic.svg?v=transparent-v2" alt="Monocraft ExtraLight Italic preview" width="720">

#### Monocraft ExtraLight

<img src="assets/previews/monocraft/Monocraft-ExtraLight.svg?v=transparent-v2" alt="Monocraft ExtraLight preview" width="720">

#### Monocraft Italic

<img src="assets/previews/monocraft/Monocraft-Italic.svg?v=transparent-v2" alt="Monocraft Italic preview" width="720">

#### Monocraft Light Italic

<img src="assets/previews/monocraft/Monocraft-Light-Italic.svg?v=transparent-v2" alt="Monocraft Light Italic preview" width="720">

#### Monocraft Light

<img src="assets/previews/monocraft/Monocraft-Light.svg?v=transparent-v2" alt="Monocraft Light preview" width="720">

#### Monocraft SemiBold Italic

<img src="assets/previews/monocraft/Monocraft-SemiBold-Italic.svg?v=transparent-v2" alt="Monocraft SemiBold Italic preview" width="720">

#### Monocraft SemiBold

<img src="assets/previews/monocraft/Monocraft-SemiBold.svg?v=transparent-v2" alt="Monocraft SemiBold preview" width="720">

#### Monocraft

<img src="assets/previews/monocraft/Monocraft.svg?v=transparent-v2" alt="Monocraft preview" width="720">

#### Moono Regular

<img src="assets/previews/moono/Moono-Regular.svg?v=transparent-v2" alt="Moono Regular preview" width="720">

#### Nib Regular

<img src="assets/previews/nib/Nib-Regular.svg?v=transparent-v2" alt="Nib Regular preview" width="720">

#### Quaver Mono Regular

<img src="assets/previews/quaver-mono/QuaverMono-Regular.svg?v=transparent-v2" alt="Quaver Mono Regular preview" width="720">

#### Quaver Mono Condensed Regular

<img src="assets/previews/quaver-mono/QuaverMonoCondensed-Regular.svg?v=transparent-v2" alt="Quaver Mono Condensed Regular preview" width="720">

#### RuneScape

<img src="assets/previews/runescape/RuneScape.svg?v=transparent-v2" alt="RuneScape preview" width="720">

#### RuneScape Small

<img src="assets/previews/runescape/runescape_small.svg?v=transparent-v2" alt="RuneScape Small preview" width="720">

#### RuneScape Small Mono

<img src="assets/previews/runescape/runescape_small_mono.svg?v=transparent-v2" alt="RuneScape Small Mono preview" width="720">

Preview phrase: “Sphinx of black quartz, judge my vow.”

Regenerate the SVGs and this README section with Nix:

```bash
nix develop -c ./scripts/generate_previews.py
```

Or without Nix:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install fonttools uharfbuzz
./scripts/generate_previews.py
```
<!-- previews:end -->

## Credits

- **Nib**: original, 5 × 7 glyphs in a 6 × 11 cell, built from shared stroke rules.
- **m5x7 Mono** (6 × 9) and **m5x7 Mono Condensed** (5 × 9): remixes of [m5x7](https://managore.itch.io/m5x7) by Daniel Linssen, CC0.
- **m3x6 Mono** (4 × 8): remix of [m3x6](https://managore.itch.io/m3x6) by Daniel Linssen, CC0.
- **Quaver Mono** (6 × 8) and **Quaver Mono Condensed** (5 × 8): remixes of [Quaver](https://caffinate.itch.io/quaver) by Nathan Scott, CC0.
- **Another Tiny Pixel Font Mono 3x5** by [alasseearfalas](https://alasseearfalas.itch.io/another-tiny-pixel-font-mono-3x5), CC0, unchanged.

The remixes keep the original bitmaps and only narrow glyphs that don't fit the cell. Each family folder's `LICENSE` carries its credit.

## License

AGPL-3.0-or-later; see [`LICENSE`](LICENSE). Bundled fonts keep their upstream licenses.
