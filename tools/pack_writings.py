#!/usr/bin/env python3
"""
tools/pack_writings.py

Creates a zip bundle of the current writings:
- By default, packs English writings only (paths without locale suffixes like .es.md)
- writing/index.yaml (canonical)
- writing/INDEX.md (human map, if present)
- all essay markdown files referenced by writing/index.yaml
- optionally: generated PDFs for each essay (basic formatting)

Usage:
  python tools/pack_writings.py --out dist/pack-writings.zip --pdf
  python tools/pack_writings.py --out dist/pack-writings-src.zip --no-pdf

English-only is the default. To include non-English writings (e.g. *.es.md, *.de-CH.md):
  python tools/pack_writings.py --out dist/pack-writings.zip --all-languages --pdf
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import re
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Tuple

import yaml

ROOT = Path(__file__).resolve().parent.parent
WRITING_DIR = ROOT / "writing"
INDEX_YAML = WRITING_DIR / "index.yaml"
INDEX_MD = WRITING_DIR / "INDEX.md"

_LOCALE_SUFFIX_RE = re.compile(r"\.[a-z]{2}(?:-[A-Za-z]{2})?\.md$")


def _is_english_path(path: str) -> bool:
    """Return True if the markdown path appears to be an English essay.

    Convention: non-English essays have a locale suffix before .md, e.g.
      foo.es.md, foo.de-CH.md
    English essays are plain .md without a locale suffix.

    This function is intentionally filename-based to avoid adding per-file metadata.
    """
    path = path.strip()
    return not bool(_LOCALE_SUFFIX_RE.search(path))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_index_yaml() -> Dict:
    if not INDEX_YAML.exists():
        raise FileNotFoundError(f"Missing {INDEX_YAML}")
    with open(INDEX_YAML, "r", encoding="utf-8") as f:
        idx = yaml.safe_load(f)
    if not isinstance(idx, dict):
        raise ValueError(f"{INDEX_YAML} must parse as a YAML mapping/dict.")
    return idx


def _parse_md_simple(md: str) -> List[Tuple[str, str]]:
    """
    Very small markdown parser for basic PDF formatting.

    Returns list of (kind, text) where kind in {"h1","h2","h3","p","code"}.
    """
    lines = md.splitlines()
    out: List[Tuple[str, str]] = []
    in_code = False
    code_buf: List[str] = []

    for raw in lines:
        line = raw.rstrip("\n")

        if line.strip().startswith("```"):
            if in_code:
                out.append(("code", "\n".join(code_buf).rstrip()))
                code_buf = []
                in_code = False
            else:
                in_code = True
            continue

        if in_code:
            code_buf.append(line)
            continue

        if line.startswith("# "):
            out.append(("h1", line[2:].strip()))
        elif line.startswith("## "):
            out.append(("h2", line[3:].strip()))
        elif line.startswith("### "):
            out.append(("h3", line[4:].strip()))
        else:
            # keep blank lines as paragraph separators
            out.append(("p", line))

    if in_code and code_buf:
        out.append(("code", "\n".join(code_buf).rstrip()))

    return out


def _write_pdf_basic(md_path: Path, pdf_path: Path) -> None:
    """
    Write a simple PDF from markdown using ReportLab.

    If reportlab isn't installed, raises a helpful error.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except Exception as e:
        raise RuntimeError(
            "reportlab is required for PDF output.\n"
            "Install into your venv: pip install reportlab\n"
        ) from e

    text = _read_text(md_path)
    blocks = _parse_md_simple(text)

    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter

    margin = 54  # 0.75 inch
    x = margin
    y = height - margin

    def new_page():
        nonlocal y
        c.showPage()
        y = height - margin

    def draw_wrapped(s: str, font_name: str, font_size: int, leading: int):
        nonlocal y
        c.setFont(font_name, font_size)
        max_w = width - 2 * margin

        # naive wrapping by words
        words = s.split()
        if not words:
            y -= leading
            return

        line = words[0]
        for w in words[1:]:
            test = f"{line} {w}"
            if c.stringWidth(test, font_name, font_size) <= max_w:
                line = test
            else:
                c.drawString(x, y, line)
                y -= leading
                if y < margin:
                    new_page()
                line = w
        c.drawString(x, y, line)
        y -= leading

    for kind, raw in blocks:
        txt = html.unescape(raw.rstrip())

        if kind == "h1":
            if txt:
                c.setFont("Helvetica-Bold", 18)
                c.drawString(x, y, txt)
                y -= 26
            else:
                y -= 10
        elif kind == "h2":
            if txt:
                c.setFont("Helvetica-Bold", 14)
                c.drawString(x, y, txt)
                y -= 20
            else:
                y -= 10
        elif kind == "h3":
            if txt:
                c.setFont("Helvetica-Bold", 12)
                c.drawString(x, y, txt)
                y -= 16
            else:
                y -= 10
        elif kind == "code":
            if txt:
                # light box with monospace
                c.setFont("Courier", 9)
                for code_line in txt.splitlines():
                    c.drawString(x, y, code_line[:120])
                    y -= 11
                    if y < margin:
                        new_page()
                y -= 6
            else:
                y -= 10
        else:
            # paragraph
            if txt == "":
                y -= 10
                if y < margin:
                    new_page()
            else:
                draw_wrapped(txt, "Helvetica", 11, 14)

        if y < margin:
            new_page()

    c.save()


