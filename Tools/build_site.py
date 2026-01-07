#!/usr/bin/env python3
"""
Build a minimal static site for IAM writings from Markdown.

Inputs (authoritative):
- writing/index.yaml   (navigation + ordering + titles)
- writing/*.md         (essay content)

Outputs:
- site/index.html
- site/style.css
- site/writings/*.html

Design goals:
- Deterministic output (no timestamps)
- Simple templates
- No JS, no frameworks
"""

from __future__ import annotations

import argparse
import html
import os
from pathlib import Path

import yaml  # pip install pyyaml
import markdown  # pip install markdown


STYLE_CSS = """\
:root { color-scheme: light dark; }
body {
  margin: 0;
  font: 16px/1.65 system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
}
.wrap { max-width: 820px; margin: 0 auto; padding: 28px; }
h1 { font-size: 28px; margin: 0 0 8px; }
.lede { margin: 0; opacity: 0.88; }
h2 { margin-top: 28px; font-size: 18px; }
a { text-decoration: none; }
a:hover { text-decoration: underline; }
.note { font-size: 14px; opacity: 0.8; margin: 4px 0 12px; }
ol, ul { padding-left: 20px; }
hr { border: 0; border-top: 1px solid rgba(127,127,127,0.25); margin: 22px 0; }
code { font-size: 0.95em; }
.small { font-size: 14px; opacity: 0.8; }
"""

INDEX_TEMPLATE = """\
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{title}</title>
  <link rel="stylesheet" href="./style.css" />
</head>
<body>
  <header class="wrap">
	<h1>{h1}</h1>
	<p class="lede">{lede}</p>
  </header>

  <main class="wrap">
	<section>
	  <h2>Start here</h2>
	  <ol>
		{start_here_items}
	  </ol>
	</section>

	<section>
	  <h2>All writings</h2>
	  <ul>
		{all_items}
	  </ul>
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

WRITING_TEMPLATE = """\
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{page_title}</title>
  <link rel="stylesheet" href="../style.css" />
</head>
<body>
  <header class="wrap">
	<p><a href="../index.html">← Back</a></p>
	<h1>{h1}</h1>
	<p class="small">{meta}</p>
  </header>

  <main class="wrap">
	<article>
	  {content_html}
	</article>
  </main>
