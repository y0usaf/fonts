<h1 align="center">fonts</h1>

<p align="center">Fonts I use</p>

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

#### Iosevka Term Slab Compact Italic Sonic

<img src="assets/previews/iosevka-term-slab/IosevkaTermSlabCompact-Italic-Sonic.svg?v=transparent-v2" alt="Iosevka Term Slab Compact Italic Sonic preview" width="720">

#### Iosevka Term Slab Compact Regular Sonic

<img src="assets/previews/iosevka-term-slab/IosevkaTermSlabCompact-Regular-Sonic.svg?v=transparent-v2" alt="Iosevka Term Slab Compact Regular Sonic preview" width="720">

#### RuneScape Regular Sonic

<img src="assets/previews/runescape/RuneScape-Regular-Sonic.svg?v=transparent-v2" alt="RuneScape Regular Sonic preview" width="720">

#### Terminus Regular Sonic

<img src="assets/previews/terminus/Terminus-Regular-Sonic.svg?v=transparent-v2" alt="Terminus Regular Sonic preview" width="720">

<h2 align="center">🍉 Regular Fonts 🍉</h2>

#### CommitMono 275 Italic

<img src="assets/previews/commit-mono/CommitMono-275-Italic.svg?v=transparent-v2" alt="CommitMono 275 Italic preview" width="720">

#### CommitMono 275 Regular

<img src="assets/previews/commit-mono/CommitMono-275-Regular.svg?v=transparent-v2" alt="CommitMono 275 Regular preview" width="720">

#### Departure Mono Regular

<img src="assets/previews/departure-mono/DepartureMono-Regular.svg?v=transparent-v2" alt="Departure Mono Regular preview" width="720">

#### Departure Mono Compact Regular

<img src="assets/previews/departure-mono/DepartureMonoCompact-Regular.svg?v=transparent-v2" alt="Departure Mono Compact Regular preview" width="720">

#### Departure Mono Condensed Regular

<img src="assets/previews/departure-mono/DepartureMonoCondensed-Regular.svg?v=transparent-v2" alt="Departure Mono Condensed Regular preview" width="720">

#### Departure Mono Condensed Compact Regular

<img src="assets/previews/departure-mono/DepartureMonoCondensedCompact-Regular.svg?v=transparent-v2" alt="Departure Mono Condensed Compact Regular preview" width="720">

#### Envy Code B 10pt

<img src="assets/previews/envy-code-b/EnvyCodeB10pt-Regular.svg?v=transparent-v2" alt="Envy Code B 10pt preview" width="720">

#### Envy Code B 10pt Compact Regular

<img src="assets/previews/envy-code-b/EnvyCodeB10ptCompact-Regular.svg?v=transparent-v2" alt="Envy Code B 10pt Compact Regular preview" width="720">

#### Iosevka Term Slab Compact Bold

<img src="assets/previews/iosevka-term-slab/IosevkaTermSlabCompact-Bold.svg?v=transparent-v2" alt="Iosevka Term Slab Compact Bold preview" width="720">

#### Iosevka Term Slab Compact Bold Italic

<img src="assets/previews/iosevka-term-slab/IosevkaTermSlabCompact-BoldItalic.svg?v=transparent-v2" alt="Iosevka Term Slab Compact Bold Italic preview" width="720">

#### Iosevka Term Slab Compact Italic

<img src="assets/previews/iosevka-term-slab/IosevkaTermSlabCompact-Italic.svg?v=transparent-v2" alt="Iosevka Term Slab Compact Italic preview" width="720">

#### Iosevka Term Slab Compact Light

<img src="assets/previews/iosevka-term-slab/IosevkaTermSlabCompact-Light.svg?v=transparent-v2" alt="Iosevka Term Slab Compact Light preview" width="720">

#### Iosevka Term Slab Compact Light Italic

<img src="assets/previews/iosevka-term-slab/IosevkaTermSlabCompact-LightItalic.svg?v=transparent-v2" alt="Iosevka Term Slab Compact Light Italic preview" width="720">

#### Iosevka Term Slab Compact

<img src="assets/previews/iosevka-term-slab/IosevkaTermSlabCompact-Regular.svg?v=transparent-v2" alt="Iosevka Term Slab Compact preview" width="720">

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

## Nix

Install everything:

```bash
nix profile install github:y0usaf/fonts
```

Or a single family — each subfolder of `fonts/` is its own package:

```bash
nix profile install github:y0usaf/fonts#commit-mono
nix flake show github:y0usaf/fonts   # list all families
```

Or from a local checkout:

```bash
nix profile install .
```

## License

This repository is licensed under the GNU Affero General Public License v3.0 or later. See [`LICENSE`](LICENSE).

Bundled/generated font binaries may retain license requirements from their upstream source families. Keep upstream copyright and license notices where required.
