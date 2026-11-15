# 2026-11-15 — Font roles and collage motion v3

## Typography
- Removed the sidebar A/B type study and all A/B state switching.
- NEXON Lv.1 Gothic remains the global reading/UI font.
- Bithumb Gothic Basic is reserved for selected display headings and project/object titles.
- Removed the unused Jalnan font-face and `data-font-pair` state.

## Motion and visual direction
- Added an original paper-theatre backdrop: irregular cut-paper scraps, stitched lines, registration marks, a geometric rosette, and a dashed orbital frame.
- Kept the existing C → B → A story, but changed the timing to overlapping continuous movement rather than long holds and abrupt stage swaps.
- Main animation: 4.9 seconds; final paper reveal: 1.1 seconds beginning at 4.5 seconds (about 5.6 seconds total).
- Used transform/opacity-only keyframes with small staggered offsets.
- Reduced SVG filter bounds and shadow blur; removed shadow filters from independently animated fragments and limbs while preserving dark cut edges.
- Changed SVG rendering hint to `auto`.
- Replay no longer forces a synchronous layout read; it restarts on the next two animation frames.
- Preserved `prefers-reduced-motion` behavior.
