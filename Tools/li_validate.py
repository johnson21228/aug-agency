# Tools/li_validate.py

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception as e:
    raise SystemExit(
        "ERROR: PyYAML is required for li-validate.\n"
        "Install: pip install pyyaml\n"
        f"Details: {e}"
    ) from e


LI_ROOT = Path("LI")


def iter_li_structured_files() -> list[Path]:
    pats = ["*.yaml", "*.yml", "*.json"]
    out: list[Path] = []
    for pat in pats:
        out.extend(LI_ROOT.rglob(pat))
    return sorted({p for p in out if p.is_file()})


def has_tab_bytes(p: Path) -> bool:
    b = p.read_bytes()
    return b"\t" in b


def parse_yaml(p: Path) -> None:
    with p.open("r", encoding="utf-8") as f:
        yaml.safe_load(f)


def parse_json(p: Path) -> None:
    with p.open("r", encoding="utf-8") as f:
        json.load(f)


def main() -> int:
    if not LI_ROOT.exists():
        print("ERROR: LI/ directory not found.", file=sys.stderr)
        return 2

    files = iter_li_structured_files()
    if not files:
        print("ERROR: No structured LI files found under LI/ (*.yaml, *.yml, *.json).", file=sys.stderr)
        return 2

    tab_fail: list[Path] = []
    parse_fail: list[tuple[Path, str]] = []

    for p in files:
        if has_tab_bytes(p):
            tab_fail.append(p)

    # Parse only after tab scan so the failure report is stable.
    for p in files:
        try:
            if p.suffix.lower() in {".yaml", ".yml"}:
                parse_yaml(p)
            elif p.suffix.lower() == ".json":
                parse_json(p)
        except Exception as e:
            parse_fail.append((p, f"{type(e).__name__}: {e}"))

    if tab_fail:
        print("ERROR: Tabs found in LI structured files (replace tabs with spaces):", file=sys.stderr)
        for p in tab_fail:
            print(f"  - {p.as_posix()}", file=sys.stderr)

    if parse_fail:
        print("ERROR: Parse failures in LI structured files:", file=sys.stderr)
        for p, msg in parse_fail:
            print(f"  - {p.as_posix()}: {msg}", file=sys.stderr)

    if tab_fail or parse_fail:
        return 1

    print(f"OK: LI validate passed ({len(files)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())