import os
import html
import yaml
from pathlib import Path

# -----------------------------
# Paths
# -----------------------------

ROOT = Path(__file__).resolve().parent.parent
WRITING_DIR = ROOT / "writing"
ESSAYS_DIR = WRITING_DIR / "essays"
OUTPUT_DIR = ROOT / "docs"
STYLE_PATH = "../style.css"


# -----------------------------
# Markdown rendering (robust)
# -----------------------------

def load_markdown_renderer():
    try:
        import markdown
        return lambda text: markdown.markdown(text, extensions=["fenced_code"])
    except ImportError:
        try:
            import markdown2
            return lambda text: markdown2.markdown(text)
        except ImportError:
            try:
                import mistune
                return lambda text: mistune.html(text)
            except ImportError:
                return lambda text: "<pre>" + html.escape(text) + "</pre>"

render_md = load_markdown_renderer()


# -----------------------------
# Templates
# -----------------------------

INDEX_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title}</title>
<link rel="stylesheet" href="{style}">
</head>
<body>

<h1>{h1}</h1>
<p>{lede}</p>

<h2>{start_section_title}</h2>
{start_here_items}

<h2>{all_section_title}</h2>
{all_items}

</body>
</html>
"""

ESSAY_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title}</title>
<link rel="stylesheet" href="{style}">
</head>
<body>

<h1>{title}</h1>
{notes}
{content}

</body>
</html>
"""


# -----------------------------
# Load index.yaml
# -----------------------------

def load_index():
    index_path = WRITING_DIR / "index.yaml"
    if not index_path.exists():
        raise FileNotFoundError("Missing writing/index.yaml")
    with open(index_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# -----------------------------
# Essay helpers
# -----------------------------

def read_essay(path):
    if not path.exists():
        raise FileNotFoundError(f"Essay not found: {path}")
    return path.read_text(encoding="utf-8")


def write_html(path, html_text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_text, encoding="utf-8")


# -----------------------------
# Build site
# -----------------------------

def build_writings():
    idx = load_index()

    writings = idx.get("writings", [])
    site_title = idx.get("site", {}).get("title", "IAM — Writings")

    # -----------------------------
    # SITE METADATA (THIS IS WHERE YOUR BLOCK GOES)
    # -----------------------------

    site_meta = idx.get("site", {}) if isinstance(idx.get("site", {}), dict) else {}

    start_section_title = site_meta.get("start_section_title") or "Start here"
    all_section_title = site_meta.get("all_section_title") or "All writings"

    h1 = site_meta.get("h1") or "IAM — Writings"
    lede = site_meta.get("lede") or (
        "A small set of essays that motivate and constrain the IAM project: preserving and extending "
        "human reasoning continuity in an environment increasingly shaped by automated and agentic systems."
    )

    # -----------------------------
    # Render essays
    # -----------------------------

    start_here_items = []
    all_items = []

    for item in writings:
        path = ROOT / item["path"]
        slug = Path(item["path"]).stem
        title = item["title"]

        raw_md = read_essay(path)
        body_html = render_md(raw_md)

        notes_html = ""
        if item.get("notes"):
            notes_html = f"<p><em>{html.escape(item['notes'])}</em></p>"

        essay_html = ESSAY_TEMPLATE.format(
            title=html.escape(title),
            notes=notes_html,
            content=body_html,
            style=STYLE_PATH,
        )

        output_path = OUTPUT_DIR / "writings" / f"{slug}.html"
        write_html(output_path, essay_html)

        link_html = f"<p><a href='writings/{slug}.html'>{html.escape(title)}</a></p>"

        all_items.append(link_html)
        if item.get("start_here"):
            start_here_items.append(link_html)

    # -----------------------------
    # Render index page
    # -----------------------------

    index_html = INDEX_TEMPLATE.format(
        title=html.escape(site_title),
        h1=html.escape(h1),
        lede=html.escape(lede),
        start_section_title=html.escape(start_section_title),
        all_section_title=html.escape(all_section_title),
        start_here_items="\n".join(start_here_items),
        all_items="\n".join(all_items),
        style=STYLE_PATH,
    )

    write_html(OUTPUT_DIR / "index.html", index_html)


# -----------------------------
# Entrypoint
# -----------------------------

if __name__ == "__main__":
    build_writings()
