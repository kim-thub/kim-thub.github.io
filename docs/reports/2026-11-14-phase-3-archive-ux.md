# Phase 3 — Archive UX

## Scope

Differentiate the browsing and reading experience for Projects, Diary, and About without adding new portfolio content or changing project facts. Preserve the six project records, seven diary posts, existing hash routes, project table of contents, back-to-list links, and related-post links.

## Changes

### Projects — specimen shelf

- Replaced the shared generic `.ed-entry` list with a dedicated `project-shelf` navigation landmark.
- Each project is now an `OBJECT / NN` specimen card with its existing category, title, excerpt, and an `OPEN RECORD` footer.
- Project detail pages use a distinct exhibition surface: project lede, structured facts panel, and section markers styled as field labels.
- Updated `scripts/build_projects.py` to generate the shelf from `PROJECT_INDEX` and HTML-escape the displayed strings.
- Removed the old generic index CSS selectors and the obsolete `replace_blurb()` patch path. The builder now regenerates the entire project index in one idempotent pass.

### Diary — field notebook

- Replaced the shared project-list structure with a dedicated `diary-index` navigation landmark.
- Each entry receives a folio number, note format label, title, the post's own `excerpt`, and a `READ NOTE` link.
- Corrected a pre-existing rendering bug: every diary card previously displayed the same AI Starter Kit excerpt, regardless of the post's actual content.
- Diary detail pages use a separate notebook reading surface with ruled-paper texture and a margin line. The Markdown body, tables, code blocks, and source content remain intact.

### About — owner field record

- Reframed the existing About page as `OWNER / FIELD RECORD` and a profile archive sheet.
- Kept the existing prose, collaboration/follow-up/learning/records sections, and internal project links unchanged.
- Added a paper dossier surface and a distinct two-column introduction / two-by-two record layout, collapsing to one column on narrow screens.

## Preserved

- Project source files and diary Markdown files: 15 files byte-identical to the Phase 1 source.
- Project templates: 6.
- Diary records: 7.
- Existing project/post slugs and hash routes.
- Project TOC generation, back-to-list navigation, and related-post previews.
- Phase 2 SVG path geometry and animation CSS unchanged.
- Phase 1 palette and Phase 2 signature artwork unchanged.
- No new external dependencies, content sections, contact details, CV links, or employment-oriented copy.

## Verification

- `python3 -m unittest discover -s tests -v` — 30/30 passed.
- `python3 -m py_compile scripts/build_projects.py scripts/build_blog.py tests/test_archive_contract.py tests/test_phase3_archive_ux.py` — passed.
- `node --check` on the executable inline JavaScript — passed.
- `tinycss2` parsed 9 style blocks with 0 CSS parser errors.
- Duplicate HTML IDs: 0.
- Missing local image assets: 0.
- Project templates: 6; diary records: 7.
- All internal `#project/<slug>` and `#post/<slug>` routes resolve to known records.
- Both content builders were run twice; `index.html` SHA-256 was identical after the second run: `adcdb311a17646ed4130ca2deedb140702097dbb614545c0782f3a31c7dd74a5`.
- Phase 1 content files: 15/15 byte-identical.
- Static layout previews were generated for Projects and About using WeasyPrint.

## Verification limitation

A Chromium headless attempt did not complete in this environment; its log contains unavailable D-Bus/system-bus errors and the command timed out. Therefore real-browser route interaction, mobile touch behavior, computed layout at device widths, and screen-reader behavior are not claimed as verified. WeasyPrint was used only for static layout inspection; its grid implementation is not a substitute for browser verification of the dynamic Diary list.

## Status

**Phase 3 implementation and static verification complete.** Phase 4 micro-interactions and Phase 5 browser/accessibility finish remain unchanged and out of scope.
