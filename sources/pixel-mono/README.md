# Pixel Mono

A configurable, strictly monospaced pixel-font prototype derived from Departure
Mono. The initial design keeps Departure's five-column letters and eight-pixel
capitals. It explores shared spacing and explicit glyph alternatives before
attempting smaller letterforms. This is an ASCII prototype, not a full Unicode
replacement or an arbitrary-size font generator.

Open [the standalone specimen](../../assets/previews/pixel-mono/specimen.html)
in a browser. It embeds the fonts, works offline, accepts your own text, and
compares original Departure, the existing Ultra Condensed Compact, and all three
new presets. Scale and light/dark controls support visual comparison.

| Preset | Advance at 11px | Line height at 11px | Zero | Lowercase l |
| --- | --- | --- | --- | --- |
| Balanced | 6px | 12px | Slashed | Serifed |
| Tight | 6px | 11px | Slashed | Serifed |
| Open | 7px | 12px | Dotted | Tailed |

Original Departure's local binary has a 7px advance and 14px hhea line height at
11px. Balanced uses about 27% less nominal cell area; Tight uses about 33% less.
These are geometry comparisons, not evidence of improved reading speed. The
existing Ultra Condensed Compact remains narrower at 5px; it is included as a
reference, not superseded on density. Tight adds no blank row above the tallest
ASCII marks, so assess multiline text carefully.

## Build and configure

From the repository root:

```sh
nix develop -c python scripts/build_pixel_mono.py
nix flake check path:.
```

`path:.` includes new files before they are added to Git. Once tracked, ordinary
`nix flake check` works too. Build outputs go to `fonts/pixel-mono/` and
`assets/previews/pixel-mono/specimen.html`. The existing family packaging also
exposes `pixel-mono`. Building does not install or select the fonts.

Edit `build-plans.toml` to add named builds. All distances are whole pixels:

- `family`: unique ASCII font family name.
- `letter_gap`: 1–3 blank columns after the five-column design area. Every glyph,
  including space and `.notdef`, receives the same advance.
- `line_gap`: 0–4 extra rows above the eleven-row ink envelope; encoded in ascent
  so applications using hhea or OS/2 metrics see matching line heights.
- `zero`: `slashed`, `dotted`, or `plain`.
- `ell`: `serifed` or `tailed`.

Unknown options and unsupported values fail before font output. Give each new
plan a distinct family. The builder does not delete older output files when a
plan is removed. Supported overrides: `--plans`, `--glyphs`, `--out`, and
`--specimen`; see `--help`.

## Design source

`glyphs.json` is editable source: each character has eleven rows of five pixels;
`#` is ink, `.` is empty. Rows run from y=8 down to y=-2, with y=0 the row directly
above the baseline. Printable ASCII is required. This fixed envelope intentionally
protects the current proportions; width and height are not scaling controls.

The initial masks were extracted with FreeType at 11ppem from the repository's
`DepartureMono-Regular.ttf`, then placed within five columns. `#`, `%`, and `&`
were explicitly redrawn to fit. Narrow glyphs were centered within the design
area. The zero recipe preserves its bowl while replacing the interior; the
alternate l uses a shared vertical stem and a tail. Future size presets should
supply deliberately drawn masks/recipes rather than resampling these pixels.

The builder reuses `scripts/pixelize.py` for merged square-pixel contours, then
writes TTF tables with fontTools. No kerning, substitutions, or positioning tables
are emitted. Output timestamps are fixed for reproducibility. Rasterization is
intended for 11px and integer multiples; display scaling and placement still
matter. Build-time configuration produces ordinary static TTFs.

Checks cover every ASCII glyph through FreeType at 11px and 22px, cell bounds,
HarfBuzz spacing, source validation, configuration rejection, distinguishing
characters, and reproducible output. These checks establish rendering and spacing
properties; the visual design still needs human review.

## License and attribution

Departure Mono: Copyright 2022–2024 Helena Zhang (helenazhang.com).
The derivative font and its editable glyph source use the
[SIL Open Font License 1.1](../../fonts/pixel-mono/LICENSE). The new family name is
Pixel Mono. Repository code retains the repository's AGPL-3.0-or-later license.

Upstream: https://github.com/rektdeckard/departure-mono
