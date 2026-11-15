# Phase 2 — Signature Experience

## Scope

This change is limited to the Paper Collage Archive home artwork and the logic that starts its one-time reveal. Project content, diary content, profile content, navigation design, global palette, and other phases were not redesigned.

## Implemented

### C — Specimen fragments

- Replaced the previous ten-ish generic fragments with eight distinct torn-paper specimens.
- Added detached hooked/jointed fragments, stitched marks, measurement ticks, punch holes, and specimen annotations.
- Kept the pieces spatially unresolved so they suggest an anatomy without forming a recognizable body.

### B — Impossible fold

- Replaced the former simple polygon with an overlapping folded sheet made from independently animated paper planes.
- Added an off-center hollow, mismatched crease directions, unaligned joints, and duplicate hinge marks at visibly different scales.
- The fold reads as an unstable intermediate structure rather than a finished character.

### A — The Unbound Index

- Built a new asymmetric, nonhuman archive creature from layered torn-paper planes and angular paper ribbons.
- Added a hollow center, embedded book-spine segments, a duplicated/mismatched limb pair, and long appendages that cross the SVG viewport edges.
- Kept the silhouette deliberately headless and anatomically inconsistent.

## Motion and accessibility

- C → B → A is an 8.8-second CSS/SVG sequence with one iteration and no replay control.
- The reveal starts only when the home view is first entered. Opening a project URL directly does not consume the animation.
- The final A form is the no-JavaScript fallback and is shown immediately under `prefers-reduced-motion`.
- The SVG has an accessible title and description; the visible specimen caption remains separate.
- No external image, font, animation, or runtime dependency was added.

## Verification evidence

- `python3 -m unittest discover -s tests -v` — 18/18 passed.
- `python3 -m py_compile scripts/build_projects.py scripts/build_blog.py` — passed.
- Both builders were run twice; project and post counts remained 6 and 7.
- CSS parsed with tinycss2 — 8 style blocks, 0 parse errors.
- Both inline JavaScript blocks passed `node --check`.
- Chromium rendered the C, B, and A frames separately with the expected visible state at each point; no page errors were reported.
- Document horizontal overflow was 0 at 320, 360, 390, 430, and 1440 CSS pixels.
- With reduced motion enabled, C and B are hidden and A is visible immediately.
- Direct entry to `#project/spot-radar` leaves the reveal unplayed; navigating to `#home` starts it.

## Not included in this phase

- Global design-token cleanup (Phase 1).
- Distinct archive-reading layouts (Phase 3).
- Page transitions and broader micro-interactions (Phase 4).
- Full assistive-technology testing with a screen reader.
