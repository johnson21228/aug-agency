#!/usr/bin/env python3
"""Inventory the current git worktree for cleanup planning.

This script does not modify files. It groups `git status --short` output into
likely categories so the human owner can decide commit boundaries.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from collections import defaultdict

ROOT = Path.cwd()

SENSITIVE_PREFIXES = ("patent/", "legal/", "private/", "secrets/", "data/")
GENERATED_PREFIXES = ("dist/", "outputs/", "Derived/", "docs/site/", "site/")
SOURCE_PREFIXES = ("LI/", "architecture/", "core-ontology/", "embodiments/", "governance/", "writing/", "prompts/", "tools/")


def git_status() -> list[str]:
    out = subprocess.check_output(["git", "status", "--short"], text=True)
    return [line for line in out.splitlines() if line.strip()]


def classify(path: str) -> str:
    p = path.strip()
    if p.startswith(SENSITIVE_PREFIXES):
        return "sensitive-review-before-commit"
    if p.startswith(GENERATED_PREFIXES):
        return "generated-or-pack-output"
    if p.startswith(SOURCE_PREFIXES) or p in {"README.md", "MAP.md", "Makefile", "LLM_READ_FIRST.md", "HOW_LI_RULES.md", "SPINE.md"}:
        return "likely-source-or-governance"
    return "needs-human-classification"


def main() -> int:
    lines = git_status()
    groups: dict[str, list[str]] = defaultdict(list)
    for line in lines:
        # format: XY path, or XY old -> new
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        groups[classify(path)].append(line)

    print("# Worktree Inventory")
    print()
    print(f"Repository: {ROOT}")
    print()
    if not lines:
        print("Worktree is clean.")
        return 0
    for group in [
        "likely-source-or-governance",
        "sensitive-review-before-commit",
        "generated-or-pack-output",
        "needs-human-classification",
    ]:
        items = groups.get(group, [])
        if not items:
            continue
        print(f"## {group}")
        print()
        for item in items:
            print(f"- `{item}`")
        print()

    print("## Suggested discipline")
    print()
    print("Do not run `git add -A` until every item above has an intentional commit destination.")
    print("Commit narrow accepted CB/governance work before broad tooling/site/patent work.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
