#!/usr/bin/env python3
"""
Site Language Infrastructure (LI) Compiler

Prefers JSON source to eliminate YAML fragility in human-authored LI.

Inputs (authoritative):
- LI/site/index.source.json  (preferred)
- LI/site/index.source.yaml  (fallback)

Output (derived, executable):
- Derived/site/site_manifest.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import yaml


ROOT = Path(__file__).resolve().parent.parent

LI_JSON = ROOT / "LI" / "site" / "index.source.json"
LI_YAML = ROOT / "LI" / "site" / "index.source.yaml"
OUT = ROOT / "Derived" / "site" / "site_manifest.json"


def _as_dict(x: Any) -> Dict[str, Any]:
    return x if isinstance(x, dict) else {}


def _as_list(x: Any) -> List[Any]:
    return x if isinstance(x, list) else []


def _norm_items(lst: Any) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    for it in _as_list(lst):
        if not isinstance(it, dict):
            continue
        p = it.get("path")
        t = it.get("title")
        if not p or not t:
            continue
        out.append({"path": str(p), "title": str(t)})
    return out


def load_li() -> Dict[str, Any]:
    if LI_JSON.exists():
        return json.loads(LI_JSON.read_text(encoding="utf-8"))
    if LI_YAML.exists():
        data = yaml.safe_load(LI_YAML.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("LI YAML must parse to a mapping (dict).")
        return data
    raise FileNotFoundError(
        f"Missing LI source. Expected one of:\n- {LI_JSON}\n- {LI_YAML}"
    )


def compile_from_json_shape(li: Dict[str, Any]) -> Dict[str, Any] | None:
    # JSON shape:
    # { site: {...}, sections: [ {key,label,purpose,items:[{path,title}]} ... ] }
    if "sections" not in li:
        return None

    site = _as_dict(li.get("site"))
    sections_in = _as_list(li.get("sections"))

    sections: List[Dict[str, Any]] = []
    for sec in sections_in:
        if not isinstance(sec, dict):
            continue
        key = str(sec.get("key") or "").strip()
        label = str(sec.get("label") or "").strip()
        audience = str(sec.get("audience") or "").strip()
        purpose = str(sec.get("purpose") or "")
        items = _norm_items(sec.get("items"))
        if not key or not label or not items:
            continue
        sections.append(
            {
                "key": key,
                "label": label,
                "audience": audience,
                "purpose": purpose,
                "items": items,
            }
        )

    manifest = {
        "site": {
            "title": str(site.get("title", "IAM — Writings")),
            "h1": str(site.get("h1", site.get("title", "IAM — Writings"))),
            "lede": str(site.get("lede", "")).rstrip() + ("\n" if site.get("lede") else ""),
            "audiences": _as_dict(site.get("audiences")),
        },
        "sections": sections,
        "writings": _as_list(li.get("writings")) if isinstance(li.get("writings"), list) else [],
    }
    return manifest


def compile_from_yaml_shape(li: Dict[str, Any]) -> Dict[str, Any]:
    # Your existing YAML shape (reading_paths or start_paths) remains supported.
    site = _as_dict(li.get("site"))

    sections: List[Dict[str, Any]] = []

    reading_paths = _as_dict(li.get("reading_paths"))
    if reading_paths:
        for key, block_any in reading_paths.items():
            block = _as_dict(block_any)
            items = _norm_items(block.get("items"))
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
    else:
        start_paths = _as_dict(li.get("start_paths"))
        if start_paths:
            sh = _norm_items(start_paths.get("start_here"))
            sb = _norm_items(start_paths.get("start_here_builders"))
            if sh:
                sections.append(
                    {"key": "start_here", "label": "Start here", "audience": "general", "purpose": "", "items": sh}
                )
            if sb:
                sections.append(
                    {"key": "start_here_builders", "label": "Start here — builders", "audience": "builders", "purpose": "", "items": sb}
                )
        else:
            raise ValueError("YAML LI must contain either 'reading_paths' or 'start_paths'.")

    return {
        "site": {
            "title": str(site.get("title", "IAM — Writings")),
            "h1": str(site.get("h1", site.get("title", "IAM — Writings"))),
            "lede": str(site.get("lede", "")).rstrip() + ("\n" if site.get("lede") else ""),
            "audiences": _as_dict(site.get("audiences")),
        },
        "sections": sections,
        "writings": [],
    }


def main() -> int:
    li = load_li()

    manifest = compile_from_json_shape(li)
    if manifest is None:
        manifest = compile_from_yaml_shape(li)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
