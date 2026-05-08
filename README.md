<h1 align="center">fonts</h1>

<p align="center">Fonts I use</p>

## Previews

GitHub README Markdown cannot load arbitrary local fonts for live text, so these previews are generated as standalone SVGs with HarfBuzz-shaped glyph outlines. That applies OpenType features such as the Sonic `calt` substitutions. The SVG backgrounds are transparent and the preview text adapts for light/dark themes.

Preview phrase: “Sphinx of black quartz, judge my vow.”

Regenerate the SVGs and this README section with:

```bash
nix develop -c ./scripts/generate_previews.py
```

<table>
  <tr>
    <td align="center">
      <h2>⚡ Sonic Fonts</h2>
      <p><em>Fast-reading variants with Sonic OpenType substitutions.</em></p>
    </td>
  </tr>
</table>

#### AtkinsonHyperlegibleMono-Regular-Sonic.ttf

<img src="assets/previews/AtkinsonHyperlegibleMono-Regular-Sonic.svg?v=transparent-v2" alt="Atkinson Hyperlegible Mono Regular Sonic preview" width="720">

#### CommitMono-200-Italic-Sonic.otf

<img src="assets/previews/CommitMono-200-Italic-Sonic.svg?v=transparent-v2" alt="CommitMono 200 Sonic Italic preview" width="720">

#### CommitMono-200-Regular-Sonic.otf

<img src="assets/previews/CommitMono-200-Regular-Sonic.svg?v=transparent-v2" alt="CommitMono 200 Regular Sonic preview" width="720">

#### GoMono-Regular-Sonic.ttf

<img src="assets/previews/GoMono-Regular-Sonic.svg?v=transparent-v2" alt="Go Mono Regular Sonic preview" width="720">

#### IosevkaTermSlab-Regular-Sonic.ttf

<img src="assets/previews/IosevkaTermSlab-Regular-Sonic.svg?v=transparent-v2" alt="Iosevka Term Slab Regular Sonic preview" width="720">

#### IosevkaTermSlabCompact-Italic-Sonic.ttf

<img src="assets/previews/IosevkaTermSlabCompact-Italic-Sonic.svg?v=transparent-v2" alt="Iosevka Term Slab Compact Sonic Italic preview" width="720">

#### IosevkaTermSlabCompact-Regular-Sonic.ttf

<img src="assets/previews/IosevkaTermSlabCompact-Regular-Sonic.svg?v=transparent-v2" alt="Iosevka Term Slab Compact Regular Sonic preview" width="720">

#### RuneScape-Regular-Sonic.ttf

<img src="assets/previews/RuneScape-Regular-Sonic.svg?v=transparent-v2" alt="RuneScape Regular Sonic preview" width="720">

#### Terminus-Regular-Sonic.ttf

<img src="assets/previews/Terminus-Regular-Sonic.svg?v=transparent-v2" alt="Terminus Regular Sonic preview" width="720">

<table>
  <tr>
    <td align="center">
      <h2>Regular Fonts</h2>
      <p><em>Regular font files without Sonic substitutions.</em></p>
    </td>
  </tr>
</table>

#### CommitMono-275-Italic.otf

<img src="assets/previews/CommitMono-275-Italic.svg?v=transparent-v2" alt="CommitMono 275 Italic preview" width="720">

#### CommitMono-275-Regular.otf

<img src="assets/previews/CommitMono-275-Regular.svg?v=transparent-v2" alt="CommitMono 275 Regular preview" width="720">

#### DepartureMono-Regular.otf

<img src="assets/previews/DepartureMono-Regular.svg?v=transparent-v2" alt="Departure Mono Regular preview" width="720">

#### IosevkaTermSlabCompact-Bold.ttf

<img src="assets/previews/IosevkaTermSlabCompact-Bold.svg?v=transparent-v2" alt="Iosevka Term Slab Compact Bold preview" width="720">

#### IosevkaTermSlabCompact-BoldItalic.ttf

<img src="assets/previews/IosevkaTermSlabCompact-BoldItalic.svg?v=transparent-v2" alt="Iosevka Term Slab Compact Bold Italic preview" width="720">

#### IosevkaTermSlabCompact-Italic.ttf

<img src="assets/previews/IosevkaTermSlabCompact-Italic.svg?v=transparent-v2" alt="Iosevka Term Slab Compact Italic preview" width="720">

#### IosevkaTermSlabCompact-Light.ttf

<img src="assets/previews/IosevkaTermSlabCompact-Light.svg?v=transparent-v2" alt="Iosevka Term Slab Compact Light preview" width="720">

#### IosevkaTermSlabCompact-LightItalic.ttf

<img src="assets/previews/IosevkaTermSlabCompact-LightItalic.svg?v=transparent-v2" alt="Iosevka Term Slab Compact Light Italic preview" width="720">

#### IosevkaTermSlabCompact-Regular.ttf

<img src="assets/previews/IosevkaTermSlabCompact-Regular.svg?v=transparent-v2" alt="Iosevka Term Slab Compact preview" width="720">

#### Pixel_IosevkaSlab_24.ttf

<img src="assets/previews/Pixel_IosevkaSlab_24.svg?v=transparent-v2" alt="Pixel Iosevka Slab 24 preview" width="720">

#### RuneScape.ttf

<img src="assets/previews/RuneScape.svg?v=transparent-v2" alt="RuneScape preview" width="720">

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
