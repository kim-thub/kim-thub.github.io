# Paper Collage Archive Main — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** `02 — Paper Collage Archive`를 유일한 `index.html`로 만들고 01 시안 및 불필요한 레거시 분기를 제거하면서 개인 아카이브의 시각·탐색·접근성 완성도를 높인다.

**Architecture:** 기존 02 HTML을 루트 페이지로 승격한다. 두 Python 빌더는 단일 `index.html`에만 콘텐츠를 삽입한다. 기존 프로젝트/다이어리 원고와 복잡한 도식은 유지하고, 공통 토큰·사이드바·아카이브 전용 CSS 및 접근성 구조만 정돈한다.

**Tech Stack:** Static HTML, CSS, inline SVG, vanilla JavaScript, Python 3, Pygments, Python `unittest`.

**Spec:** `docs/superpowers/specs/2026-11-14-paper-collage-archive-main-design.md`

## Global Constraints

- 취업용 CTA, 연락처, 이력서, 스킬 목록, 프로젝트 추가 금지.
- 기존 프로젝트 6개와 다이어리 7개의 사실·지표·기여·한계 보존.
- 외부 런타임/폰트/이미지/모션 의존성 추가 금지.
- 공개 배포, 푸시, 원본 ZIP 덮어쓰기 금지.
- `index.html`만 canonical page; 01/02 preview 파일 제거.
- C → B → A 모션과 reduced-motion의 A 최종 형태 유지.

## Review Focus

- 루트 직접 진입, 새로고침, `#project/<slug>` 및 `#post/<slug>` 직접 진입.
- 320px 폭에서 사이드바/표/코드/콜라주가 문서 너비를 확장하지 않는지.
- 키보드만으로 홈·프로젝트·다이어리·목차를 탐색할 수 있는지.
- reduced-motion에서 C/B 중간 프레임 없이 A가 보이는지.
- 빌더 반복 실행 시 프로젝트/다이어리/TOC/style 데이터가 중복되지 않는지.

---

### Task 1: Single-entry archive contract

**Files:**
- Create: `tests/test_archive_contract.py`
- Modify: `index.html`
- Delete: `01-diff-reader.html`
- Delete: `02-paper-collage.html` (after its contents are promoted to `index.html`)
- Modify: `README.txt`
- Modify: `scripts/build_projects.py`
- Modify: `scripts/build_blog.py`

**Interfaces:**
- Both build scripts target `ROOT / "index.html"` only.
- `index.html` contains the editorial archive route structure and six project templates.

- [x] **Step 1: Write failing archive contract tests**
  - `test_root_is_paper_collage_archive`
  - `test_legacy_preview_files_are_removed`
  - `test_sidebar_has_real_markup_not_regex_placeholders`
  - `test_build_scripts_target_only_root_index`
  - `test_existing_project_and_post_content_counts_are_preserved`
- [x] **Step 2: Run tests and verify expected failures**
  - Run: `python3 -m unittest discover -s tests -v`
  - Expected: fail because root is still a chooser, old files exist, sidebar placeholders remain, builders still target previews.
- [x] **Step 3: Promote 02 to `index.html` and rebuild the sidebar**
  - Replace the chooser `index.html` with the 02 HTML source.
  - Insert a complete `<aside class="ed-rail">` containing brand, global navigation, project TOC, and profile note; remove literal `\\1`/`\\2`.
  - Add a skip link and `id="main-content"` to the main element.
- [x] **Step 4: Make both builders target `index.html` only**
  - Remove multi-page `HTML_FILES` loops and 01-specific branches.
  - Keep the existing editorial project list, Markdown blog generation, and syntax highlighting.
  - Make `ensure_project_toc_markup()` idempotently ensure the editorial nav without regex backreference strings.
- [x] **Step 5: Remove the 01 and old 02 files; update README**
  - README states `index.html` is the only entry point and there is no design chooser.
  - Remove old standalone HTML filenames from references.
- [x] **Step 6: Run focused tests and both builders**
  - Run: `python3 -m unittest discover -s tests -v`
  - Run: `python3 scripts/build_projects.py && python3 scripts/build_blog.py`
  - Expected: all archive contract tests pass; build output reports six projects and seven posts.

### Task 2: Cohesive paper-collage art direction

**Files:**
- Modify: `index.html`
- Test: `tests/test_archive_contract.py`

**Interfaces:**
- CSS custom properties define the single archive palette.
- Existing route markup, project templates, and SVG art remain intact.

