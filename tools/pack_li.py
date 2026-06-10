#!/usr/bin/env python3
"""
tools/pack_li.py

Create a deterministic ZIP bundle for the IAM Language Infrastructure (LI),
excluding writings.

- Includes: tracked + untracked non-ignored files (git ls-files + others)
- Filters by allowed extensions (md/py/sql/json/yaml/yml)
- Excludes configurable top-level dirs (default: writing, data, residue)
- Writes a manifest with SHA-256 per file for auditability

Usage:
  python tools/pack_li.py --out dist/pack-li.zip
  python tools/pack_li.py --out dist/pack-li.zip --exclude writing,data,residue,patent
"""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import zipfile
from pathlib import Path
from typing import List, Tuple

ALLOWED_EXTS = {".md", ".py", ".sql", ".json", ".yaml", ".yml"}

DEFAULT_EXCLUDED_TOP_LEVEL_DIRS = {"writing", "data", "residue"}


def git(cmd: List[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="Output zip path, e.g. dist/pack-li.zip")
    ap.add_argument(
        "--exclude",
        default=",".join(sorted(DEFAULT_EXCLUDED_TOP_LEVEL_DIRS)),
        help="Comma-separated top-level dirs to exclude (default: writing,data,residue)",
    )
    args = ap.parse_args()

    excluded = {s.strip() for s in args.exclude.split(",") if s.strip()}

    repo_root = Path(git(["git", "rev-parse", "--show-toplevel"]))
    out_path = (repo_root / args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # tracked files
    tracked = git(["git", "ls-files"]).splitlines()
    # untracked, not ignored
    untracked = git(["git", "ls-files", "--others", "--exclude-standard"]).splitlines()

    all_files = [p for p in (tracked + untracked) if p]
    selected: List[str] = []
    skipped: List[str] = []

    for rel in all_files:
        top = rel.split("/", 1)[0]
        if top in excluded:
            skipped.append(rel)
            continue

        ext = os.path.splitext(rel)[1].lower()
        if ext not in ALLOWED_EXTS:
            skipped.append(rel)
            continue

        abs_path = repo_root / rel
        if abs_path.is_file():
            selected.append(rel)
        else:
            skipped.append(rel)

    # deterministic ordering
    selected.sort()

    manifest_lines: List[str] = []
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for rel in selected:
            abs_path = repo_root / rel
            digest = sha256_file(abs_path)
            manifest_lines.append(f"{digest}  {rel}")
            z.write(abs_path, arcname=rel)

        # embed manifest inside zip
        z.writestr("MANIFEST.sha256", "\n".join(manifest_lines) + "\n")

    print(f"Wrote: {out_path}")
    print(f"Included: {len(selected)} files")
    print(f"Excluded top-level dirs: {sorted(excluded)}")
    if skipped:
        print(f"Skipped: {len(skipped)} files (showing first 10)")
        print("  " + "\n  ".join(skipped[:10]))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
