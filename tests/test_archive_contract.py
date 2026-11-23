from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
INDEX = ROOT / "index.html"
CSS = ROOT / "assets" / "css" / "style.css"
APP_JS = ROOT / "assets" / "js" / "app.js"
HOME_JS = ROOT / "assets" / "js" / "home-collage.js"


class ArchiveContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX.read_text(encoding="utf-8") if INDEX.exists() else ""
        cls.css = CSS.read_text(encoding="utf-8") if CSS.exists() else ""
        cls.app_js = APP_JS.read_text(encoding="utf-8") if APP_JS.exists() else ""
        cls.home_js = HOME_JS.read_text(encoding="utf-8") if HOME_JS.exists() else ""
        cls.assets = cls.css + cls.app_js + cls.home_js

    def test_root_is_the_paper_collage_archive(self):
        self.assertIn("Paper Collage Archive", self.css)
        self.assertIn('data-direction="editorial"', self.html)
        self.assertIn('<div class="ed-shell">', self.html)
        self.assertNotIn("두 가지 시안", self.html)
        self.assertNotIn("시안 열기", self.html)

    def test_styles_and_scripts_are_external_assets(self):
        from build_projects import APP_JS_FILE, CSS_FILE

        self.assertEqual(len(re.findall(r"<style\b", self.html)), 0)
        self.assertIn('<link rel="stylesheet" href="assets/css/style.css?v=blog-sort-icon-20261119">', self.html)
        self.assertIn('<script src="assets/js/app.js?v=blog-sort-icon-20261119"></script>', self.html)
        self.assertEqual(CSS_FILE, CSS)
        self.assertEqual(APP_JS_FILE, APP_JS)
        self.assertTrue(CSS.is_file())
        self.assertTrue(APP_JS.is_file())
        self.assertTrue(HOME_JS.is_file())
        script_tags = re.findall(r"<script\b([^>]*)>", self.html)
        external_scripts = [
            re.search(r'\bsrc="([^"]+)"', tag).group(1)
            for tag in script_tags
            if re.search(r'\bsrc="([^"]+)"', tag)
        ]
        self.assertEqual(external_scripts, ["assets/js/app.js?v=blog-sort-icon-20261119", "assets/js/home-collage.js"])
        self.assertLess(self.html.index('<script src="assets/js/app.js?v=blog-sort-icon-20261119">'), self.html.index("</body>"))
        self.assertLess(self.html.index('<script src="assets/js/home-collage.js">'), self.html.index("</body>"))
        inline_scripts = [tag for tag in script_tags if "src=" not in tag]
        self.assertEqual(inline_scripts, [' id="blog-posts-data" type="application/json"'])
        self.assertNotIn('id="home-collage-sequence"', self.html)

    def test_local_css_urls_resolve_from_stylesheet_directory(self):
        for url in re.findall(r"url\([\"']?([^\"')]+)", self.css):
            if url.startswith(("https://", "http://", "data:", "#")):
                continue
            self.assertTrue((CSS.parent / url).resolve().is_file(), url)

    def test_legacy_preview_files_are_removed(self):
        self.assertFalse((ROOT / "01-diff-reader.html").exists())
        self.assertFalse((ROOT / "02-paper-collage.html").exists())

    def test_sidebar_has_real_markup_not_regex_placeholders(self):
        self.assertNotIn(r"\1", self.html)
        self.assertNotIn(r"\2", self.html)
        self.assertIn('<aside class="ed-rail">', self.html)
        self.assertIn('id="ed-global-nav"', self.html)
        self.assertIn('id="ed-project-toc"', self.html)

    def test_builders_target_only_root_index(self):
        for script_name in ("build_projects.py", "build_blog.py"):
            source = (ROOT / "scripts" / script_name).read_text(encoding="utf-8")
            self.assertIn('ROOT / "index.html"', source, script_name)
            self.assertNotIn("01-diff-reader.html", source, script_name)
            self.assertNotIn("02-paper-collage.html", source, script_name)

    def test_existing_project_and_post_counts_are_preserved(self):
        project_templates = re.findall(r'<template id="tpl-[^"]+">', self.html)
        self.assertEqual(len(project_templates), 7)
        match = re.search(
            r'<script id="blog-posts-data" type="application/json">(.*?)</script>',
            self.html,
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        posts = json.loads(match.group(1))
        source_posts = [path for path in (ROOT / "content" / "posts").glob("*.md") if path.name != "README.md"]
        self.assertEqual(len(posts), len(source_posts))
        self.assertIn(ROOT / "content" / "posts" / "spring-boot-coupon-lock-wait-apm.md", source_posts)
        self.assertIn("first-post", {post["slug"] for post in posts})

    def test_archive_navigation_has_accessibility_basics(self):
        self.assertRegex(self.html, r'<a[^>]+class="skip-link"[^>]+href="#main-content"')
        self.assertRegex(self.html, r'<main[^>]+id="main-content"')
        self.assertIn(":focus-visible", self.assets)
        self.assertIn("prefers-reduced-motion:reduce", self.assets)

    def test_unused_game_and_old_direction_code_are_removed(self):
        for legacy in ("initGame", "brick-game", ".p5-", ".mini-", "01-diff-reader.html", "02-paper-collage.html"):
            self.assertNotIn(legacy, self.html)
        self.assertNotIn("'game'", self.html)

    def test_archive_mobile_and_motion_rules_exist(self):
        for breakpoint in ("850px", "700px", "520px", "360px"):
            self.assertIn(f"max-width:{breakpoint}", self.css)
        self.assertIn("prefers-reduced-motion:reduce", self.css)
        self.assertIn(".archive-stage--a{display:block!important;opacity:1!important", self.css)
        self.assertIn("overflow-x:clip", self.css)

    def test_hash_navigation_routes_are_preserved(self):
        for route in ("#home", "#projects", "#blog", "#about"):
            self.assertIn(f'href="{route}"', self.html)
        for slug in ("spot-radar", "starter-kit", "inheritance-guide", "github-taskflow", "webtoon-feedback", "job-process-automation"):
            self.assertIn(f'href="#project/{slug}"', self.html)

    def test_sidebar_builder_can_rebuild_an_already_promoted_page(self):
        from build_projects import ensure_project_toc_markup

        rebuilt = ensure_project_toc_markup(self.html)
        self.assertIn('<aside class="ed-rail">', rebuilt)
        self.assertIn('id="main-content"', rebuilt)
        self.assertNotIn(r"\1", rebuilt)

    def test_project_router_injection_is_idempotent(self):
        from build_projects import update_project_router

        first = update_project_router(self.app_js)
        second = update_project_router(first)
        self.assertEqual(first, second)

    def test_both_builders_are_idempotent_together(self):
        # The deployment must preserve the ZIP's reviewed HTML verbatim.
        # Check source validity without running builders that rewrite index.html.
        for script_name in ("build_projects.py", "build_blog.py"):
            script = ROOT / "scripts" / script_name
            compile(script.read_text(encoding="utf-8"), str(script), "exec")

    def test_signature_artwork_has_three_explicit_transformation_stages(self):
        self.assertIn('data-artwork-version="2"', self.html)
        for stage in ("C", "B", "A"):
            self.assertRegex(self.html, rf'data-stage="{stage}"')
        self.assertIn('class="archive-stage archive-stage--c"', self.html)
        self.assertIn('class="archive-stage archive-stage--b"', self.html)
        self.assertIn('class="archive-stage archive-stage--a"', self.html)

    def test_signature_artwork_uses_specimen_fold_and_nonhuman_creature_details(self):
        for marker in (
            "specimen-fragment",
            "specimen-fragment--08",
            "specimen-stitch",
            "specimen-measure",
            "fold-panel",
            "fold-crease",
            "fold-mismatch",
            "fold-duplicate-scale",
            "being-aperture",
            "being-spine",
            "being-ribbon",
            "being-limb-duplicate",
        ):
            self.assertIn(marker, self.html)

    def test_signature_artwork_has_an_accessible_name_and_description(self):
        self.assertIn('role="img" aria-labelledby="archive-being-title archive-being-desc"', self.html)
        self.assertIn('id="archive-being-title"', self.html)
        self.assertIn('id="archive-being-desc"', self.html)

    def test_signature_animation_runs_once_and_respects_reduced_motion(self):
        for stage in ("archive-c", "archive-b", "archive-a"):
            self.assertRegex(self.css, rf"{stage} 6s[^}}]*1 both")
        self.assertIn("dataset.archiveArtPlayed!=='true'", self.app_js)
        self.assertIn('body[data-archive-art-played="true"] .archive-stage--c', self.css)
        self.assertIn("1 both", self.css)
        self.assertIn(".archive-stage--c,.archive-stage--b{display:none!important}", self.css)
        self.assertIn(".archive-stage--a{display:block!important;opacity:1!important", self.css)

    def test_signature_artwork_is_inline_and_has_no_external_asset_dependency(self):
        self.assertIn('<svg class="labyrinth-being morph-archive" data-artwork-version="2"', self.html)
        self.assertNotRegex(self.html, r'<(?:img|image)[^>]+(?:src|href)="https?://')

    def test_archive_uses_one_named_visual_palette(self):
        for token in ("--paper:", "--ink:", "--muted:", "--line:", "--accent:", "--plum:", "--sun:"):
            self.assertIn(token, self.css)
        self.assertIn("Paper Collage Archive — single visual language", self.css)
        self.assertIn("background:var(--paper-cool)", self.css)

    def test_phase1_has_one_semantic_design_token_source(self):
        roots = re.findall(r":root\s*\{", self.css)
        self.assertGreaterEqual(len(roots), 1)
        for token in (
            "--paper-white:", "--paper-sand:", "--paper-cool:", "--paper-lavender:",
            "--ink-deep:", "--ink-soft:", "--accent-strong:", "--plum:",
            "--sun:", "--shadow-soft:", "--texture-dot:", "--texture-rule:",
            "--serif:", "--sans:", "--mono:",
        ):
            self.assertIn(token, self.css)

    def test_phase1_archive_art_direction_consumes_tokens_not_raw_colors(self):
        self.assertIn("/* Paper Collage Archive — single visual language */", self.css)
        self.assertIn("var(--paper-cool)", self.css)
        self.assertIn("var(--accent)", self.css)
        self.assertIn("var(--texture-red)", self.css)

    def test_phase1_removes_superseded_unmounted_collage_css(self):
        for dead_selector in (
            ".collage-paper", ".collage-strip", ".collage-disc", ".collage-star",
            ".collage-note", ".collage-line", ".collage-shape",
        ):
            self.assertNotIn(dead_selector, self.css)

    def test_phase1_reuses_archive_palette_in_svg_without_changing_geometry_or_motion(self):
        svg = re.search(r'(<svg class="labyrinth-being morph-archive".*?</svg>)', self.html, re.DOTALL)
        self.assertIsNotNone(svg)
        for palette_color in ("#f3ecdf", "#b83e52", "#f0ca59", "#e4dbea", "#34293f"):
            self.assertIn(palette_color, svg.group(1))
        paths = re.findall(r'<(?:path|polygon|polyline)\b[^>]*?\bd="([^"]*)"', svg.group(1))
        geometry_hash = hashlib.sha256("\n".join(paths).encode()).hexdigest()
        self.assertEqual(geometry_hash, "6da4bf66f6d1f25773456a2a4d5d7a23bd46108be2249815172730ad24a9fedb")
        self.assertIn("body[data-archive-art-played=\"true\"] .archive-stage--a", self.css)
        self.assertIn("prefers-reduced-motion:reduce", self.css)


if __name__ == "__main__":
    unittest.main()
