# 2026-11-15 — Home, learning timeline, and blog ordering polish

- About / Learning: sorted by start date, newest first. The degree is no longer forced to the first row.
- Home: removed the two top-left SVG labels from the C and B motion stages.
- Home layout: constrained the artwork to the main grid column and removed the Home-only decorative strip at the sidebar boundary.
- Motion: shortened the C → B → A sequence from 8.8s to 6s, tightened fragment staggering, and shortened the paper-reverse transition to 1.45s beginning at 5.55s. The choreography and easing remain intact.
- Project objects: moved OPEN to a dedicated top-right label, reserving space beside the folio number and keeping it out of the title/description area.
- Blog: added an explicit `index_order` field so 01–07 follows the project archive's latest-first sequence. The UI continues to show post numbers, not dates.
- Future Markdown posts: documented how to maintain `index_order` in `content/posts/README.md`.
