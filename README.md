<h1 align="center">fonts</h1>

<p align="center">Fonts I use</p>

<!-- previews:start -->
<h2 align="center">⚡ Sonic Fonts ⚡</h2>

#### Atkinson Hyperlegible Mono Regular Sonic

<img src="assets/previews/AtkinsonHyperlegibleMono-Regular-Sonic.svg?v=transparent-v2" alt="Atkinson Hyperlegible Mono Regular Sonic preview" width="720">

#### CommitMono 200 Italic Sonic

<img src="assets/previews/CommitMono-200-Italic-Sonic.svg?v=transparent-v2" alt="CommitMono 200 Italic Sonic preview" width="720">

#### CommitMono 200 Regular Sonic

<img src="assets/previews/CommitMono-200-Regular-Sonic.svg?v=transparent-v2" alt="CommitMono 200 Regular Sonic preview" width="720">

#### Go Mono Regular Sonic

<img src="assets/previews/GoMono-Regular-Sonic.svg?v=transparent-v2" alt="Go Mono Regular Sonic preview" width="720">

#### Iosevka Term Slab Regular Sonic

<img src="assets/previews/IosevkaTermSlab-Regular-Sonic.svg?v=transparent-v2" alt="Iosevka Term Slab Regular Sonic preview" width="720">

#### Iosevka Term Slab Compact Italic Sonic

<img src="assets/previews/IosevkaTermSlabCompact-Italic-Sonic.svg?v=transparent-v2" alt="Iosevka Term Slab Compact Italic Sonic preview" width="720">

#### Iosevka Term Slab Compact Regular Sonic

<img src="assets/previews/IosevkaTermSlabCompact-Regular-Sonic.svg?v=transparent-v2" alt="Iosevka Term Slab Compact Regular Sonic preview" width="720">

#### RuneScape Regular Sonic

<img src="assets/previews/RuneScape-Regular-Sonic.svg?v=transparent-v2" alt="RuneScape Regular Sonic preview" width="720">

#### Terminus Regular Sonic

<img src="assets/previews/Terminus-Regular-Sonic.svg?v=transparent-v2" alt="Terminus Regular Sonic preview" width="720">

<h2 align="center">🍉 Regular Fonts 🍉</h2>

#### CommitMono 275 Italic

<img src="assets/previews/CommitMono-275-Italic.svg?v=transparent-v2" alt="CommitMono 275 Italic preview" width="720">

#### CommitMono 275 Regular

<img src="assets/previews/CommitMono-275-Regular.svg?v=transparent-v2" alt="CommitMono 275 Regular preview" width="720">

#### Departure Mono Regular

<img src="assets/previews/DepartureMono-Regular.svg?v=transparent-v2" alt="Departure Mono Regular preview" width="720">

#### Departure Mono Condensed Regular

<img src="assets/previews/DepartureMonoCondensed-Regular.svg?v=transparent-v2" alt="Departure Mono Condensed Regular preview" width="720">

#### Departure Mono Condensed Compact Regular

<img src="assets/previews/DepartureMonoCondensedCompact-Regular.svg?v=transparent-v2" alt="Departure Mono Condensed Compact Regular preview" width="720">

#### Envy Code B 10pt

<img src="assets/previews/EnvyCodeB10pt-Regular.svg?v=transparent-v2" alt="Envy Code B 10pt preview" width="720">

#### Envy Code B 10pt Compact Regular

<img src="assets/previews/EnvyCodeB10ptCompact-Regular.svg?v=transparent-v2" alt="Envy Code B 10pt Compact Regular preview" width="720">

#### Iosevka Term Slab Compact Bold

<img src="assets/previews/IosevkaTermSlabCompact-Bold.svg?v=transparent-v2" alt="Iosevka Term Slab Compact Bold preview" width="720">

#### Iosevka Term Slab Compact Bold Italic

<img src="assets/previews/IosevkaTermSlabCompact-BoldItalic.svg?v=transparent-v2" alt="Iosevka Term Slab Compact Bold Italic preview" width="720">

#### Iosevka Term Slab Compact Italic

<img src="assets/previews/IosevkaTermSlabCompact-Italic.svg?v=transparent-v2" alt="Iosevka Term Slab Compact Italic preview" width="720">

#### Iosevka Term Slab Compact Light

<img src="assets/previews/IosevkaTermSlabCompact-Light.svg?v=transparent-v2" alt="Iosevka Term Slab Compact Light preview" width="720">

#### Iosevka Term Slab Compact Light Italic

<img src="assets/previews/IosevkaTermSlabCompact-LightItalic.svg?v=transparent-v2" alt="Iosevka Term Slab Compact Light Italic preview" width="720">

#### Iosevka Term Slab Compact

<img src="assets/previews/IosevkaTermSlabCompact-Regular.svg?v=transparent-v2" alt="Iosevka Term Slab Compact preview" width="720">

#### RuneScape

<img src="assets/previews/RuneScape.svg?v=transparent-v2" alt="RuneScape preview" width="720">

#### RuneScape Small

<img src="assets/previews/runescape_small.svg?v=transparent-v2" alt="RuneScape Small preview" width="720">

#### RuneScape Small Mono

<img src="assets/previews/runescape_small_mono.svg?v=transparent-v2" alt="RuneScape Small Mono preview" width="720">

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

## Nix

```bash
nix profile install github:y0usaf/fonts
```

Or from a local checkout:

```bash
nix profile install .
```

## License

This repository is licensed under the GNU Affero General Public License v3.0 or later. See [`LICENSE`](LICENSE).

Bundled/generated font binaries may retain license requirements from their upstream source families. Keep upstream copyright and license notices where required.
