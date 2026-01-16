#!/usr/bin/env python3
"""
Static site builder (Derived-executed)

This builder treats Derived/site/site_manifest.json as the executable source
for homepage reading paths (Start here / Start here — builders), including
section purposes.

It builds the "All writings" catalog by scanning writing/essays/*.md directly
(no YAML required), to avoid configuration fragility.

Outputs:
- docs/index.html
- docs/writings/*.html
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple


# -----------------------------
# Paths
# -----------------------------

ROOT = Path(__file__).resolve().parent.parent
WRITING_DIR = ROOT / "writing"
ESSAYS_DIR = WRITING_DIR / "essays"
OUTPUT_DIR = ROOT / "docs"

MANIFEST_PATH = ROOT / "Derived" / "site" / "site_manifest.json"

# Essays are written to docs/writings/*.html -> need ../style.css
STYLE_ESSAY = "../style.css"
# Index is written to docs/index.html -> need style.css
STYLE_INDEX = "style.css"


# -----------------------------
# Templates
# -----------------------------

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
      <h2>{all_section_title}</h2>
      {all_items_html}
    </section>

    <hr />

    <section>
      <h2>Repository</h2>
      <p class="small">
        The writings are upstream of architecture and code. For authority boundaries, see <code>MAP.md</code>.
      </p>
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
    <h1>{title}</h1>
    {content}
  </main>
</body>
</html>
"""


# -----------------------------
# Markdown rendering
# -----------------------------

def render_md(md_text: str) -> str:
    """
    Convert Markdown to HTML using markdown2 or markdown if available.
    """
    try:
        import markdown2  # type: ignore
        return markdown2.markdown(md_text, extras=["fenced-code-blocks", "tables"])
    except Exception:
        try:
            import markdown  # type: ignore
            return markdown.markdown(md_text, extensions=["fenced_code", "tables"])
        except Exception:
            # Minimal fallback: escape and wrap in <pre>
            return "<pre>" + html.escape(md_text) + "</pre>"


def extract_title(md_text: str, fallback: str) -> str:
    """
    Title = first Markdown H1 '# ...' line, else fallback.
    """
    for line in md_text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


# -----------------------------
# IO helpers
# -----------------------------

def write_html(path: Path, html_text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_text, encoding="utf-8")


def load_manifest() -> Dict[str, Any]:
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(
            f"Missing Derived manifest: {MANIFEST_PATH}\n"
            "Run: python3 Tools/compile_site_manifest.py"
        )
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def scan_essays() -> List[Tuple[Path, str, str]]:
    """
    Returns list of (absolute_path, rel_path_str, title)
    for all essays under writing/essays/*.md (recursive).
    """
    if not ESSAYS_DIR.exists():
        raise FileNotFoundError(f"Missing essays dir: {ESSAYS_DIR}")

    essays: List[Tuple[Path, str, str]] = []
    for p in sorted(ESSAYS_DIR.rglob("*.md")):
        if p.name.startswith("._"):
            continue
        rel = p.relative_to(ROOT).as_posix()
        md_text = p.read_text(encoding="utf-8")
        title = extract_title(md_text, fallback=p.stem)
        essays.append((p, rel, title))
    return essays


def essay_slug_from_relpath(rel_path: str) -> str:
    """
    Keep compatibility with prior behavior: use filename stem.
    (Spaces may appear; browsers will URL-encode.)
    """
    return Path(rel_path).stem


def build_link_map(essays: List[Tuple[Path, str, str]]) -> Dict[str, Dict[str, str]]:
    """
    Map from repo-relative path -> {slug, title, href}
    """
    m: Dict[str, Dict[str, str]] = {}
    for _abs, rel, title in essays:
        slug = essay_slug_from_relpath(rel)
        href = f"./writings/{slug}.html"
        m[rel] = {"slug": slug, "title": title, "href": href}
    return m


# -----------------------------
# Build
# -----------------------------

def render_sections_html(manifest: Dict[str, Any], link_map: Dict[str, Dict[str, str]]) -> str:
    sections = manifest.get("sections", [])
    if not isinstance(sections, list):
        sections = []

    out: List[str] = []
    for sec in sections:
        if not isinstance(sec, dict):
            continue

        label = str(sec.get("label") or "")
        purpose = str(sec.get("purpose") or "").strip()
        items = sec.get("items", [])
        if not label or not isinstance(items, list) or not items:
            continue

        out.append("<section>")
        out.append(f"  <h2>{html.escape(label)}</h2>")
        if purpose:
            out.append(f"  <p><em>{html.escape(purpose)}</em></p>")
        out.append("  <ol>")

        for it in items:
            if not isinstance(it, dict):
                continue
            path = str(it.get("path") or "")
            title = str(it.get("title") or "").strip()

            if not path:
                continue

            # Only writings/essays/* are linkable in this builder
            # (If you later want architecture/*, add a second builder pipeline.)
            if path not in link_map:
                # Try to normalize to repo-relative path if given as absolute-ish
                # For safety, skip if not found.
                continue

            href = link_map[path]["href"]
            display_title = title or link_map[path]["title"]
            out.append(
                f"    <li><a href='{html.escape(href)}'>{html.escape(display_title)}</a></li>"
            )

        out.append("  </ol>")
        out.append("</section>")

    return "\n".join(out)


def build_all_writings_html(essays: List[Tuple[Path, str, str]], link_map: Dict[str, Dict[str, str]]) -> str:
    # Simple alphabetical list by title (stable, non-recency)
    items = sorted([(title, rel) for _abs, rel, title in essays], key=lambda x: x[0].lower())
    out: List[str] = ["<ul>"]
    for title, rel in items:
        href = link_map[rel]["href"]
        out.append(f"  <li><a href='{html.escape(href)}'>{html.escape(title)}</a></li>")
    out.append("</ul>")
    return "\n".join(out)


def build_essay_pages(essays: List[Tuple[Path, str, str]]) -> None:
    for abs_path, rel, title in essays:
        md_text = abs_path.read_text(encoding="utf-8")
        body_html = render_md(md_text)

        html_text = ESSAY_TEMPLATE.format(
            title=html.escape(title),
            content=body_html,
            style=STYLE_ESSAY,
        )

        slug = essay_slug_from_relpath(rel)
        out_path = OUTPUT_DIR / "writings" / f"{slug}.html"
        write_html(out_path, html_text)


def build_site() -> None:
    manifest = load_manifest()
    essays = scan_essays()
    link_map = build_link_map(essays)

    # Build essay pages first
    build_essay_pages(essays)

    site = manifest.get("site", {}) if isinstance(manifest.get("site", {}), dict) else {}
    site_title = str(site.get("title") or "IAM — Writings")
    h1 = str(site.get("h1") or site_title)
    lede = str(site.get("lede") or "").strip()

    sections_html = render_sections_html(manifest, link_map)
    all_items_html = build_all_writings_html(essays, link_map)

    index_html = INDEX_TEMPLATE.format(
        title=html.escape(site_title),
        h1=html.escape(h1),
        lede=html.escape(lede),
        sections_html=sections_html,
        all_section_title="All writings",
        all_items_html=all_items_html,
        style=STYLE_INDEX,
    )

    write_html(OUTPUT_DIR / "index.html", index_html)


if __name__ == "__main__":
    build_site()