def _collect_writings(idx: Dict, *, english_only: bool = True) -> List[Dict]:
    writings = idx.get("writings", [])
    if not isinstance(writings, list):
        raise ValueError("writing/index.yaml: 'writings' must be a list.")
    for item in writings:
        if not isinstance(item, dict) or "path" not in item or "title" not in item:
            raise ValueError("Each writings[] item must be a mapping with at least 'path' and 'title'.")
    if english_only:
        writings = [w for w in writings if _is_english_path(str(w.get("path", "")))]
    return writings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--all-languages",
        action="store_true",
        help="Include non-English writings (e.g. *.es.md, *.de-CH.md). Default is English-only.",
    )
    ap.add_argument("--out", required=True, help="Output zip path, e.g. dist/pack-writings.zip")
    ap.add_argument("--pdf", dest="pdf", action="store_true", help="Include generated PDFs")
    ap.add_argument("--no-pdf", dest="pdf", action="store_false", help="Do not include PDFs")
    ap.set_defaults(pdf=True)
    args = ap.parse_args()

    out_zip = Path(args.out)
    out_zip.parent.mkdir(parents=True, exist_ok=True)

    idx = _load_index_yaml()
    writings = _collect_writings(idx, english_only=(not args.all_languages))
    if args.all_languages:
        print(f"Packing {len(writings)} writings (all languages)")
    else:
        print(f"Packing {len(writings)} writings (English-only)")

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bundle_root = f"pack-writings-{stamp}"

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        pdf_dir = tmp / "pdfs"
        pdf_dir.mkdir(parents=True, exist_ok=True)

        to_add: List[Tuple[Path, str]] = []
        to_add.append((INDEX_YAML, f"{bundle_root}/writing/index.yaml"))
        if INDEX_MD.exists():
            to_add.append((INDEX_MD, f"{bundle_root}/writing/INDEX.md"))

        for item in writings:
            src = ROOT / item["path"]
            if not src.exists():
                raise FileNotFoundError(f"Index references missing file: {src}")
            arc = f"{bundle_root}/{item['path']}"
            to_add.append((src, arc))

        if args.pdf:
            for item in writings:
                md_path = ROOT / item["path"]
                # safe deterministic pdf filename
                pdf_name = (
                    Path(item["path"]).stem.replace(" ", "_").replace("*", "").replace('"', "").replace("'", "")
                    + ".pdf"
                )
                pdf_path = pdf_dir / pdf_name
                _write_pdf_basic(md_path, pdf_path)

                zip_pdf_path = f"{bundle_root}/writing/pdfs/{pdf_name}"
                to_add.append((pdf_path, zip_pdf_path))

        with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for src, arc in to_add:
                z.write(src, arc)

    print(f"Wrote: {out_zip}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
