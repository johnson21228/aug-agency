#!/usr/bin/env python3
"""
inspect_conversations_json.py

Usage (from augmented-agency repo root):
  python3 tools/inspect_conversations_json.py \
    --path ../augmented-agency-data/<export-dir>/conversations.json \
    --samples 2 \
    --max-depth 4

If --path is omitted, the script tries:
  ../augmented-agency-data/**/conversations.json  (most recent mtime)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union
from collections import Counter, defaultdict

Json = Union[dict, list, str, int, float, bool, None]


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def human(n: int) -> str:
    # simple human-ish formatter
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024:
            return f"{n:.0f}{unit}"
        n /= 1024
    return f"{n:.0f}PB"


def find_default_conversations_json(repo_root: Path) -> Path | None:
    data_root = (repo_root / ".." / "augmented-agency-data").resolve()
    if not data_root.exists():
        return None
    candidates = list(data_root.rglob("conversations.json"))
    if not candidates:
        return None
    # choose most recently modified
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def load_json(path: Path) -> Json:
    # conversations.json can be large; but we still load fully for schema scan.
    # If this becomes too big, we can switch to ijson streaming later.
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def type_name(x: Any) -> str:
    return type(x).__name__


def preview_value(v: Any, limit: int = 120) -> str:
    if isinstance(v, (dict, list)):
        s = json.dumps(v, ensure_ascii=False)
    else:
        s = str(v)
    if len(s) > limit:
        return s[: limit - 1] + "…"
    return s


def keys_top(d: dict, max_keys: int = 40) -> List[str]:
    ks = list(d.keys())
    return ks[:max_keys] + (["…"] if len(ks) > max_keys else [])


def list_summary(lst: list, max_items: int = 5) -> str:
    types = Counter(type_name(x) for x in lst[: max_items])
    total = len(lst)
    return f"len={total}, first_types={dict(types)}"


def get_at_path(obj: Json, path: List[Union[str, int]]) -> Any:
    cur: Any = obj
    for p in path:
        if isinstance(p, int):
            if not isinstance(cur, list) or p >= len(cur):
                return None
            cur = cur[p]
        else:
            if not isinstance(cur, dict) or p not in cur:
                return None
            cur = cur[p]
    return cur


def jsonpath(path: List[Union[str, int]]) -> str:
    s = "$"
    for p in path:
        if isinstance(p, int):
            s += f"[{p}]"
        else:
            # simple key path (no escaping)
            s += f".{p}"
    return s


def find_list_fields(obj: dict, min_len: int = 1) -> List[Tuple[str, int]]:
    out: List[Tuple[str, int]] = []
    for k, v in obj.items():
        if isinstance(v, list) and len(v) >= min_len:
            out.append((k, len(v)))
    out.sort(key=lambda t: t[1], reverse=True)
    return out


def guess_conversation_container(root: Json) -> Tuple[str, list] | None:
    """
    Try to locate the list of conversations.
    Common patterns:
      root is list
      root["conversations"] is list
      root["items"] / root["data"] is list
    Returns (jsonpath, list_ref)
    """
    if isinstance(root, list):
        return ("$", root)

    if isinstance(root, dict):
        for key in ["conversations", "items", "data", "chats", "threads"]:
            v = root.get(key)
            if isinstance(v, list) and v:
                return (f"$.{key}", v)

        # fallback: largest list field at top-level
        candidates = find_list_fields(root, min_len=1)
        if candidates:
            k, _ = candidates[0]
            return (f"$.{k}", root[k])

    return None


def guess_message_container(conv_obj: dict) -> Tuple[str, list] | None:
    """
    Try to find list of messages/turns inside a conversation object.
    """
    for key in ["messages", "mapping", "turns", "items", "chat_messages", "conversation", "content"]:
        v = conv_obj.get(key)
        if isinstance(v, list) and v:
            return (f".{key}", v)

    # sometimes messages are under nested dict keys
    # e.g. {"mapping": {...}} in ChatGPT exports, but mapping is dict.
    # We scan for list fields, preferring ones with dict elements.
    list_fields = []
    for k, v in conv_obj.items():
        if isinstance(v, list) and v:
            # score: how many dicts in first few
            score = sum(1 for x in v[:5] if isinstance(x, dict))
            list_fields.append((k, len(v), score))
    list_fields.sort(key=lambda t: (t[2], t[1]), reverse=True)
    if list_fields and list_fields[0][2] > 0:
        k, _, _ = list_fields[0]
        return (f".{k}", conv_obj[k])

    return None


def scan_message_fields(messages: list, max_scan: int = 200) -> Dict[str, Counter]:
    """
    Look across first N messages (dicts) and gather key frequency, plus role/timestamp candidates.
    """
    key_freq = Counter()
    role_vals = Counter()
    ts_keys = Counter()
    id_keys = Counter()

    common_ts_keys = {"timestamp", "time", "created_at", "create_time", "updated_at", "date", "datetime"}
    common_id_keys = {"id", "message_id", "uuid", "node_id", "client_id"}

    for m in messages[:max_scan]:
        if not isinstance(m, dict):
            continue
        key_freq.update(m.keys())

        # role
        for rk in ["role", "author", "sender", "from"]:
            if rk in m:
                role_vals.update([f"{rk}={preview_value(m[rk], 60)}"])
        # timestamps
        for k in m.keys():
            lk = k.lower()
            if lk in common_ts_keys or lk.endswith("_time") or lk.endswith("_at"):
                ts_keys.update([k])
        # ids
        for k in m.keys():
            lk = k.lower()
            if lk in common_id_keys or lk.endswith("_id"):
                id_keys.update([k])

    return {
        "message_keys": key_freq,
        "role_candidates": role_vals,
        "timestamp_key_candidates": ts_keys,
        "id_key_candidates": id_keys,
    }


def print_header(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", type=str, default="", help="Path to conversations.json (relative to repo root OK)")
    ap.add_argument("--samples", type=int, default=2, help="How many conversations to sample")
    ap.add_argument("--max-depth", type=int, default=4, help="How deep to print nested structure preview")
    args = ap.parse_args()

    repo_root = Path.cwd()

    if args.path:
        path = Path(args.path).expanduser()
        if not path.is_absolute():
            path = (repo_root / path).resolve()
    else:
        found = find_default_conversations_json(repo_root)
        if not found:
            eprint("ERROR: --path not provided and could not find ../augmented-agency-data/**/conversations.json")
            return 2
        path = found

    if not path.exists():
        eprint(f"ERROR: file not found: {path}")
        return 2

    print_header("FILE")
    st = path.stat()
    print(f"path: {path}")
    print(f"size: {human(st.st_size)}")
    print(f"mtime: {st.st_mtime:.0f}")

    print_header("LOAD JSON")
    root = load_json(path)
    print(f"root type: {type_name(root)}")

    if isinstance(root, dict):
        print(f"top-level keys ({len(root)}): {keys_top(root)}")
        list_fields = find_list_fields(root, min_len=1)
        if list_fields:
            print("top-level list fields (key, len):", list_fields[:10])
    elif isinstance(root, list):
        print(list_summary(root))

    print_header("GUESS CONVERSATION CONTAINER")
    cc = guess_conversation_container(root)
    if not cc:
        print("Could not auto-detect conversation list container.")
        print("If root is dict, examine top-level keys above and pass correct path manually later.")
        return 0

    conv_path, conv_list = cc
    print(f"conversation_list_path: {conv_path}")
    print(f"conversation_list_summary: {list_summary(conv_list)}")

    # sample conversation objects
    samples = [c for c in conv_list if isinstance(c, dict)][: max(1, args.samples)]
    if not samples:
        print("No dict-like conversation objects found in the detected list.")
        return 0

    print_header("SAMPLE CONVERSATION OBJECTS")
    for i, conv in enumerate(samples):
        print(f"\n--- sample #{i} ---")
        print(f"type: {type_name(conv)}")
        print(f"keys ({len(conv)}): {keys_top(conv)}")
        # show small previews of a few keys
        for k in list(conv.keys())[: min(12, len(conv))]:
            v = conv[k]
            if isinstance(v, dict):
                print(f"  {k}: dict(keys={len(v)}, preview_keys={list(v.keys())[:8]})")
            elif isinstance(v, list):
                print(f"  {k}: list({list_summary(v)})")
            else:
                print(f"  {k}: {type_name(v)} = {preview_value(v)}")

        # try to find messages
        mc = guess_message_container(conv)
        print("\n  message_container_guess:", mc[0] if mc else None)
        if mc:
            _, msgs = mc
            msg_dicts = [m for m in msgs if isinstance(m, dict)]
            print(f"  messages_len: {len(msgs)} (dicts={len(msg_dicts)})")
            scan = scan_message_fields(msgs)
            print("  most_common_message_keys:", scan["message_keys"].most_common(20))
            print("  role_candidates:", scan["role_candidates"].most_common(10))
            print("  timestamp_key_candidates:", scan["timestamp_key_candidates"].most_common(10))
            print("  id_key_candidates:", scan["id_key_candidates"].most_common(10))
        else:
            # hint about mapping-style exports
            if "mapping" in conv and isinstance(conv["mapping"], dict):
                print("  NOTE: conv['mapping'] is a dict. This is common in ChatGPT exports.")
                print("  We may need to linearize messages by traversing parent/child links.")
                print("  mapping keys preview:", list(conv["mapping"].keys())[:5])

    print_header("NEXT ACTION")
    print("Paste the output of this script here.")
    print("Then I will:")
    print("  1) extract a concrete schema (paths + field names)")
    print("  2) define an idempotent client_lui_id strategy")
    print("  3) write the adaptor that emits spooler POSTs per message/turn")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())