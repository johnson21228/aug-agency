#!/usr/bin/env python3
"""
Build PDF bundles for site reading paths.

Inputs (executable LI):
- Derived/site/site_manifest.json

Outputs (derived artifacts):
- dist/bundles/<section_key>.zip
- dist/bundles/<section_key>/*.pdf

Optional publish output:
- docs/downloads/<section_key>.zip

PDF formatting:
- 3 inch right margin (notes margin)
- 1 inch top/bottom/left
- xelatex via pandoc
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "Derived" / "site" / "site_manifest.json"

DIST_DIR = ROOT / "dist" / "bundles"
DOCS_DOWNLOADS_DIR = ROOT / "docs" / "downloads"

# PDF layout: 3-inch right margin for notes
PDF_GEOMETRY = "top=1in,bottom=1in,left=1in,right=3in"
PDF_FONTSIZE = "11pt"
PDF_ENGINE = "xelatex"


def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s)
    return s.strip("-") or "untitled"


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def ensure_tools() -> None:
    # Fail fast with helpful messages if pandoc isn't available
    if shutil.which("pandoc") is None:
        raise RuntimeError(
            "pandoc not found. Install pandoc (e.g., brew install pandoc) "
            "and ensure it's on PATH."
        )
    # xelatex is invoked by pandoc; availability varies by TeX install.
    if shutil.which("xelatex") is None:
        raise RuntimeError(
            "xelatex not found. Install a TeX distribution (MacTeX or TinyTeX) "
            "so pandoc can render PDFs."
        )


def load_manifest() -> dict:
    if not MANIFEST.exists():
        raise FileNotFoundError(
            f"Missing manifest: {MANIFEST}\n"
            "Run: python3 Tools/compile_site_manifest.py"
        )
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def build_pdf(md_rel_path: str, title: str, out_pdf: Path) -> None:
    md_path = ROOT / md_rel_path
    if not md_path.exists():
        raise FileNotFoundError(f"Essay markdown not found: {md_path}")

    out_pdf.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "pandoc",
        str(md_path),
        "-o",
        str(out_pdf),
        "--pdf-engine",
        PDF_ENGINE,
        "-V",
        f"geometry:{PDF_GEOMETRY}",
        "-V",
        f"fontsize={PDF_FONTSIZE}",
        # Keep metadata title stable even if file name differs
        "-M",
        f"title={title}",
    ]
    run(cmd)


def zip_dir(folder: Path, zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as z:
        for p in sorted(folder.rglob("*.pdf")):
            z.write(p, arcname=p.name)


def main() -> int:
    ensure_tools()

    manifest = load_manifest()
    sections = manifest.get("sections", [])
    if not isinstance(sections, list) or not sections:
        raise ValueError("Manifest has no sections. Check Derived/site/site_manifest.json")

    DIST_DIR.mkdir(parents=True, exist_ok=True)

    for sec in sections:
        if not isinstance(sec, dict):
            continue
        key = str(sec.get("key") or "").strip()
        label = str(sec.get("label") or key).strip()
        items = sec.get("items", [])
        if not key or not isinstance(items, list) or not items:
            continue

        # Output folder for this section
        section_dir = DIST_DIR / key
        if section_dir.exists():
            shutil.rmtree(section_dir)
        section_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n== Building bundle: {key} ({label}) ==")

        seen_slugs = set()
        for i, it in enumerate(items, start=1):
            if not isinstance(it, dict):
                continue
            md_path = str(it.get("path") or "").strip()
            title = str(it.get("title") or "").strip()
            if not md_path:
                continue

            base = slugify(title) if title else slugify(Path(md_path).stem)
            # Ensure unique filenames within a bundle
            out_name = base
            n = 2
            while out_name in seen_slugs:
                out_name = f"{base}-{n}"
                n += 1
            seen_slugs.add(out_name)

            out_pdf = section_dir / f"{i:02d}-{out_name}.pdf"
            print(f"  - {out_pdf.name}  <=  {md_path}")
            build_pdf(md_path, title or Path(md_path).stem, out_pdf)

        # Zip it
        zip_path = DIST_DIR / f"{key}.zip"
        zip_dir(section_dir, zip_path)
        print(f"== Wrote ZIP: {zip_path} ==")

        # Optional: copy into docs/downloads for site hosting
        DOCS_DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(zip_path, DOCS_DOWNLOADS_DIR / zip_path.name)
        print(f"== Copied to: {DOCS_DOWNLOADS_DIR / zip_path.name} ==")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
