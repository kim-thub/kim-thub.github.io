# Portfolio mobile, content, and collage revision

## Intent

Revise the three local portfolio previews so they remain readable on mobile, the mini-home room stays aligned at responsive sizes, and concept 02 becomes clearly nonhuman and uncanny. Keep each project as an independent detail page, while moving project-specific technical deep dives out of those pages into editable Markdown blog posts.

The user selected a staged transformation for concept 02: **C → B → A**. The image should begin as scattered specimen fragments, fold into an impossible paper form, and resolve into an original, distorted archive creature.

## Current findings

- Project and blog tables include `min-width: 520px`. Several are not constrained by a parent scroll region, so the table can exceed a narrow viewport. The starter-kit evaluation table has four columns and is the clearest readability problem.
- The mini-home uses a 900×480 SVG room. Its avatar button is absolutely positioned with viewport-like percentages, while the room itself is not its positioned container. The button can drift away from the avatar when the grid changes at responsive breakpoints.
- Concept 02 layers paper shapes but keeps a centered, coherent creature-like composition. Its silhouette and spatial hierarchy still read as an ordinary illustration.
- Project templates are duplicated across all three standalone HTML files. `scripts/build_blog.py` already reads Markdown files in `content/posts/` and injects their contents into all three pages.
- Project detail pages currently mix project context with migration, benchmark, trade-off, implementation, and test narratives. Blog routes support independent Markdown posts, but project pages have no links to those posts.

## Goals

1. Prevent page-level horizontal overflow at 320, 360, 390, and 430 CSS-pixel widths. Keep all table content available and legible on mobile.
2. Keep the mini-room's SVG proportions and anchor the avatar status trigger to the avatar's actual responsive position. Ensure the trigger remains keyboard and touch accessible.
3. Make concept 02's opening transform visibly progress C → B → A, with an unmistakably nonhuman final form and legible navigation.
4. Give every project page a concise overview of the project itself: audience, problem or purpose, project type/period, result/artifact, the user's role, and implementation boundary.
5. Retain compact diagrams that explain project architecture or the user's implementation scope. Move detailed technical evidence, choices, tests, trade-offs, and code excerpts into relevant Markdown posts linked from the project page.
6. Remove prose whose sole job is to justify a code excerpt. Put only useful non-obvious intent in code comments, without line-by-line narration.

## Non-goals

- Do not publish or push changes to the public GitHub Pages site.
- Do not merge the three concept layouts into one shared visual design; make only the responsive fixes each concept needs.
- Do not invent project results, test coverage, ownership, or technical decisions while moving content.
- Do not add external image, font, animation, or sound dependencies.
- Do not change the existing APM article's substance.

## Approaches considered

### Mobile tables

- **Bounded horizontal scroll for every table:** minimal change and preserves tabular semantics, but dense four-column comparisons remain difficult to read on a phone.
- **Responsive record cards for wide comparison tables, bounded scrolling for genuinely tabular long data:** clearer on phones and keeps desktop comparison tables. The mobile card view must be generated from the same headers and cells so values cannot drift. **Selected.**

### Mini-home alignment

- **Tune breakpoints and margins only:** quick, but leaves the avatar button detached from the scene's coordinate system.
- **Use a positioned room frame with a preserved 900:480 aspect ratio and place the avatar trigger relative to that frame:** addresses the root cause and stays accurate across breakpoints. **Selected.**

### Concept 02 creature

- **C → B → A staged transformation:** fragments become an impossible fold and resolve into the most distorted form. **Selected by the user.**
- A static A form would be simpler but would lose the staged reveal.
- C or B as the final form would remain more abstract, but would not deliver the desired grotesque payoff.

### Project detail and blog split

- **One large article for all projects:** fewer posts, but project narratives would be mixed and links less specific.
- **One Markdown post per project, with the starter-kit divided into RAG evidence and bootstrap/package implementation:** articles remain focused while all non-overview details have a clear home. **Selected.**

## Design and content decisions

### Responsive tables

- Inventory every table in project templates, the existing APM article, and Markdown rendering.
- Keep compact tables in a width-constrained scroll wrapper with visible mobile affordance; never allow the table to increase document width.
- For comparison tables with three or more meaningful columns, provide a mobile card for each data row. Each field label comes from the table header, and card values are generated from the same table source.
- Preserve table headers and row order on desktop. Do not shrink dense text to an unreadable size.
- Verify document width and cell/card bounds at the four target widths.

### Mini-home

