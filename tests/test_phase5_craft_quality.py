from __future__ import annotations

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
CSS = (ROOT / "assets" / "css" / "style.css").read_text(encoding="utf-8")
APP_JS = (ROOT / "assets" / "js" / "app.js").read_text(encoding="utf-8")


def contrast_ratio(foreground: str, background: str) -> float:
    def luminance(color: str) -> float:
        value = color.lstrip("#")
        channels = [int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        linear = [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4 for channel in channels]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

    lighter, darker = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


class Phase5CraftQualityTests(unittest.TestCase):
    def test_project_detail_promotes_template_title_to_visible_page_heading(self):
        self.assertIn('data-project-title', HTML)
        self.assertRegex(APP_JS, r"projectHeading\.textContent\s*=\s*projectSourceTitle")
        self.assertRegex(APP_JS, r"projectSourceTitle\.remove\(\)")

    def test_diary_detail_has_a_visible_title_and_removes_duplicate_article_h1(self):
        self.assertIn('data-post-title', APP_JS)
        self.assertRegex(APP_JS, r"postHeading\?\.textContent\.trim\(\)")
        self.assertRegex(APP_JS, r"postHeading\.remove\(\)")
        self.assertIn(".diary-reader-head h1", CSS)

    def test_keyboard_navigation_focuses_visible_diary_title(self):
        self.assertIn(".diary-reader-head h1", CSS)
        self.assertRegex(APP_JS, r"else if\(route\.startsWith\('post/'\)\)focusTarget=activeView\?\.querySelector\([^;]*diary-reader-head h1")

    def test_clipped_navigation_shape_keeps_a_visible_keyboard_focus_ring(self):
        self.assertRegex(CSS, r"\.ed-nav a:focus-visible\s*\{[^}]*clip-path\s*:\s*none")
        self.assertRegex(CSS, r"\.ed-nav a:focus-visible\s*\{[^}]*outline\s*:\s*3px")

    def test_small_metadata_text_meets_wcag_aa_contrast_on_its_card_surfaces(self):
        root = re.search(r":root\s*\{(.*?)\}", CSS, re.DOTALL)
        self.assertIsNotNone(root)
        tokens = dict(re.findall(r"(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{6})", root.group(1)))
        # The third home card uses paper-gold; its metadata must not use muted gray.
        self.assertIn("color:var(--ink-soft)", CSS)
        self.assertGreaterEqual(contrast_ratio(tokens["--ink-soft"], tokens["--paper-gold"]), 4.5)
        # Diary READ NOTE appears on alternating sand cards.
        self.assertRegex(CSS, r"\.diary-entry__read\s*\{[^}]*color\s*:\s*var\(--accent-strong\)")
        self.assertGreaterEqual(contrast_ratio(tokens["--accent-strong"], tokens["--paper-sand"]), 4.5)
        # Project specimen metadata also appears on lavender cards.
        self.assertRegex(CSS, r"\.specimen-topline,\s*\.specimen-footer\s*\{[^}]*color\s*:\s*var\(--ink-soft\)")
        self.assertGreaterEqual(contrast_ratio(tokens["--ink-soft"], tokens["--paper-lavender"]), 4.5)
        # Project reader eyebrow sits on a cool-paper header.
        self.assertRegex(CSS, r"\.ed-reader-head small\s*\{[^}]*color\s*:\s*var\(--accent-strong\)")
        self.assertGreaterEqual(contrast_ratio(tokens["--accent-strong"], tokens["--paper-cool"]), 4.5)

    def test_local_images_exist_and_have_nonempty_alt_text(self):
        image_tags = [tag for tag in re.findall(r"<img\b[^>]*>", HTML, re.IGNORECASE) if "esc(safeUrl(url))" not in tag]
        self.assertGreaterEqual(len(image_tags), 5)
        for tag in image_tags:
            src = re.search(r'\bsrc=["\']([^"\']+)', tag)
            alt = re.search(r'\balt=["\']([^"\']*)', tag)
            self.assertIsNotNone(src, tag)
            self.assertIsNotNone(alt, tag)
            self.assertTrue(alt.group(1).strip(), tag)
            self.assertTrue((ROOT / src.group(1)).is_file(), src.group(1))

    def test_markdown_images_have_alt_text_and_existing_assets(self):
        for markdown in (ROOT / "content").rglob("*.md"):
            source = markdown.read_text(encoding="utf-8")
            for alt, asset in re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", source):
                self.assertTrue(alt.strip(), f"{markdown}: {asset}")
                resolved = ROOT / asset if asset.startswith("assets/") else markdown.parent / asset
                self.assertTrue(resolved.resolve().is_file(), f"{markdown}: {asset}")

    def test_external_new_tab_links_are_protected(self):
        for tag in re.findall(r"<a\b[^>]*target=[\"']_blank[\"'][^>]*>", HTML, re.IGNORECASE):
            rel = re.search(r'\brel=["\']([^"\']+)', tag)
            self.assertIsNotNone(rel, tag)
            self.assertTrue({"noopener", "noreferrer"}.issubset(set(rel.group(1).split())), tag)


    def test_route_transition_does_not_rotate_viewport_wider_than_screen(self):
        self.assertIn("@keyframes archive-view-arrive{\n  0%{opacity:0;transform:translateY(11px)}\n  100%{opacity:1;transform:translateY(0)}", CSS)

    def test_project_toc_scrolls_inside_its_own_container(self):
        self.assertIn("containerRect=toc.getBoundingClientRect(),itemRect=activeButton.getBoundingClientRect()", APP_JS)
        self.assertIn("toc.scrollLeft", APP_JS)
        self.assertIn("toc.scrollTop", APP_JS)
        self.assertNotIn("activeButton.scrollIntoView", APP_JS)

    def test_keyboard_navigation_focuses_home_heading_too(self):
        self.assertIn("else if(route==='home')focusTarget=activeView?.querySelector('.ed-home-title')", APP_JS)

    def test_static_hash_links_resolve_to_pages_routes_or_real_ids(self):
        ids = set(re.findall(r'\bid=["\']([^"\']+)', HTML))
        routes = {"home", "projects", "blog", "about"}
        project_slugs = set(re.findall(r'<template id="tpl-([^"]+)"', HTML))
        data = re.search(r'<script id="blog-posts-data" type="application/json">(.*?)</script>', HTML, re.DOTALL)
        self.assertIsNotNone(data)
        import json
        post_slugs = {item["slug"] for item in json.loads(data.group(1))}
        class AnchorParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.hash_links = []
            def handle_starttag(self, tag, attrs):
                if tag == "a":
                    href = dict(attrs).get("href", "")
                    if href.startswith("#"):
                        self.hash_links.append(href)

        parser = AnchorParser()
        parser.feed(HTML)
        for href in parser.hash_links:
            target = href[1:]
            if target in routes or target in ids:
                continue
            if target.startswith("project/"):
                self.assertIn(target[8:], project_slugs, href)
            elif target.startswith("post/"):
                self.assertIn(target[5:], post_slugs, href)
            else:
                self.fail(f"Broken in-page link: {href}")

    def test_responsive_table_enhancement_is_accessibly_named(self):
        self.assertIn("mobile-table-cards", CSS + APP_JS)
        self.assertIn("mobile-card-source", APP_JS)
        self.assertIn("headers[index]", APP_JS)
        self.assertIn("<dt>", HTML)
        self.assertIn("<dd>", HTML)
        self.assertIn('<th scope="col">', APP_JS)


if __name__ == "__main__":
    unittest.main()
