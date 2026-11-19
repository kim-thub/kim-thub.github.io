"""Check static assets, SPA routes, and same-page anchors before publishing."""

from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1] / "site"


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids: set[str] = set()
        self.duplicates: set[str] = set()
        self.links: list[str] = []
        self.headings = 0
        self.title = False
        self.views: set[str] = set()
        self.project_slugs: set[str] = set()
        self.post_slugs: set[str] = set()
        self.template_depth = 0

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        in_template = self.template_depth > 0 or tag == "template"
        element_id = attributes.get("id")
        if element_id and not in_template:
            if element_id in self.ids:
                self.duplicates.add(element_id)
            self.ids.add(element_id)
        if tag == "h1" and not in_template:
            self.headings += 1
        if tag == "title":
            self.title = True
        if attributes.get("data-view"):
            self.views.add(attributes["data-view"])
        if tag == "template" and element_id and element_id.startswith("tpl-"):
            self.project_slugs.add(element_id[4:])
        if tag in {"a", "link"} and attributes.get("href"):
            self.links.append(attributes["href"])
        if tag in {"script", "img", "source", "iframe", "video", "audio"}:
            source = attributes.get("src") or attributes.get("poster")
            if source:
                self.links.append(source)
        if tag == "template":
            self.template_depth += 1

    def handle_endtag(self, tag):
        if tag == "template" and self.template_depth:
            self.template_depth -= 1


def target_for(page_path: Path, href: str):
    parts = urlsplit(href)
    if parts.scheme or parts.netloc:
        return None
    target = (page_path.parent / unquote(parts.path)).resolve() if parts.path else page_path
    if target.is_dir():
        target = target / "index.html"
    return target, unquote(parts.fragment)


def main():
    pages = {}
    errors = []
    for page_path in ROOT.rglob("*.html"):
        parsed = Page()
        source = page_path.read_text(encoding="utf-8")
        parsed.feed(source)
        pages[page_path.resolve()] = parsed
        if page_path.resolve() == (ROOT / "index.html").resolve():
            posts = re.search(
                r'<script id="blog-posts-data" type="application/json">(.*?)</script>',
                source,
                re.DOTALL,
            )
            if posts:
                parsed.post_slugs = {item["slug"] for item in json.loads(posts.group(1))}
            is_spa = {"home", "projects", "blog", "about", "detail", "post-detail"}.issubset(parsed.views)
            headings_valid = is_spa and parsed.headings >= 1
        else:
            headings_valid = parsed.headings == 1
        if not headings_valid or not parsed.title:
            errors.append(f"{page_path}: title or expected h1 count missing")
        for duplicate in parsed.duplicates:
            errors.append(f"{page_path}: duplicate id #{duplicate}")

    for page_path, parsed in pages.items():
        for href in parsed.links:
            target = target_for(page_path, href)
            if target is None:
                continue
            local_path, fragment = target
            if not local_path.is_relative_to(ROOT.resolve()) or not local_path.exists():
                errors.append(f"{page_path}: broken local link {href}")
            elif fragment and local_path in pages:
                target_page = pages[local_path]
                if fragment in {"home", "about", "projects", "blog"}:
                    if fragment not in target_page.views:
                        errors.append(f"{page_path}: missing SPA view {href}")
                elif fragment.startswith("project/"):
                    if fragment[8:] not in target_page.project_slugs:
                        errors.append(f"{page_path}: missing project route {href}")
                elif fragment.startswith("post/"):
                    if fragment[5:] not in target_page.post_slugs:
                        errors.append(f"{page_path}: missing post route {href}")
                elif fragment not in target_page.ids:
                    errors.append(f"{page_path}: missing anchor {href}")

    if errors:
        print("\n".join(errors))
        raise SystemExit(1)
    print(f"PASS: {len(pages)} pages, local assets, SPA routes, and anchors resolved")


if __name__ == "__main__":
    main()
