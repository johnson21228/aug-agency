#!/usr/bin/env python3
"""
make_ingest_zip.py

Create a ZIP archive of the repository suitable for one-shot ingestion.

Includes:
- All tracked files
- All untracked files that are NOT ignored

Excludes:
- Anything ignored by .gitignore
- .git/info/exclude
- Global gitignore rules

This produces a clean snapshot of the repo's *semantic surface*:
architecture, essays, code, patents, references — without local artifacts.

Usage:
    python3 tools/make_ingest_zip.py

Output:
    augmented-agency-ingest-YYYYMMDD-HHMMSS.zip
"""

import subprocess
import os
import zipfile
from datetime import datetime


def git(cmd):
    return subprocess.check_output(cmd, text=True).strip()


def main():
    repo_root = git(["git", "rev-parse", "--show-toplevel"])

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_name = f"augmented-agency-ingest-{timestamp}.zip"
    out_path = os.path.join(repo_root, out_name)

    # Get tracked + untracked (but not ignored) files.
    # NUL-separated to safely handle spaces and special characters.
    raw = subprocess.check_output([
        "git", "ls-files",
        "-z",
        "--cached",
        "--others",
        "--exclude-standard"
    ])

    paths = [p.decode("utf-8") for p in raw.split(b"\0") if p]

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        for rel_path in paths:
            abs_path = os.path.join(repo_root, rel_path)
            if os.path.isfile(abs_path):
                z.write(abs_path, arcname=rel_path)

    print(f"Created ingest archive:")
    print(f"  {out_path}")
    print(f"Files included: {len(paths)}")


if __name__ == "__main__":
    main()