- Wrap the room SVG and avatar trigger in one positioned scene container. Set its aspect ratio to 900:480, keep the SVG at `width: 100%; height: auto`, and calculate the trigger's position from the SVG viewBox coordinates rather than an unrelated page percentage.
- At mobile widths, stack profile, room, and right-side information in one column. Prevent fixed-width children and decorative shadows from extending beyond the viewport.
- Keep the existing pixel-room content and status modal; the status trigger must have a useful accessible name and a practical touch target.

### Concept 02: C → B → A

1. **C — Specimen fragments:** scattered paper, ink, stitched marks, and detached anatomical-looking pieces; labels and measurement lines imply a specimen but do not resolve its anatomy.
2. **B — Impossible fold:** fragments fold and overlap into an unstable body. Perspective and negative space become inconsistent; joints do not align, and repeated parts disagree in scale.
3. **A — Archive creature:** the fragments resolve into a large, asymmetric, original nonhuman form. A missing or hollow face, book-spine-like segments, duplicated or mismatched limbs, and torn edges should make it feel malformed rather than like a person in a costume. Some mass should breach the viewport edges.

- Build from inline SVG shapes and CSS transforms; do not import character art or add a runtime animation library.
- Run the transformation once when the 02 home view opens. Keep project navigation labels and click targets separate from moving art. Do not add a replay control.
- Under `prefers-reduced-motion`, show the final A composition immediately. Keep reading/detail pages calm and readable.

### Project pages and Markdown articles

Each project page keeps a brief overview, the project's purpose and audience, type/period, artifact or outcome, the user's exact contribution, stack, and a compact diagram that reflects confirmed project structure and ownership. Detailed code, metrics, decision paths, trade-offs, tests, and learning move to Markdown articles. Project-page links appear beside the overview diagram or the specific topic summary they expand.

Proposed articles:

| Slug | Project | Content moved from project details |
|---|---|---|
| `spot-radar-spring-migration` | SPOT RADAR | API-contract migration, Projection/query reduction, measured performance, cache choice and trade-off |
| `starterkit-rag-evaluation` | 상속길잡이 스타터킷 | Chunking comparison, 512-token input budget, PDF overflow, XLSX row preservation, provenance and evaluation limits |
| `starterkit-local-bootstrap` | 상속길잡이 스타터킷 | Bootstrap profiles, OS-dependent installation decision, encrypted local secrets, OCI packaging |
| `github-taskflow-safe-workflow` | GitHub Taskflow | Git state safety, `--adopt` boundaries, worktree/change preservation, test setup and limits |
| `webtoon-feedback-pipeline` | Webtoon Feedback | User-owned analysis/storage flow, label consistency, duplicate handling, manual verification and team boundary |
| `job-process-automation-notes` | Job Process Automation | Implemented mail pipeline, manual verification only, and paused development state |

The existing APM Markdown article remains unchanged. New articles preserve evidence and uncertainty from the current project material. Code snippets move with each narrative; their surrounding “why this code is included” prose is removed and relevant rationale is expressed as concise code comments.

## Constraints and trade-offs

- Maintaining three independent HTML files keeps each preview portable but risks content drift. The blog build script updates all three; project content changes must be applied consistently and checked across variants.
- Generating mobile cards duplicates the rendered presentation, not the source data. Desktop table and mobile cards must be created from one table structure.
- The staged creature animation adds a short visual pause before the final shape. It must not block navigation or delay access to the page; reduced-motion users see the final shape directly.
- Splitting dense case studies into posts adds blog length, but keeps project pages scannable and gives each technical topic a focused destination.

## Validation

- Run the Markdown builder and verify each new slug appears once in every HTML file.
- Verify every project detail page has an overview, an implementation-scope diagram, and links to its related posts; no technical deep-dive section remains duplicated there.
- Check all project and blog tables at 320, 360, 390, and 430px. Confirm the document itself has no horizontal overflow, card labels match headers, and any intentional table scroller stays inside its panel.
- Check the mini-home's avatar trigger overlays the avatar and opens/closes the status dialog at desktop and mobile sizes, including keyboard navigation.
- Check C → B → A timing and final shape, independent project routes, links from project pages to articles, and the reduced-motion final state.
- Parse all three HTML files and run `node --check` on inline JavaScript. Do not publish.

## Open to implementation judgment

- Exact SVG geometry, palette adjustment within the existing concept, and animation easing/duration are implementation choices as long as the C → B → A progression is unmistakable, performant, and does not obscure navigation.
- Article prose should be edited for clarity while preserving all documented facts, distinctions, and caveats.