- [x] **Step 1: Add failing design-token and hero-copy assertions**
  - Assert the canonical token names and that the approved archive-intro copy exists.
- [x] **Step 2: Run the focused tests and verify failure**
- [x] **Step 3: Consolidate the root palette**
  - Use warm paper, ink/plum, muted annotation, vermilion, ochre, and lavender as the one palette.
  - Update `theme-color` to match the paper surface.
  - Remove duplicate `:root` overrides while retaining project-specific semantic tokens.
- [x] **Step 4: Refine the home composition**
  - Use the approved personal-archive direction, not a job-seeking introduction.
  - Refine hierarchy, specimen labels, spacing, paper edges, collage frame, and type pairing.
  - Preserve the C → B → A SVG artwork and its timing.
- [x] **Step 5: Run tests and inspect generated CSS/HTML**
  - Run: `python3 -m unittest discover -s tests -v`
  - Parse every style block with `tinycss2` when available; otherwise run a brace-balance and selector sanity check.

### Task 3: Archive navigation and micro-interactions

**Files:**
- Modify: `index.html`
- Test: `tests/test_archive_contract.py`

**Interfaces:**
- Navigation links keep existing hash routes: `#home`, `#projects`, `#blog`, `#about`.
- Project TOC is generated from `.case-copy h3` and remains hidden outside project detail routes.

- [x] **Step 1: Add failing navigation and interaction assertions**
  - Check route links, active-state semantics, TOC target behavior, and no unused game route.
- [x] **Step 2: Verify failure**
- [x] **Step 3: Repair global navigation and route semantics**
  - Add `aria-label`, active `aria-current`, clear project TOC on non-project routes.
  - Preserve direct hash routing and back-to-list links.
- [x] **Step 4: Refine archive hover/focus/entry states**
  - Keep motion subtle and use CSS transitions only.
  - Ensure hover has a matching visible keyboard focus state.
  - Add `scroll-margin-top` to reader headings and prevent animated art from covering controls.
- [x] **Step 5: Remove unused 01/minihome/game branches**
  - Remove P5 and mini post-card variants, stale game route, unused brick-breaker script, and obsolete selectors only when no markup or runtime reference remains.
- [x] **Step 6: Run focused tests and `node --check` on every inline script**

### Task 4: Responsive and accessibility finish

**Files:**
- Modify: `index.html`
- Test: `tests/test_archive_contract.py`

- [x] **Step 1: Add failing responsive and reduced-motion assertions**
  - Assert media queries for 850/700/520/360 widths, reduced motion, focus-visible, skip-link, and table containment.
- [x] **Step 2: Verify failure**
- [x] **Step 3: Tune the responsive rail, hero, archive entries, diagrams, tables, and code blocks**
  - Preserve readable type; do not shrink dense content to fit.
  - Ensure decorative transforms and shadows do not create page-level horizontal overflow.
- [x] **Step 4: Complete keyboard and reduced-motion states**
  - Keep skip link visible on focus.
  - Keep a visible focus ring on anchors and buttons.
  - Show the final A artwork immediately when reduced motion is requested.
- [x] **Step 5: Run static checks at 320/360/390/430px and CSS parse checks**
  - If browser execution remains blocked, record that limitation instead of claiming a visual pass.

### Task 5: Final archive build and evidence report

**Files:**
- Modify: `README.txt`
- Create: `docs/reports/2026-11-14-paper-collage-archive-revision.md`
- Test: `tests/test_archive_contract.py`

- [x] **Step 1: Run both builders twice and compare output hashes**
  - Expected: second build is idempotent.
- [x] **Step 2: Verify HTML structure, internal routes, project/post counts, local asset paths, Python compilation, and inline JavaScript syntax**
- [x] **Step 3: Review facts and copy**
  - Confirm no project facts, measurements, contribution boundaries, or caveats changed.
  - Apply F1/F2/F3 checks to the README and archive microcopy only; do not flatten authored technical prose.
- [x] **Step 4: Write an evidence-led report**
  - Separate expected behavior, actual changes, command output, untested browser behavior, and remaining risks.
- [x] **Step 5: Package the working copy as a new ZIP**
  - Keep original ZIP untouched; do not publish or push.


**Execution note:** 13 automated tests pass; static checks, CSS parsing, inline JavaScript syntax, asset/link integrity, and two-pass build idempotence completed. Actual Chromium rendering and real assistive-technology testing remain unverified because the container browser was blocked by administrator policy; see `docs/reports/2026-11-14-paper-collage-archive-revision.md`.
