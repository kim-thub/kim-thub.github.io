"""Check local Pages routes and same-page anchors before publishing."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1] / "site"


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids: set[str] = set()
        self.duplicates: set[str] = set()
        self.links: list[str] = []
        self.headings = 0
        self.detail_pages = 0
        self.title = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        element_id = attributes.get("id")
        if element_id:
            if element_id in self.ids:
                self.duplicates.add(element_id)
            self.ids.add(element_id)
        if tag == "h1":
            self.headings += 1
        if tag == "article" and "detail-page" in attributes.get("class", "").split():
            self.detail_pages += 1
        if tag == "title":
            self.title = True
        if tag in {"a", "link"} and attributes.get("href"):
            self.links.append(attributes["href"])


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
        parsed.feed(page_path.read_text(encoding="utf-8"))
        pages[page_path.resolve()] = parsed
        expected_headings = 1 + parsed.detail_pages if page_path == ROOT / "index.html" else 1
        if parsed.headings != expected_headings or not parsed.title:
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
            elif fragment.startswith("p/"):
                route_parts = fragment.split("/")
                if len(route_parts) not in {2, 3} or local_path not in pages:
                    errors.append(f"{page_path}: invalid SPA route {href}")
                else:
                    expected_id = "page-" + route_parts[1] if len(route_parts) == 2 else route_parts[1] + "-" + route_parts[2]
                    if expected_id not in pages[local_path].ids:
                        errors.append(f"{page_path}: missing SPA route target {href}")
            elif fragment and local_path.suffix == ".html" and fragment not in pages[local_path].ids:
                errors.append(f"{page_path}: missing anchor {href}")

    if errors:
        print("\n".join(errors))
        raise SystemExit(1)
    print(f"PASS: {len(pages)} pages, all local links and anchors resolved")


if __name__ == "__main__":
    main()
