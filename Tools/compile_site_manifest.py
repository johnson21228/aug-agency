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
from typing import Any, Dict, List

import yaml


ROOT = Path(__file__).resolve().parent.parent
LI_SRC = ROOT / "LI" / "site" / "index.source.yaml"
OUT = ROOT / "Derived" / "site" / "site_manifest.json"


def _as_dict(x: Any) -> Dict[str, Any]:
    return x if isinstance(x, dict) else {}


def _as_list(x: Any) -> List[Any]:
    return x if isinstance(x, list) else []


def _norm_items(lst: Any) -> List[Dict[str, str]]:
    """
    Normalize a list of items into:
      [{ "path": "...", "title": "..." }, ...]
    Ignores malformed entries.
    """
    out: List[Dict[str, str]] = []
    for it in _as_list(lst):
        if not isinstance(it, dict):
            continue
        if "path" not in it or "title" not in it:
            continue
        out.append({"path": str(it["path"]), "title": str(it["title"])})
    return out


def _compile_from_reading_paths(li: Dict[str, Any]) -> Dict[str, Any] | None:
    """
    New schema:

    reading_paths:
      start_here:
        label: ...
        audience: ...
        purpose: ...
        items:
          - path: ...
            title: ...
      start_here_builders:
        ...
    """
    reading_paths = _as_dict(li.get("reading_paths"))
    if not reading_paths:
        return None

    sections: List[Dict[str, Any]] = []
    for key, block_any in reading_paths.items():
        block = _as_dict(block_any)
        items = _norm_items(block.get("items"))

        # Only include sections that have at least one item
        if not items:
            continue

        sections.append(
            {
                "key": str(key),
                "label": str(block.get("label") or key),
                "audience": str(block.get("audience") or ""),
                "purpose": str(block.get("purpose") or ""),
                "items": items,
            }
        )

    return {"sections": sections}


def _compile_from_start_paths(li: Dict[str, Any]) -> Dict[str, Any] | None:
    """
    Backward-compatible schema:

    start_paths:
      start_here:
        - path: ...
          title: ...
      start_here_builders:
        - path: ...
          title: ...
    """
    start_paths = _as_dict(li.get("start_paths"))
    if not start_paths:
        return None

    start_here = _norm_items(start_paths.get("start_here"))
    start_here_builders = _norm_items(start_paths.get("start_here_builders"))

    sections: List[Dict[str, Any]] = []
    if start_here:
        sections.append(
            {
                "key": "start_here",
                "label": "Start here",
                "audience": "general",
                "purpose": "",
                "items": start_here,
            }
        )
    if start_here_builders:
        sections.append(
            {
                "key": "start_here_builders",
                "label": "Start here — builders",
                "audience": "builders",
                "purpose": "",
                "items": start_here_builders,
            }
        )

    return {"sections": sections}


def main() -> int:
    if not LI_SRC.exists():
        raise FileNotFoundError(f"Missing LI source: {LI_SRC}")

    li = yaml.safe_load(LI_SRC.read_text(encoding="utf-8"))
    if not isinstance(li, dict):
        raise ValueError("LI/site/index.source.yaml must parse to a mapping (dict).")

    site = _as_dict(li.get("site"))

    # Compile sections using preferred schema; fall back if needed
    compiled = _compile_from_reading_paths(li) or _compile_from_start_paths(li)
    if compiled is None:
        raise ValueError(
            "LI/site/index.source.yaml must contain either 'reading_paths' or 'start_paths'."
        )

    # Build final manifest (executable, not expressive)
    manifest: Dict[str, Any] = {
        "site": {
            "title": str(site.get("title", "IAM — Writings")),
            "h1": str(site.get("h1", site.get("title", "IAM — Writings"))),
            "lede": str(site.get("lede", "")).rstrip() + ("\n" if site.get("lede") else ""),
            "audiences": _as_dict(site.get("audiences")),
        },
        "sections": compiled["sections"],
        # Optional: can be populated later by a separate compiler step.
        "writings": _as_list(li.get("writings")) if isinstance(li.get("writings"), list) else [],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
