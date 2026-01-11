from pathlib import Path
import yaml

INDEX_PATH = Path("writing/index.yaml")
ESSAYS_DIR = Path("writing/essays")

def load_existing():
    if INDEX_PATH.exists():
        with INDEX_PATH.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}

def extract_title(md_path: Path) -> str:
    try:
        for line in md_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    except Exception:
        pass
    return md_path.stem.replace("_", " ")

def main():
    data = load_existing()

    essays = sorted(ESSAYS_DIR.glob("*.md"))
    writings = []

    for md in essays:
        writings.append({
            "path": md.as_posix(),
            "title": extract_title(md),
        })

    data["writings"] = writings

    with INDEX_PATH.open("w", encoding="utf-8") as f:
        yaml.safe_dump(
            data,
            f,
            sort_keys=False,
            allow_unicode=True,
        )

    print(f"Updated {INDEX_PATH} with {len(writings)} essays")

if __name__ == "__main__":
    main()
