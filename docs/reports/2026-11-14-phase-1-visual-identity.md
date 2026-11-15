# Phase 1 — Visual Identity

## Scope

This phase consolidates the Paper Collage Archive's visual language only. The C → B → A artwork geometry, timing, navigation, project/diary content, page structure, and responsive layout were not redesigned.

## Changes

### Semantic palette

Replaced scattered one-off values in the active archive art-direction layer with one semantic token source in `:root`:

- Paper surfaces: paper, white paper, sand, cool lavender, lavender, tape, gold.
- Typography: ink, deep ink, soft ink, muted text.
- Editorial accents: line, strong line, red accent, deep red, plum, gold.
- Depth and texture: soft/medium/strong shadows, paper grain dots, ruled texture, translucent tape and ink overlays.
- Typography roles: serif for reading, sans-serif for display/interface, monospace for specimen labels and metadata.

The active `archive-art-direction` consumer rules contain no raw hex colors outside the token declaration. The SVG uses literal presentation colors because the available static renderer does not resolve CSS custom properties in SVG presentation attributes; those literal values were normalized to exact matches of the global palette.

### Typography and recurring graphic language

- Kept the three established roles: serif reading surfaces, sans-serif display/navigation, monospace labels and specimen metadata.
- Standardized the active art-direction layer's tape, paper, ink, border, shadow, and texture treatments around the semantic palette.
- Kept existing asymmetrical cuts, rotated paper planes, torn edges, and generous paper margins. No new content sections were introduced.

### CSS cleanup

- Removed the superseded early HTML collage prototype rules (`.collage-paper`, `.collage-disc`, `.collage-star`, etc.) because those elements are no longer present; the current signature artwork is inline SVG.
- Removed obsolete `.ed-about` rules because the current About view uses the profile-column structure instead.
- Kept component-specific diagram and project-content styles separate; they are not global art-direction tokens.

## Explicitly preserved

- Phase 2 SVG path geometry and polygon/polyline geometry: unchanged (SHA-256 of geometry path data: `0984d1da66d8163807289e62b7dc3786085c5e65c98d99d587f297125597d4b5`).
- Phase 2 animation CSS: unchanged (SHA-256: `62905a1976d8b6640e10ed40bf3b822fd46b48f0dd0a57b72ec9aec88d716eaf`).
- Projects: 6; diary posts: 7.
- Existing routes, assets, project diagrams, and source content.

## Contrast spot checks

| Pair | Contrast |
|---|---:|
| Main ink on paper | 13.25:1 |
| Muted text on paper | 5.33:1 |
| Strong accent on paper | 7.46:1 |
| White paper text on plum | 13.06:1 |
| Red accent on white paper | 5.21:1 |

All sampled combinations exceed 4.5:1 for normal text.

## Verification

- `python3 -m unittest discover -s tests -v` — 22/22 passed.
- `python3 -m py_compile scripts/build_projects.py scripts/build_blog.py` — passed.
- Both content builders were run twice; the final `index.html` SHA-256 was identical after the second run.
- `tinycss2` parsed all 8 style blocks with 0 parser errors.
- Exactly one `:root` design-token declaration remains.
- No unmounted prototype selectors listed above remain.
- No unresolved custom properties were found after accounting for component-local variables and fallbacks.
- SVG geometry and animation hashes match the Phase 2 baseline.
- Duplicate HTML IDs: 0; project templates: 6.

## Verification limitation

Chromium is blocked by the execution environment with `ERR_BLOCKED_BY_ADMINISTRATOR` for both `file://` and localhost navigation. WeasyPrint can render the page's static layout but does not render the inline SVG artwork in this document; it is therefore not used as evidence for the creature's visual appearance. No claim is made that real-browser visual regression, touch, or screen-reader testing was completed.

## Status

**Phase 1 implementation and static verification complete.** Phase 2 artwork, Phase 3 archive UX, Phase 4 interactions, and Phase 5 browser/accessibility verification remain unchanged and are outside this phase.
