#!/usr/bin/env python3
"""
Safely update writing/index.yaml.

Rules:
- Preserve `site` exactly.
- Regenerate ONLY `writings`.
- Write YAML in ONE safe_dump call.
- Never concatenate YAML strings.
"""

from pathlib import Path
import yaml
import sys

ROOT = Path(__file__).resolve().parent.parent
INDEX_PATH = ROOT / "writing" / "index.yaml"
ESSAYS_DIR = ROOT / "writing" / "essays"


def extract_title(md_path: Path) -> str:
    for line in md_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return md_path.stem.replace("_", " ")


def main() -> int:
    if not INDEX_PATH.exists():
        raise FileNotFoundError(INDEX_PATH)

    data = yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("index.yaml must be a mapping")

    # Preserve site verbatim
    site = data.get("site", {})
    if not isinstance(site, dict):
        raise ValueError("'site' must be a mapping")

    writings = []
    for md in sorted(ESSAYS_DIR.glob("*.md")):
        writings.append(
            {
                "path": f"writing/essays/{md.name}",
                "title": extract_title(md),
            }
        )

    data["writings"] = writings

    # SINGLE write, fully serialized
    with INDEX_PATH.open("w", encoding="utf-8") as f:
        yaml.safe_dump(
            data,
            f,
            sort_keys=False,
            allow_unicode=True,
            default_style='"',   # prevents colon bugs forever
        )

    print(f"Updated {INDEX_PATH} with {len(writings)} essays (site preserved).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
