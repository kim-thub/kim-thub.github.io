# Home Motion & Patchwork Scene Revision

## Decisions
- Removed scroll scrubbing. The C → B → A artwork now runs as a time-based sequence with its original easing and a small stagger between paper fragments.
- The Home view stays within one viewport; it no longer stretches to 300svh or pins the scene during scrolling.
- After the A form settles, the final scene arrives as a page-reverse transition. A replay control restarts the sequence.
- Rebuilt the final scene as an original patchwork cabinet of six clickable project objects.
- Removed all project screenshot images from the Home final scene. Project images remain in their own project detail pages.
- Replaced the generic “만들고, 모으고, 다시 펼쳐보는 것들” copy with the direct invitation “어디부터 열어볼까요?” and a short interaction hint.
- The six objects are original CSS/SVG paper illustrations: manual, map/radar, terminal ticket, envelope, comic fragment, and field guide.
- Blog, About, and Contact remain as small secondary links, not cards.

## Motion
- Automatic C → B → A sequence: 8.8 seconds.
- The final paper-reverse scene starts after the artwork has settled.
- Up/down scrolling no longer changes animation progress.
- `prefers-reduced-motion` skips the transition and exposes the final scene immediately.

## Type
- Titles: Bithumb Gothic Basic.
- Body/UI: NEXON Lv.1 Gothic.
- Code and technical metadata: monospace.