</body>
</html>
"""


def slug_from_md_path(md_path: str) -> str:
	# writing/foo-bar.md -> foo-bar.html
	base = Path(md_path).name
	if base.lower().endswith(".md"):
		base = base[:-3]
	return f"{base}.html"


def load_index_yaml(index_path: Path) -> dict:
	data = yaml.safe_load(index_path.read_text(encoding="utf-8"))
	if not isinstance(data, dict):
		raise ValueError("index.yaml must parse to a mapping/object.")
	return data


def md_to_html(md_text: str) -> str:
	# Keep it minimal and predictable.
	md = markdown.Markdown(
		extensions=[
			"extra",        # tables, fenced_code, etc.
			"sane_lists",
			"toc",          # optional; doesn't show unless you include [TOC]
		],
		output_format="html5",
	)
	return md.convert(md_text)


def build_site(repo_root: Path, out_dir: Path, site_title: str) -> None:
	index_yaml_path = repo_root / "writing" / "index.yaml"
	if not index_yaml_path.exists():
		raise FileNotFoundError(f"Missing {index_yaml_path}")

	idx = load_index_yaml(index_yaml_path)

	writings = idx.get("writings", [])
	drafts = idx.get("drafts", [])

	if not isinstance(writings, list):
		raise ValueError("index.yaml: 'writings' must be a list")
	if drafts is not None and not isinstance(drafts, list):
		raise ValueError("index.yaml: 'drafts' must be a list if present")

	out_dir.mkdir(parents=True, exist_ok=True)
	(out_dir / "writings").mkdir(parents=True, exist_ok=True)

	# Write CSS
	(out_dir / "style.css").write_text(STYLE_CSS, encoding="utf-8")

	def normalize_entry(e: dict) -> dict:
		# Required: id, path, title, status, authoritative, created
		if not isinstance(e, dict):
			raise ValueError("Each writing entry must be an object/map.")
		for k in ("id", "path", "title", "status", "authoritative", "created"):
			if k not in e:
				raise ValueError(f"Missing required field '{k}' in entry: {e}")
		return e

	writings_n = [normalize_entry(e) for e in writings]
	drafts_n = [normalize_entry(e) for e in drafts] if drafts else []

	# Helper: build HTML page for each writing
	def render_entry_page(entry: dict, is_draft: bool) -> str:
		md_path = repo_root / entry["path"]
		if not md_path.exists():
			raise FileNotFoundError(f"Missing writing file: {entry['path']}")

		md_text = md_path.read_text(encoding="utf-8")
		content_html = md_to_html(md_text)

		meta_bits = [
			f"ID: {entry['id']}",
			f"Status: {entry['status']}",
			"Draft" if is_draft else "Authoritative" if entry.get("authoritative") else "Non-authoritative",
			f"Created: {entry['created']}",
		]
		meta = " · ".join(html.escape(x) for x in meta_bits)

		return WRITING_TEMPLATE.format(
			page_title=html.escape(entry["title"]),
			h1=html.escape(entry["title"]),
			meta=meta,
			content_html=content_html,
		)

	# Write pages
	all_entries = []
	for entry in writings_n:
		html_name = slug_from_md_path(entry["path"])
		page_path = out_dir / "writings" / html_name
		page_path.write_text(render_entry_page(entry, is_draft=False), encoding="utf-8")
		all_entries.append((entry, html_name, False))

	for entry in drafts_n:
		html_name = slug_from_md_path(entry["path"])
		page_path = out_dir / "writings" / html_name
		page_path.write_text(render_entry_page(entry, is_draft=True), encoding="utf-8")
		all_entries.append((entry, html_name, True))

	# Build landing page lists

	# "Start here" = explicitly curated entries (Index.yaml: start_here: true)
	start_here = [x for x in all_entries if (x[2] is False and x[0].get("start_here") is True)]
	if not start_here:
		# Fallback for older indexes: first 3 authoritative writings, in the order listed
		start_here = [x for x in all_entries if x[2] is False][:3]


	def li_link(entry: dict, html_name: str, note: str | None = None) -> str:
		title = html.escape(entry["title"])
		href = f'./writings/{html.escape(html_name)}'
		if note:
			return f'<li><a href="{href}">{title}</a><div class="note">{html.escape(note)}</div></li>'
		return f'<li><a href="{href}">{title}</a></li>'

	# Optional notes: use entry["notes"] if present in YAML
	start_here_items = "\n        ".join(
		li_link(e, html_name, (e.get("notes") or "").strip() or None)
		for (e, html_name, _is_draft) in start_here
	)

	all_items = "\n        ".join(
		li_link(e, html_name)
		for (e, html_name, _is_draft) in all_entries
	)

	index_html = INDEX_TEMPLATE.format(
		title=html.escape(site_title),
		h1="IAM — Writings",
		lede=(
			"A small set of essays that motivate and constrain the IAM project: preserving and extending "
			"human reasoning continuity in an environment increasingly shaped by automated and agentic systems."
		),
		start_here_items=start_here_items,
		all_items=all_items,
	)

	(out_dir / "index.html").write_text(index_html, encoding="utf-8")


def main() -> None:
	ap = argparse.ArgumentParser()
	ap.add_argument("--repo-root", default=".", help="Path to repo root (default: .)")
	ap.add_argument("--out", default="site", help="Output directory (default: site)")
	ap.add_argument("--title", default="IAM — Writings", help="Site title (default: IAM — Writings)")
	args = ap.parse_args()

	repo_root = Path(args.repo_root).resolve()
	out_dir = Path(args.out).resolve()

	build_site(repo_root=repo_root, out_dir=out_dir, site_title=args.title)
	print(f"Wrote static site to: {out_dir}")


if __name__ == "__main__":
	main()
