#!/usr/bin/env python3
"""
make_ingest_zip.py

Create a ZIP archive of the repository suitable for one-shot ingestion.

Includes:
- All tracked files
- All untracked files that are NOT ignored

Then filters to:
- Only *.md files

Excludes:
- Anything ignored by .gitignore
- The entire `data/` directory (hard exclusion)
- .git metadata

Usage:
    make ingest-zip
"""

import subprocess
import os
import zipfile
from datetime import datetime


EXCLUDED_TOP_LEVEL_DIRS = {"data"}
ALLOWED_EXTS = {".md"}


def git(cmd):
    return subprocess.check_output(cmd, text=True).strip()


def is_excluded(rel_path: str) -> bool:
    """Hard exclusions beyond gitignore."""
    parts = rel_path.split(os.sep)
    return parts[0] in EXCLUDED_TOP_LEVEL_DIRS


def is_allowed(rel_path: str) -> bool:
    """Content-type filter for ingestion."""
    _, ext = os.path.splitext(rel_path)
    return ext.lower() in ALLOWED_EXTS


def main():
    repo_root = git(["git", "rev-parse", "--show-toplevel"])

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_name = f"augmented-agency-ingest-md-{timestamp}.zip"
    out_path = os.path.join(repo_root, out_name)

    raw = subprocess.check_output([
        "git", "ls-files",
        "-z",
        "--cached",
        "--others",
        "--exclude-standard"
    ])

    paths = [p.decode("utf-8") for p in raw.split(b"\0") if p]

    included = []
    skipped = []

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in paths:
            if is_excluded(rel):
                skipped.append(rel)
                continue

            if not is_allowed(rel):
                skipped.append(rel)
                continue

            abs_path = os.path.join(repo_root, rel)
            if not os.path.isfile(abs_path):
                continue

            z.write(abs_path, arcname=rel)
            included.append(rel)

    print("Created ingest archive:")
    print(f"  {out_path}")
    print(f"Files included: {len(included)}")
    print(f"Files skipped: {len(skipped)}")
    if skipped:
        print("  (e.g.)", skipped[:10])


if __name__ == "__main__":
    main()
