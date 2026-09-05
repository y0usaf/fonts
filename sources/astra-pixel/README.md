# Astra Pixel

Original, editable pixel letterforms. The released font is **Astra Pixel**, at **10ppem with a 5 × 10px cell**. It preserves compact Departure's
8px capital height and 6px lowercase height while fitting three additional
rows in a 640 × 330px viewport. Its main compromise is one-row descenders.
Released as version 1.0.0. The capacity measurements do not claim improved
human reading speed.

Open [the standalone comparison](../../assets/previews/astra-pixel/comparison.html)
in a browser. Fonts are embedded; no server or network connection is needed.
The [pair proof](../../assets/previews/astra-pixel/pairs.png) shows the actual
browser canvases at 2× nearest-neighbor enlargement.

## Measured comparison

The reference is the repository's actual
`DepartureMonoUltraCondensedCompact-Regular.ttf`, not regular Departure or a
reconstruction. FreeType measures a fixed 5px ASCII advance and 11px line height
at 11ppem. `hhea` ascent/descent are 450/-100 with UPM 550, so the line is
exactly 11px. It has no ASCII cell escapes or pixel collisions.

All capacities below use **640 × 330 physical pixels**, complete cells only.
Cap and lowercase heights are raster ink bounds of H and x respectively.

| Design | Native ppem | Advance | Line | Cap / x | Columns | Rows | Characters |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Compact Departure | 11 | 5px | 11px | 8 / 6px | 128 | 30 | 3,840 |
| Pixel Mono Tight | 11 | 6px | 11px | 8 / 6px | 106 | 30 | 3,180 |
| Pixel Mono Balanced | 11 | 6px | 12px | 8 / 6px | 106 | 27 | 2,862 |
| Pixel Mono Open | 11 | 7px | 12px | 8 / 6px | 91 | 27 | 2,457 |
| **Astra Pixel** | **10** | **5px** | **10px** | **8 / 6px** | **128** | **33** | **4,224** |
| Astra Pixel Facet | 10 | 5px | 10px | 7 / 5px | 128 | 33 | 4,224 |
| Astra Pixel Loom | 10 | 5px | 10px | 7 / 5px | 128 | 33 | 4,224 |
| Astra Pixel Reed | 10 | 4px | 10px | 7 / 5px | 160 | 33 | 5,280 |

Text gains **10% capacity through rows**, without losing columns or reducing
cap/x heights. Facet and Loom have smaller letter bodies, so their identical
capacity is not an equivalent readability result. Reed's 37.5% capacity gain
also comes with smaller, narrower letters and visibly compromised M/N/m.
Retain Reed as an experiment; do not use its capacity number as evidence of
better usable text density.

