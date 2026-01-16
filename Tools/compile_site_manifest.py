#!/usr/bin/env python3
"""
Site Language Infrastructure (LI) Compiler

This file is a Language Infrastructure compiler.

Role:
- Transforms authoritative, human-authored Site LI (LI/site/)
  into a machine-consumable, executable manifest (Derived/site/).
- Enforces the boundary between intent (LI) and execution (Derived).

Authority rules:
- LI/site/* is normative and must never be mutated by tools.
- Derived/site/* is disposable and fully regenerable.
- Site execution MUST consume only Derived artifacts.

Why this exists:
- Prevents regeneration of meaning from prose.
- Prevents YAML mutation and structural drift.
- Makes site construction deterministic and auditable.

This compiler is the only lawful bridge between Site LI and execution.
Bypassing it is a violation of the repo’s LI invariants.

Usage:
  python3 Tools/compile_site_manifest.py
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parent.parent
LI_SRC = ROOT / "LI" / "site" / "index.source.yaml"
OUT = ROOT / "Derived" / "site" / "site_manifest.json"

def main() -> int:
    if not LI_SRC.exists():
        raise FileNotFoundError(f"Missing LI source: {LI_SRC}")

    data = yaml.safe_load(LI_SRC.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("LI/site/index.source.yaml must parse to a mapping (dict).")

    site = data.get("site", {}) if isinstance(data.get("site", {}), dict) else {}
    start_paths = data.get("start_paths", {}) if isinstance(data.get("start_paths", {}), dict) else {}

    start_here = start_paths.get("start_here", [])
    start_here_builders = start_paths.get("start_here_builders", [])

    def normalize_list(lst):
        out = []
        if not isinstance(lst, list):
            return out
        for item in lst:
            if isinstance(item, dict) and "path" in item and "title" in item:
                out.append({"path": str(item["path"]), "title": str(item["title"])})
        return out

    manifest = {
        "site": {
            "title": site.get("title", "IAM — Writings"),
            "h1": site.get("h1", site.get("title", "IAM — Writings")),
            "lede": site.get("lede", ""),
        },
        "start_here": normalize_list(start_here),
        "start_here_builders": normalize_list(start_here_builders),
        # Optional: this can be filled later by a separate catalog compiler
        "writings": [],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
