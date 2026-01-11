#!/usr/bin/env python3
"""
Tools/pack_writings.py

Creates a zip bundle of the current writings:
- writing/index.yaml (canonical)
- writing/INDEX.md (human map, if present)
- all essay markdown files referenced by writing/index.yaml
- optionally: generated PDFs for each essay (basic formatting)

Usage:
  python Tools/pack_writings.py --out dist/pack-writings.zip --pdf
  python Tools/pack_writings.py --out dist/pack-writings-src.zip --no-pdf
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


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_index_yaml() -> Dict:
    if not INDEX_YAML.exists():
        raise FileNotFoundError(f"Missing {INDEX_YAML}")
    with open(INDEX_YAML, "r", encoding="utf-8") as f:
        idx = yaml.safe_load(f)
    if not isinstance(idx, dict):
        raise ValueError("writing/index.yaml must parse to a mapping (dict).")
    return idx


def _sanitize_filename(name: str) -> str:
    name = name.strip()
    name = re.sub(r"[^\w\-\.\s]", "", name)
    name = re.sub(r"\s+", " ", name)
    name = name.replace(" ", "_")
    return name or "untitled"


def _basic_md_to_blocks(md: str) -> List[Tuple[str, str]]:
    """
    Minimal markdown-to-blocks mapper for PDF output.
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

        s = line.strip()
        if not s:
            out.append(("p", ""))
            continue

        if s.startswith("# "):
            out.append(("h1", s[2:].strip()))
        elif s.startswith("## "):
            out.append(("h2", s[3:].strip()))
        elif s.startswith("### "):
            out.append(("h3", s[4:].strip()))
        else:
            t = s
            t = re.sub(r"\*\*(.*?)\*\*", r"\1", t)
            t = re.sub(r"\*(.*?)\*", r"\1", t)
            t = re.sub(r"`(.*?)`", r"\1", t)
            out.append(("p", t))

    if in_code and code_buf:
        out.append(("code", "\n".join(code_buf).rstrip()))

    return out


def _write_pdf_basic(out_pdf: Path, title: str, md_text: str) -> None:
    """
    Generates a basic PDF using reportlab.
    Deterministic, minimal formatting, no external binaries.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import inch
        from reportlab.pdfgen import canvas
    except Exception as e:
        raise RuntimeError(
            "PDF generation requires reportlab. Install with: pip install reportlab "
            "(or run: make venv-pdf)"
        ) from e

    page_w, page_h = letter
    margin = 0.75 * inch
    x = margin
    y = page_h - margin

    c = canvas.Canvas(str(out_pdf), pagesize=letter)

    def new_page():
        nonlocal y
        c.showPage()
        y = page_h - margin

    def draw_wrapped(text: str, font: str, size: int, leading: int):
        nonlocal y
        c.setFont(font, size)

        max_width = page_w - 2 * margin
        approx_chars = max(40, int(max_width / (size * 0.55)))

        paragraphs = text.split("\n")
        for p in paragraphs:
            if p.strip() == "":
                y -= leading
                if y < margin:
                    new_page()
                continue

            words = p.split(" ")
            line = ""
            for w in words:
                candidate = w if not line else (line + " " + w)
                if len(candidate) <= approx_chars:
                    line = candidate
                else:
                    if y < margin + leading:
                        new_page()
                    c.drawString(x, y, line)
                    y -= leading
                    line = w

            if line:
                if y < margin + leading:
                    new_page()
                c.drawString(x, y, line)
                y -= leading

    # Title
    draw_wrapped(title, "Helvetica-Bold", 18, 22)
    y -= 8

    blocks = _basic_md_to_blocks(md_text)
    for kind, text in blocks:
        if kind == "h1":
            y -= 10
            draw_wrapped(text, "Helvetica-Bold", 16, 20)
            y -= 4
        elif kind == "h2":
            y -= 8
            draw_wrapped(text, "Helvetica-Bold", 14, 18)
            y -= 2
        elif kind == "h3":
            y -= 6
            draw_wrapped(text, "Helvetica-Bold", 12, 16)
        elif kind == "code":
            y -= 4
            draw_wrapped(text, "Courier", 9, 11)
            y -= 2
        else:
            if text == "":
                y -= 10
                if y < margin:
                    new_page()
            else:
                draw_wrapped(text, "Helvetica", 11, 14)

        if y < margin:
            new_page()

    c.save()


def _collect_writings(idx: Dict) -> List[Dict]:
    writings = idx.get("writings", [])
    if not isinstance(writings, list):
        raise ValueError("writing/index.yaml: 'writings' must be a list.")
    for item in writings:
        if not isinstance(item, dict) or "path" not in item or "title" not in item:
            raise ValueError("Each writings[] item must be a mapping with at least 'path' and 'title'.")
    return writings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="Output zip path, e.g. dist/pack-writings.zip")
    ap.add_argument("--pdf", dest="pdf", action="store_true", help="Include generated PDFs")
    ap.add_argument("--no-pdf", dest="pdf", action="store_false", help="Do not include PDFs")
    ap.set_defaults(pdf=True)
    args = ap.parse_args()

    out_zip = Path(args.out)
    out_zip.parent.mkdir(parents=True, exist_ok=True)

    idx = _load_index_yaml()
    writings = _collect_writings(idx)

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bundle_root = f"pack-writings-{stamp}"

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

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
            pdf_dir = tmp / "pdf"
            pdf_dir.mkdir(parents=True, exist_ok=True)

            for item in writings:
                src = ROOT / item["path"]
                title = str(item["title"])
                md_text = _read_text(src)

                safe_title = _sanitize_filename(title)
                pdf_name = f"{safe_title}.pdf"
                pdf_path = pdf_dir / pdf_name

                _write_pdf_basic(pdf_path, title=title, md_text=md_text)

                zip_pdf_path = f"{bundle_root}/writing/pdfs/{pdf_name}"
                to_add.append((pdf_path, zip_pdf_path))

        with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for src, arc in to_add:
                z.write(src, arc)

    print(f"Wrote: {out_zip}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
