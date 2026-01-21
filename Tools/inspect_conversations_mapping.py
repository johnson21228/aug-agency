#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import Counter

def preview(x: Any, n: int = 140) -> str:
    s = json.dumps(x, ensure_ascii=False) if isinstance(x, (dict, list)) else str(x)
    return s if len(s) <= n else s[: n - 1] + "…"

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", required=True, help="Path to conversations.json")
    ap.add_argument("--index", type=int, default=0, help="Which conversation in the list to inspect")
    ap.add_argument("--title", type=str, default="", help="If set, search first conversation whose title contains this substring")
    ap.add_argument("--nodes", type=int, default=5, help="How many mapping nodes to sample")
    args = ap.parse_args()

    path = Path(args.path).expanduser().resolve()
    data = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(data, list):
        raise SystemExit("Expected root list")

    conv = None
    if args.title:
        needle = args.title.lower()
        for c in data:
            if isinstance(c, dict) and str(c.get("title","")).lower().find(needle) >= 0:
                conv = c
                break
        if conv is None:
            raise SystemExit(f"No conversation title matched: {args.title}")
    else:
        conv = data[args.index]

    if not isinstance(conv, dict):
        raise SystemExit("Conversation is not dict")

    print("CONVERSATION")
    print(" title:", conv.get("title"))
    print(" conversation_id:", conv.get("conversation_id") or conv.get("id"))
    print(" create_time:", conv.get("create_time"))
    print(" update_time:", conv.get("update_time"))
    print(" current_node:", conv.get("current_node"))
    print(" keys:", list(conv.keys()))

    mapping = conv.get("mapping")
    if not isinstance(mapping, dict):
        raise SystemExit("conv['mapping'] not a dict")

    print("\nMAPPING")
    print(" nodes:", len(mapping))
    node_ids = list(mapping.keys())

    # Show schema of a few nodes
    sample_ids = node_ids[: args.nodes]
    print("\nNODE SCHEMA SAMPLES")
    for nid in sample_ids:
        node = mapping[nid]
        print("\n--- node id:", nid)
        if not isinstance(node, dict):
            print("  node type:", type(node).__name__)
            continue
        print("  node keys:", list(node.keys()))
        for k in ["id", "parent", "children"]:
            if k in node:
                print(f"  {k}:", preview(node.get(k)))
        msg = node.get("message")
        print("  message type:", type(msg).__name__)
        if isinstance(msg, dict):
            print("  message keys:", list(msg.keys()))
            for mk in ["id", "author", "create_time", "update_time", "role", "content", "metadata"]:
                if mk in msg:
                    print(f"    {mk}:", preview(msg.get(mk)))

    # Gather message field frequencies (helps us find role/content paths)
    print("\nMESSAGE FIELD FREQUENCY (first 200 nodes with dict message)")
    msg_key_freq = Counter()
    author_key_freq = Counter()
    content_key_freq = Counter()

    seen = 0
    for nid in node_ids:
        node = mapping.get(nid)
        if not isinstance(node, dict):
            continue
        msg = node.get("message")
        if not isinstance(msg, dict):
            continue
        msg_key_freq.update(msg.keys())
        author = msg.get("author")
        if isinstance(author, dict):
            author_key_freq.update(author.keys())
        content = msg.get("content")
        if isinstance(content, dict):
            content_key_freq.update(content.keys())
        seen += 1
        if seen >= 200:
            break

    print(" message keys:", msg_key_freq.most_common(30))
    if author_key_freq:
        print(" author keys:", author_key_freq.most_common(30))
    if content_key_freq:
        print(" content keys:", content_key_freq.most_common(30))

    return 0

if __name__ == "__main__":
    raise SystemExit(main())