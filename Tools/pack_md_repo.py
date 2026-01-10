#!/usr/bin/env python3
"""
make_ingest_zip.py

Create a ZIP from:
- All tracked files in the repo (git ls-files)
- All untracked files that are NOT ignored

Then filters to:
- Only *.md and *.py files

Excludes:
- Anything ignored by .gitignore
- Anything under excluded top-level dirs (see EXCLUDED_TOP_LEVEL_DIRS)

Usage:
    make ingest-zip
"""

import subprocess
import os
import zipfile
from datetime import datetime

EXCLUDED_TOP_LEVEL_DIRS = {"data"}
ALLOWED_EXTS =  {".md", ".py", ".sql",".json"}


def git(cmd):
    return subprocess.check_output(cmd, text=True).strip()


def main():
    repo_root = git(["git", "rev-parse", "--show-toplevel"])

    out_name = f"augmented-agency-ingest-md-py.zip"
    out_path = os.path.join(repo_root, out_name)

    # tracked files
    tracked = git(["git", "ls-files"]).splitlines()

    # untracked, not ignored
    untracked = git(["git", "ls-files", "--others", "--exclude-standard"]).splitlines()

    all_files = tracked + untracked
    selected = []
    skipped = []

    for rel in all_files:
        if not rel:
            continue

        top = rel.split("/", 1)[0]
        if top in EXCLUDED_TOP_LEVEL_DIRS:
            skipped.append(rel)
            continue

        ext = os.path.splitext(rel)[1].lower()
        if ext not in ALLOWED_EXTS:
            skipped.append(rel)
            continue

        selected.append(rel)

    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for rel in selected:
            abs_path = os.path.join(repo_root, rel)
            if os.path.isfile(abs_path):
                z.write(abs_path, arcname=rel)

    print(f"Wrote: {out_path}")
    print(f"Included: {len(selected)} files")
    if skipped:
        print(f"Skipped: {len(skipped)} files (showing first 10)")
        print("  " + "\n  ".join(skipped[:10]))


if __name__ == "__main__":
    main()
