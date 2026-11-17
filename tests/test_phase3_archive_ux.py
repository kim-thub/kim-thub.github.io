from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


class Phase3ArchiveUXTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX.read_text(encoding="utf-8")

    def test_projects_index_is_a_specimen_shelf(self):
        self.assertIn('<nav class="project-shelf"', self.html)
        self.assertIn('class="project-specimen"', self.html)
        self.assertIn('data-project-index', self.html)
        self.assertIn("OBJECT / 01", self.html)

    def test_project_reader_has_its_own_exhibition_surface(self):
        self.assertIn('class="ed-reader-body project-reader"', self.html)
        self.assertIn(".project-reader .project-case", self.html)

    def test_diary_index_uses_actual_post_excerpts(self):
        self.assertIn('<nav class="diary-index"', self.html)
        self.assertIn("card.className='diary-entry'", self.html)
        self.assertIn("post.excerpt", self.html)
        self.assertNotIn("a.className='ed-entry ed-post-entry'", self.html)

    def test_diary_reader_is_a_notebook_not_a_project_case(self):
        self.assertIn('class="ed-reader-body diary-reader"', self.html)
        self.assertIn(".diary-reader .markdown-body", self.html)

    def test_about_is_presented_as_an_owner_field_record(self):
        self.assertIn('profile-archive-sheet', self.html)
        self.assertIn('data-profile-index="owner"', self.html)
        self.assertIn("PERSONAL INDEX / PEOPLE & PATTERNS", self.html)

    def test_project_index_builder_emits_the_specimen_shelf(self):
        import sys
        sys.path.insert(0, str(ROOT / "scripts"))
        from build_projects import replace_project_index

        rebuilt = replace_project_index(self.html)
        self.assertIn('class="project-shelf"', rebuilt)
        self.assertEqual(rebuilt.count('class="project-specimen"'), 6)
        self.assertIn('href="#project/spot-radar"', rebuilt)

    def test_phase3_removes_the_shared_generic_index_styles(self):
        self.assertNotIn('.ed-index .ed-entry', self.html)
        self.assertNotIn('.ed-post-index', self.html)

    def test_phase3_does_not_change_project_or_post_counts(self):
        self.assertEqual(len(re.findall(r'<template id="tpl-[^\"]+">', self.html)), 6)
        match = re.search(r'<script id="blog-posts-data" type="application/json">(.*?)</script>', self.html, re.S)
        self.assertIsNotNone(match)
        source_posts = [path for path in (ROOT / "content" / "posts").glob("*.md") if path.name != "README.md"]
        self.assertEqual(len(json.loads(match.group(1))), len(source_posts))


if __name__ == "__main__":
    unittest.main()