Pixel Mono's untracked files disappeared externally between the first two
repository inspections. Its original file-writing commands were subsequently
recovered from this task's local session record. The generator, build plans,
design notes and checks were restored, including the recorded OS/2 version-4
fix. The editable masks were recreated using the original extraction recipe:
the unchanged `DepartureMono-Regular.ttf` through FreeType at 11ppem, centered
in five columns, with the original explicit `#`, `%` and `&` drawings. Its
three TTFs and specimen were rebuilt, and its original tests pass. They are
now included as required references. This restores the existing design, not
a newly invented substitute; no direct checksum comparison to the deleted
binaries is possible. The upstream OFL notice was restored from the same
[Departure license source](https://raw.githubusercontent.com/rektdeckard/departure-mono/main/public/assets/LICENSE)
used by the original command and is embedded in the offline comparison.

## Design exploration and refinement

1. **Facet:** hand-drawn 4-column ink, 7px caps, 5px lowercase, chamfered bowls,
   asymmetric terminals and a clear right-hand blank column. The first compact
   sketch is pleasingly open, but measured against the real baseline its body
   is smaller. It is retained honestly as a smaller-grid alternative.
2. **Reed:** separately drawn 3-column alphabet. Narrow counters create a wiry
   texture and more columns, but m/M/N become too dark and too similar. This is
   the weakest general-purpose coding face despite its highest capacity.
3. **Loom:** square counters, interrupted diagonal joins and a single-storey a.
   Its more mechanical texture is distinct from Facet; at native scale the
   square bowls and m/W are darker. It is useful as a stylistic alternative.
4. **Text (released as Astra Pixel):** a full-height redraw after measurement exposed the first sketches'
   smaller bodies. Its 8px caps and 6px lowercase match Departure. The 4-column
   bowls, flagged 1, hooked l, barred I and marked 0 keep a coherent identity.
   The g/y bowls rise before short tails, while p/q/j use one-row descenders.
   No drawn pixels are clipped to achieve the 10px line. This is the strongest
   balance in the current code and difficult-pair proofs.

The shared identity is upright stems, chamfered counters, compact crossbars
and small outward terminal kicks. Wide letters necessarily remain a weak
point on four columns. Perceptually distinct glyphs need more than a pixel
inequality check, so the proofs emphasize `0O 1lI rn m cl d MW MN`, punctuation,
and repeated descender/capital lines. Text's one-row descenders remain the
main item for the user's visual review.

No upstream outlines or raster letterforms are imported into Astra Pixel. The
existing `pixelize.py` contributes only the pixel-union/TrueType contour
machinery. Simply retuning Departure would have been less code, but would
not meet the requirement for original letterforms. Data files carry design
decisions; one generator serves every candidate. This is an apply-and-exit
tool, without an extension API, daemon or persistent viewer-owned state.

## Editable sources and controls

`families.json` declares grids, advances, cap heights, ascents, descents and
source overlays. Each text file uses a Unicode codepoint plus slash-separated
rows: `#` is ink and `.` is empty. Rows descend from cap top. Short drawings
have implicit blank lower rows. Facet and Reed are complete ASCII drawings;
Loom and Text overlay Facet through the same mechanism available for custom
character variants.

Every shipped font contains printable ASCII (95 characters), a visible
`.notdef`, and **15 light box-drawing characters**:
`─ │ ┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼ ╴ ╵ ╶ ╷`.
Heavy, double, dashed, diagonal and rounded boxes, block elements, accents,
and other Unicode characters are not currently covered. The preview reports
unsupported input instead of silently using another font.

Rebuild all fonts and the measured offline page:

```sh
nix develop -c python scripts/build_astra_pixel.py
nix develop -c python scripts/check_astra_pixel.py > assets/previews/astra-pixel/metrics.json
nix develop -c python scripts/preview_astra_pixel.py
```

Build a distinct custom family with one additional spacing pixel, one extra
line pixel, a dotted zero, and a serif ell:

```sh
nix develop -c python scripts/build_astra_pixel.py --family Text \
  --tracking 1 --leading 1 --alternate dotted-zero --alternate serif-ell \
  --out /tmp/astra-custom
```

Tracking and leading are nonnegative whole design pixels. Box arms extend
to the new cell edges. Custom spacing and alternate selections are included
in the internal family name so they can coexist with defaults. `--config`
accepts another family configuration; source paths resolve relative to this
source directory. Negative spacing and invalid drawings fail loudly.

Fonts are installable outline TTFs, using 64 font units per design pixel.
Use 10px native size and 10px line height for Text, or integer multiples.
Noninteger scaling can blur this outline pixel design. Some terminals impose
their own extra leading; the claimed row gain requires the measured 10px line.
No fonts were installed into the user's system as part of building them.

## Verification and limits

`check_astra_pixel.py` fails on missing ASCII, duplicate ASCII rasters, variable
advances, cell escapes, absent separator pixels, wrong cmap entries, grayscale
edge pixels, and raster/source differences. It checks every supported glyph
in FreeType monochrome and grayscale at 1×/2×/3×. Full blank separator columns
and rows prove that any adjacent ASCII pair has no overlap or edge contact.
Box glyphs intentionally connect at cell edges; their raster equals the
generated arm geometry and the horizontal/vertical extents span full cells.
HarfBuzz shaping checks every supported character for fixed, non-offset
advances and nonmissing glyph IDs.

The Nix check compares both Astra Pixel and restored Pixel Mono binaries byte-for-byte with a fresh rebuild,
checks generated measurements, rebuilds the embedded preview, and exercises
custom spacing/alternatives. Fixed font timestamps make builds reproducible.

```sh
nix flake check path:"$PWD"
nix build path:"$PWD"#astra-pixel --no-link
```

The `path:` form includes these new files before they are tracked in Git.
Once tracked, ordinary `nix flake check` and `nix build .#astra-pixel` work.
The package installs four TTFs under `share/fonts/truetype`.

For browser verification, start a dedicated Chromium instance and run:

```sh
chromium --headless --no-sandbox --disable-gpu \
  --user-data-dir=/tmp/astra-proof-browser --remote-debugging-port=9369 about:blank
# In another shell (Node and Chromium must be available):
nix develop -c node scripts/check_astra_preview.mjs
```

The browser check measures all ASCII advances, checks 1,140 Astra Pixel ASCII
rasters across 1×/2×/3× for binary pixels and separator bounds, exercises
five presets, editing, missing-character reporting and both themes, and
verifies physical canvas sizes at DPR 1/2 and zoom 1/2/3/4. It also verifies
zero HTTP requests. The page uses a fixed native backing canvas, with CSS
dimensions divided by devicePixelRatio, so a design pixel really is a physical
pixel at 1×. Browser zoom/OS compositor behavior outside those tested settings
is not a tested invariant.

The compact Departure binary has fractional horizontal outline positions
from its condensation; browsers may antialias it at native scale. The page
preserves that actual rendering. Astra Pixel uses integer square pixels. No CSS
font smoothing tricks or scaling of Departure are used to favor Astra Pixel.

GNU AGPL v3 or later, matching the repository. Original drawings and generated
font name tables carry no borrowed upstream letterform copyright claims.
