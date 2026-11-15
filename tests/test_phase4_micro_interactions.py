from __future__ import annotations
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")

class Phase4MicroInteractionTests(unittest.TestCase):
    def test_route_transition_has_reduced_motion_fallback(self):
        self.assertIn("@keyframes archive-view-arrive", HTML)
        self.assertIn('.view[data-entering="true"]', HTML)
        self.assertIn('@media(prefers-reduced-motion:reduce)', HTML)
        self.assertIn('.view[data-entering="true"]{animation:none!important}', HTML)
        self.assertIn('data-entering', HTML)

    def test_keyboard_route_navigation_moves_focus_to_new_view_heading(self):
        self.assertIn('data-route-focus', HTML)
        self.assertIn('keyboardNavigation', HTML)
        self.assertIn('focus({preventScroll:true})', HTML)
        self.assertIn("else if(route.startsWith('post/'))focusTarget=activeView?.querySelector('.diary-reader-head h1')", HTML)
        self.assertNotIn("#active-post h1');", HTML)

    def test_paper_cards_have_pointer_light_and_hover_focus_states(self):
        self.assertIn('--paper-pointer-x', HTML)
        self.assertIn('--paper-pointer-y', HTML)
        self.assertIn('.project-specimen:hover', HTML)
        self.assertIn('.project-specimen:focus-visible', HTML)
        self.assertIn('.diary-entry:focus-visible', HTML)
        self.assertIn('pointermove', HTML)

    def test_project_toc_keeps_active_item_in_view(self):
        self.assertIn('containerRect=toc.getBoundingClientRect(),itemRect=activeButton.getBoundingClientRect()', HTML)
        self.assertIn('toc.scrollLeft', HTML)
        self.assertIn('toc.scrollTop', HTML)
        self.assertNotIn('activeButton.scrollIntoView', HTML)

    def test_project_builder_preserves_phase4_toc_behavior(self):
        import sys
        sys.path.insert(0, str(ROOT / 'scripts'))
        from build_projects import update_project_router
        rebuilt = update_project_router(HTML)
        self.assertIn('containerRect=toc.getBoundingClientRect(),itemRect=activeButton.getBoundingClientRect()', rebuilt)
        self.assertNotIn('activeButton.scrollIntoView', rebuilt)

    def test_phase4_does_not_add_external_animation_dependencies(self):
        self.assertNotRegex(HTML, r'<script[^>]+src="https?://')

if __name__ == '__main__':
    unittest.main()
