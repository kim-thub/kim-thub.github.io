#!/usr/bin/env python3
"""Bundle Markdown posts into the single Paper Collage Archive page."""
from pathlib import Path
from urllib.parse import urlsplit
from html import escape
import json
import re
import posixpath
from pygments import highlight as pygments_highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

ROOT = Path(__file__).resolve().parents[1]
HTML_FILE = ROOT / "index.html"
POSTS_DIR = ROOT / "content" / "posts"
DATA_PATTERN = re.compile(
    r'<script id="blog-posts-data" type="application/json">.*?</script>',
    re.DOTALL,
)
CODE_FENCE_PATTERN = re.compile(r"(?m)^\s*```([\w+-]*)\s*\n(.*?)^\s*```\s*(?=\n|$)", re.DOTALL)
CODE_FORMATTER = HtmlFormatter(nowrap=True, classprefix="tok-")


def highlighted_code_blocks(markdown: str):
    """Reuse the existing tok-* CSS classes for every fenced code block."""
    blocks = []
    for match in CODE_FENCE_PATTERN.finditer(markdown.replace("\r", "")):
        language = match.group(1).lower()
        code = match.group(2)
        try:
            lexer = get_lexer_by_name(language, stripnl=False, ensurenl=False) if language else None
        except ClassNotFound:
            lexer = None
        markup = pygments_highlight(code, lexer, CODE_FORMATTER) if lexer else escape(code, quote=False)
        blocks.append({"language": language or "text", "html": markup})
    return blocks


def parse_frontmatter(text: str):
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("front matter 시작 `---` 뒤에 닫는 `---`가 없습니다.")
    metadata = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, value = line.partition(":")
        if not separator:
            raise ValueError(f"잘못된 front matter 줄: {line}")
        metadata[key.strip().lower()] = value.strip().strip('"').strip("'")
    return metadata, text[end + 5 :].lstrip("\n")


def make_slug(value: str):
    value = value.lower().strip()
    value = re.sub(r"[^\w-]+", "-", value, flags=re.UNICODE)
    value = re.sub(r"-+", "-", value).strip("-")
    return value


def plain_excerpt(markdown: str):
    for line in markdown.splitlines():
        value = line.strip()
        if not value or value.startswith("#") or value.startswith("```") or value.startswith("|") or value.startswith(">"):
            continue
        value = re.sub(r"!?(\[([^\]]*)\])\([^)]*\)", r"\2", value)
        value = re.sub(r"[`*_~]", "", value)
        value = re.sub(r"\s+", " ", value).strip()
        if value:
            return value[:190] + ("…" if len(value) > 190 else "")
    return "Markdown으로 작성한 기술 기록입니다."


def page_relative_links(markdown: str, source: Path):
    """Resolve local Markdown links from the post file to the HTML root."""
    rel_source = source.relative_to(ROOT).parent.as_posix()
    pattern = re.compile(r"(!?\[[^\]]*\]\()([^\s)]+)(\))")

    def rewrite(match):
        raw = match.group(2)
        parsed = urlsplit(raw)
        if parsed.scheme or raw.startswith(("#", "/")):
            return match.group(0)
        local = posixpath.normpath(posixpath.join(rel_source, parsed.path))
        suffix = ("?" + parsed.query if parsed.query else "") + ("#" + parsed.fragment if parsed.fragment else "")
        return match.group(1) + local + suffix + match.group(3)

    return pattern.sub(rewrite, markdown)


def post_entries():
    entries = []
    seen = set()
    for source in sorted(POSTS_DIR.glob("*.md")):
        if source.name.lower() == "readme.md":
            continue
        metadata, body = parse_frontmatter(source.read_text(encoding="utf-8"))
        title = metadata.get("title") or next((line[2:].strip() for line in body.splitlines() if line.startswith("# ")), source.stem)
        slug = make_slug(metadata.get("slug") or source.stem)
        if not slug:
            raise ValueError(f"slug를 만들 수 없습니다: {source.name}")
        if slug in seen:
            raise ValueError(f"중복 slug `{slug}`: {source.name}")
        seen.add(slug)
        excerpt = metadata.get("excerpt") or plain_excerpt(body)
        entries.append({
            "index_order": int(metadata.get("index_order", "999")),
            "slug": slug,
            "title": title,
            "excerpt": excerpt,
            "kind": "markdown",
            "markdown": page_relative_links(body, source),
            "codeBlocks": highlighted_code_blocks(body),
        })
    entries.sort(key=lambda entry: entry.get("index_order", 999))
    order_values = [entry.get("index_order", 999) for entry in entries]
    if len(order_values) != len(set(order_values)):
        raise ValueError("블로그 index_order 값이 중복되었습니다.")
    for entry in entries:
        entry.pop("index_order", None)
    return entries


def main():
    entries = post_entries()
    payload = json.dumps(entries, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("<", "\\u003c").replace("&", "\\u0026")
    block = f'<script id="blog-posts-data" type="application/json">{payload}</script>'
    if not HTML_FILE.exists():
        raise FileNotFoundError(HTML_FILE)
    original = HTML_FILE.read_text(encoding="utf-8")
    updated, count = DATA_PATTERN.subn(lambda _: block, original, count=1)
    if count != 1:
        raise RuntimeError(f"블로그 데이터 영역을 찾지 못했습니다: {HTML_FILE.name}")
    HTML_FILE.write_text(updated, encoding="utf-8")
    print(f"블로그 {len(entries)}개를 {HTML_FILE.name}에 반영했습니다.")


if __name__ == "__main__":
    main()
