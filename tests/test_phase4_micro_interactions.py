from __future__ import annotations
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
CSS = (ROOT / "assets" / "css" / "style.css").read_text(encoding="utf-8")
APP_JS = (ROOT / "assets" / "js" / "app.js").read_text(encoding="utf-8")

class Phase4MicroInteractionTests(unittest.TestCase):
    def test_route_transition_has_reduced_motion_fallback(self):
        self.assertIn("@keyframes archive-view-arrive", CSS)
        self.assertIn('.view[data-entering="true"]', CSS)
        self.assertIn('@media(prefers-reduced-motion:reduce)', CSS)
        self.assertIn('.view[data-entering="true"]{animation:none!important}', CSS)
        self.assertIn('data-entering', APP_JS)

    def test_keyboard_route_navigation_moves_focus_to_new_view_heading(self):
        self.assertIn('data-route-focus', APP_JS)
        self.assertIn('keyboardNavigation', APP_JS)
        self.assertIn('focus({preventScroll:true})', APP_JS)
        self.assertIn("else if(route.startsWith('post/'))focusTarget=activeView?.querySelector('.diary-reader-head h1')", APP_JS)
        self.assertNotIn("#active-post h1');", APP_JS)

    def test_paper_cards_have_pointer_light_and_hover_focus_states(self):
        self.assertIn('--paper-pointer-x', CSS)
        self.assertIn('--paper-pointer-y', CSS)
        self.assertIn('.project-specimen:hover', CSS)
        self.assertIn('.project-specimen:focus-visible', CSS)
        self.assertIn('.diary-entry:focus-visible', CSS)
        self.assertIn('pointermove', APP_JS)

    def test_code_blocks_expand_on_desktop_hover_and_keyboard_focus(self):
        self.assertIn('@media (min-width:851px) and (hover:hover) and (pointer:fine)', CSS)
        self.assertIn('.portfolio-code:hover{', CSS)
        self.assertIn('.portfolio-code:focus-within{', CSS)
        self.assertIn('calc(100vw - 351px)', CSS)
        self.assertIn('calc(50vw + 260px)', CSS)
        self.assertIn('min(1000px', CSS)
        self.assertIn('.portfolio-code pre:focus-visible', CSS)

        focusability = APP_JS.index("if(!pre.hasAttribute('tabindex'))pre.tabIndex=0;")
        existing_frame_return = APP_JS.index("if(pre.closest('.portfolio-code'))return;")
        self.assertLess(focusability, existing_frame_return)
        self.assertIn('overflow:auto', CSS)
        self.assertIn('@media (max-width:850px)', CSS)
        self.assertIn('.portfolio-code:hover,.portfolio-code:focus-within{width:100%;max-width:100%;box-shadow:none;}', CSS)

        import sys
        sys.path.insert(0, str(ROOT / 'scripts'))
        from build_projects import update_project_router
        self.assertIn("if(!pre.hasAttribute('tabindex'))pre.tabIndex=0;", update_project_router(APP_JS))

    def test_project_toc_keeps_active_item_in_view(self):
        self.assertIn('containerRect=toc.getBoundingClientRect(),itemRect=activeButton.getBoundingClientRect()', APP_JS)
        self.assertIn('toc.scrollLeft', APP_JS)
        self.assertIn('toc.scrollTop', APP_JS)
        self.assertNotIn('activeButton.scrollIntoView', APP_JS)

    def test_project_builder_preserves_phase4_toc_behavior(self):
        import sys
        sys.path.insert(0, str(ROOT / 'scripts'))
        from build_projects import update_project_router
        rebuilt = update_project_router(APP_JS)
        self.assertIn('containerRect=toc.getBoundingClientRect(),itemRect=activeButton.getBoundingClientRect()', rebuilt)
        self.assertNotIn('activeButton.scrollIntoView', rebuilt)

    def test_phase4_does_not_add_external_animation_dependencies(self):
        self.assertNotRegex(HTML, r'<script[^>]+src="https?://')

if __name__ == '__main__':
    unittest.main()
