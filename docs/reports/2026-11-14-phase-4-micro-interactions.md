# Phase 4 — Micro-interaction

## Scope

Phase 4 improves the interaction layer only. It preserves the Phase 1 visual tokens, Phase 2 C → B → A artwork and animation, and Phase 3 project / diary / owner-record content and structure.

## Implemented

1. **Route transitions**
   - Active archive views receive a short paper-like entrance transition when the hash route changes.
   - The initial page load does not animate the entire page.
   - `prefers-reduced-motion: reduce` disables the route entrance animation.

2. **Paper-layer response**
   - Project specimens, diary folios, home links, and owner-record panels lift subtly on hover or keyboard focus.
   - A low-contrast radial light follows the pointer on fine-pointer devices.
   - The pointer effect is CSS-variable based and does not add external libraries or assets.
   - Touch devices do not receive sticky hover behavior.

3. **Keyboard and focus behavior**
   - When a route is opened through keyboard navigation, focus moves to the new view's main heading.
   - Pointer navigation does not forcibly move focus.
   - Existing `:focus-visible` outlines remain in place.

4. **Project table of contents**
   - The active section retains `aria-current="location"`.
   - When the active section changes, its TOC button is scrolled into view within the TOC's scroll container.
   - TOC activation continues to move focus to the target heading.

5. **Motion preference**
   - Route, card, navigation, and link transitions are disabled for reduced-motion users.
   - The Phase 2 artwork's existing reduced-motion behavior remains unchanged.

## Verification

- `python -m unittest discover -s tests -v`: 35 tests passed.
- `node --check` on the inline runtime script: passed.
- CSS parsing across 10 style blocks: 0 parse errors.
- Existing build idempotency tests: passed after two rounds of both builders.
- Existing Phase 1/2/3 tests: passed.
- Project records: 6 preserved.
- Diary records: 7 preserved.
- Phase 2 artwork: C/B/A stages and artwork version 2 preserved.
- No external animation script dependency added.

## Browser verification limitation

Chromium is present in the environment, but navigation to both `file://` and localhost URLs is blocked with `net::ERR_BLOCKED_BY_ADMINISTRATOR`. Therefore, actual browser visual inspection and pointer/keyboard interaction playback could not be completed in this environment. Static tests and syntax checks are not presented as substitutes for that browser verification.

## Files changed

- `index.html`
- `scripts/build_projects.py` (keeps the TOC auto-follow behavior when rebuilding)
- `tests/test_phase4_micro_interactions.py`

No project content, diary content, SVG geometry, or existing Phase 1–3 design tokens were changed in this phase.
