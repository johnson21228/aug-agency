#!/usr/bin/env python3
"""
Static site builder (Derived-executed)

This builder executes Site Language Infrastructure (LI) via
Derived/site/site_manifest.json.

Authority rules:
- LI/site/* defines intent
- Derived/site/* is executable, regenerable
- writing/essays/*.md are authoritative content
- Tools must not re-author meaning
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


# -------------------------------------------------
# Paths
# -------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
ESSAYS_DIR = ROOT / "writing" / "essays"
OUTPUT_DIR = ROOT / "docs"

MANIFEST_PATH = ROOT / "Derived" / "site" / "site_manifest.json"

STYLE_INDEX = "style.css"
STYLE_ESSAY = "../style.css"


# -------------------------------------------------
# Templates
# -------------------------------------------------

INDEX_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{title}</title>
  <link rel="stylesheet" href="./{style}" />
</head>
<body>
  <header class="wrap">
    <h1>{h1}</h1>
    <p class="lede">{lede}</p>
  </header>

  <main class="wrap">
    {sections_html}

    <section>
      <h2>All writings</h2>
      {all_items_html}
    </section>
  </main>
</body>
</html>
"""


ESSAY_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{title}</title>
  <link rel="stylesheet" href="{style}" />
</head>
<body>
  <main class="wrap">
    {content}
  </main>
</body>
</html>
"""


# -------------------------------------------------
# Markdown rendering
# -------------------------------------------------

def render_md(md_text: str) -> str:
    try:
        import markdown2  # type: ignore
        return markdown2.markdown(md_text, extras=["fenced-code-blocks", "tables"])
    except Exception:
        try:
            import markdown  # type: ignore
            return markdown.markdown(md_text, extensions=["fenced_code", "tables"])
        except Exception:
            return "<pre>" + html.escape(md_text) + "</pre>"


def extract_title(md_text: str, fallback: str) -> str:
    for line in md_text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


# -------------------------------------------------
# IO helpers
# -------------------------------------------------

def write_html(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_manifest() -> Dict[str, Any]:
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(
            f"Missing Derived manifest: {MANIFEST_PATH}\n"
            "Run: python3 Tools/compile_site_manifest.py"
        )
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


# -------------------------------------------------
# Build helpers
# -------------------------------------------------

def scan_essays() -> List[Tuple[Path, str, str]]:
    essays: List[Tuple[Path, str, str]] = []
    for p in sorted(ESSAYS_DIR.rglob("*.md")):
        if p.name.startswith("._"):
            continue
        rel = p.relative_to(ROOT).as_posix()
        text = p.read_text(encoding="utf-8")
        title = extract_title(text, p.stem)
        essays.append((p, rel, title))
    return essays


def essay_slug(rel_path: str) -> str:
    return Path(rel_path).stem


def build_link_map(
    essays: List[Tuple[Path, str, str]]
) -> Dict[str, Dict[str, str]]:
    m: Dict[str, Dict[str, str]] = {}
    for _abs, rel, title in essays:
        m[rel] = {
            "slug": essay_slug(rel),
            "title": title,
            "href": f"./writings/{essay_slug(rel)}.html",
        }
    return m


# -------------------------------------------------
# Rendering
# -------------------------------------------------

def render_sections(manifest: Dict[str, Any], link_map: Dict[str, Dict[str, str]]) -> str:
    out: List[str] = []

    for section in manifest.get("sections", []):
        label = section.get("label")
        purpose = (section.get("purpose") or "").strip()
        items = section.get("items", [])

        if not label or not items:
            continue

        out.append("<section>")
        out.append(f"<h2>{html.escape(label)}</h2>")
        if purpose:
            out.append(f"<p><em>{html.escape(purpose)}</em></p>")
        out.append("<ol>")

        for item in items:
            path = item.get("path")
            title = item.get("title") or ""
            if path not in link_map:
                continue
            href = link_map[path]["href"]
            out.append(
                f"<li><a href='{html.escape(href)}'>{html.escape(title)}</a></li>"
            )

        out.append("</ol>")
        out.append("</section>")

    return "\n".join(out)


def render_all_writings(essays, link_map) -> str:
    out = ["<ul>"]
    for _, rel, title in sorted(essays, key=lambda x: x[2].lower()):
        out.append(
            f"<li><a href='{html.escape(link_map[rel]['href'])}'>{html.escape(title)}</a></li>"
        )
    out.append("</ul>")
    return "\n".join(out)


def build_essay_pages(essays):
    for abs_path, rel, title in essays:
        md = abs_path.read_text(encoding="utf-8")
        html_body = render_md(md)
        html_page = ESSAY_TEMPLATE.format(
            title=html.escape(title),
            content=html_body,
            style=STYLE_ESSAY,
        )
        write_html(OUTPUT_DIR / "writings" / f"{essay_slug(rel)}.html", html_page)


# -------------------------------------------------
# Entry point
# -------------------------------------------------

def build_site() -> None:
    manifest = load_manifest()
    essays = scan_essays()
    link_map = build_link_map(essays)

    build_essay_pages(essays)

    site = manifest.get("site", {})
    title = site.get("title", "IAM - Writings")
    h1 = site.get("h1", title)
    lede = (site.get("lede") or "").strip()

    index_html = INDEX_TEMPLATE.format(
        title=html.escape(title),
        h1=html.escape(h1),
        lede=html.escape(lede),
        sections_html=render_sections(manifest, link_map),
        all_items_html=render_all_writings(essays, link_map),
        style=STYLE_INDEX,
    )

    write_html(OUTPUT_DIR / "index.html", index_html)


if __name__ == "__main__":
    build_site()
