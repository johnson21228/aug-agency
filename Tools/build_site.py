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

# Essays are written to docs/writings/*.html -> need ../style.css
STYLE_ESSAY = "../style.css"
# Index is written to docs/index.html -> need style.css
STYLE_INDEX = "style.css"


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

{builders_section_html}
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
        idx = yaml.safe_load(f)
    if not isinstance(idx, dict):
        raise ValueError("writing/index.yaml must parse to a mapping (dict).")
    return idx


# -----------------------------
# IO helpers
# -----------------------------

def read_essay(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Essay not found: {path}")
    return path.read_text(encoding="utf-8")


def write_html(path: Path, html_text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_text, encoding="utf-8")


# -----------------------------
# Build site
# -----------------------------

def build_writings():
    idx = load_index()

    writings = idx.get("writings", [])
    if not isinstance(writings, list):
        raise ValueError("writing/index.yaml: 'writings' must be a list.")

    site_meta = idx.get("site", {}) if isinstance(idx.get("site", {}), dict) else {}

    site_title = site_meta.get("title") or "IAM — Writings"
    h1 = site_meta.get("h1") or "IAM — Writings"
    lede = site_meta.get("lede") or (
        "A small set of essays that motivate and constrain the IAM project: preserving and extending "
        "human reasoning continuity in an environment increasingly shaped by automated and agentic systems."
    )
    start_section_title = site_meta.get("start_section_title") or "Start here"
    builders_section_title = site_meta.get("builders_section_title") or "Start here — builders"
    all_section_title = site_meta.get("all_section_title") or "All writings"

    start_here_list = site_meta.get("start_here")
    builders_list = site_meta.get("start_here_builders")

    start_here_items = []
    builders_items = []
    all_items = []
    link_by_path = {}

    for item in writings:
        if not isinstance(item, dict) or "path" not in item or "title" not in item:
            raise ValueError("Each writings[] item must be a mapping with at least 'path' and 'title'.")

        src = ROOT / item["path"]
        slug = Path(item["path"]).stem
        title = str(item["title"])

        raw_md = read_essay(src)
        body_html = render_md(raw_md)

        notes_html = ""
        if item.get("notes"):
            notes_html = f"<p><em>{html.escape(str(item['notes']))}</em></p>"

        essay_html = ESSAY_TEMPLATE.format(
            title=html.escape(title),
            notes=notes_html,
            content=body_html,
            style=STYLE_ESSAY,
        )

        out_path = OUTPUT_DIR / "writings" / f"{slug}.html"
        write_html(out_path, essay_html)

        link_html = f"<p><a href='writings/{slug}.html'>{html.escape(title)}</a></p>"

        all_items.append(link_html)
        link_by_path[str(item["path"])] = link_html


    # Build Start Here section
    if isinstance(start_here_list, list):
        for ref in start_here_list:
            if isinstance(ref, dict) and "path" in ref:
                p = str(ref["path"])
                if p in link_by_path:
                    start_here_items.append(link_by_path[p])
            elif isinstance(ref, str) and ref in link_by_path:
                start_here_items.append(link_by_path[ref])
    else:
        # Backward compatible: use writings[].start_here flag
        for item in writings:
            if isinstance(item, dict) and item.get("start_here"):
                p = str(item["path"])
                if p in link_by_path:
                    start_here_items.append(link_by_path[p])

    # Build Builders Start Here section
    if isinstance(builders_list, list):
        for ref in builders_list:
            if isinstance(ref, dict) and "path" in ref:
                p = str(ref["path"])
                if p in link_by_path:
                    builders_items.append(link_by_path[p])
            elif isinstance(ref, str) and ref in link_by_path:
                builders_items.append(link_by_path[ref])

    builders_section_html = ""
    if builders_items:
        builders_section_html = (
            f"<h2>{html.escape(builders_section_title)}</h2>\n" + "\n".join(builders_items) + "\n"
        )

    index_html = INDEX_TEMPLATE.format(
        title=html.escape(site_title),
        h1=html.escape(h1),
        lede=html.escape(lede),
        start_section_title=html.escape(start_section_title),
        all_section_title=html.escape(all_section_title),
        start_here_items="\n".join(start_here_items),
        builders_section_html=builders_section_html,
        all_items="\n".join(all_items),
        style=STYLE_INDEX,
    )

    write_html(OUTPUT_DIR / "index.html", index_html)


if __name__ == "__main__":
    build_writings()
