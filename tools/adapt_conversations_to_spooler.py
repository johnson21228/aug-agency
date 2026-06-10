#!/usr/bin/env python3
"""
adapt_conversations_to_spooler.py

Reads ChatGPT export conversations.json (root list of conversations).
Linearizes each conversation's main branch using current_node parent-chain.
Extracts user + assistant visible text messages from mapping nodes.
Pairs user -> assistant safely (skipping tool-call/hidden/system-ish messages).
Emits spool payloads via dry-run, NDJSON, or POST.

This version adds:
- Filtering to avoid tool/command assistant nodes
- Timestamp sanity check: assistant.create_time >= user.create_time when both exist
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

Json = Any


def eprint(*args: object) -> None:
    print(*args, file=sys.stderr)


def unix_to_iso8601_utc(ts: Optional[float]) -> Optional[str]:
    if ts is None:
        return None
    try:
        return datetime.fromtimestamp(float(ts), tz=timezone.utc).isoformat()
    except Exception:
        return None


def extract_text_from_content(content: Any) -> str:
    """
    Observed content variants:
      - {"content_type": "text", "parts": [<strings>...]}
      - {"content_type": "text", "text": "..."}
    Be conservative; return "" for non-text content.
    """
    if not isinstance(content, dict):
        return ""

    if content.get("content_type") != "text":
        return ""

    parts = content.get("parts")
    if isinstance(parts, list):
        strs = [p for p in parts if isinstance(p, str)]
        if strs:
            return "\n".join(strs).strip()

    txt = content.get("text")
    if isinstance(txt, str) and txt.strip():
        return txt.strip()

    # Conservative fallback
    c = content.get("content")
    if isinstance(c, str) and c.strip():
        return c.strip()

    return ""


def looks_like_command_blob(text: str) -> bool:
    """
    Fallback filter for assistant nodes that are actually tool/command payloads.
    Keep conservative (few prefixes).
    """
    t = text.lstrip()
    prefixes = (
        "bash -lc ",
        "python ",
        "python3 ",
        "curl ",
        "rm -rf ",
        "ls -la ",
        "find ",
        "cat ",
        "unzip ",
    )
    return t.startswith(prefixes)

def message_is_hidden_or_toolish(msg: Dict[str, Any]) -> bool:
    """
    Only skip on explicit "hidden/rebase/next" indicators that we have
    already observed in your export. Do NOT gate on channel/recipient
    until we empirically confirm their normal values.
    """
    meta = msg.get("metadata")
    if not isinstance(meta, dict):
        meta = {}

    if meta.get("is_visually_hidden_from_conversation") is True:
        return True

    if meta.get("rebase_system_message") is True:
        return True
    if meta.get("rebase_developer_message") is True:
        return True
    if meta.get("rebase_user_message") is True:
        return True

    mt = meta.get("message_type")
    if isinstance(mt, str) and mt.lower() in {"next"}:
        return True

    return False


@dataclass
class MessageItem:
    conv_id: str
    conv_title: str
    node_id: str
    msg_id: str
    role: str
    create_time: Optional[float]
    text: str
    raw_message: Dict[str, Any]


def linearize_main_branch(conv: Dict[str, Any]) -> List[str]:
    mapping = conv.get("mapping")
    if not isinstance(mapping, dict):
        return []

    current = conv.get("current_node")
    if not isinstance(current, str) or current not in mapping:
        return []

    chain: List[str] = []
    seen = set()
    nid: Optional[str] = current

    while isinstance(nid, str) and nid in mapping:
        if nid in seen:
            break
        seen.add(nid)
        chain.append(nid)

        node = mapping.get(nid)
        parent = node.get("parent") if isinstance(node, dict) else None
        if parent is None:
            break
        nid = parent

    chain.reverse()
    return chain


def extract_messages(conv: Dict[str, Any], node_path: List[str]) -> List[MessageItem]:
    mapping = conv.get("mapping")
    if not isinstance(mapping, dict):
        return []

    conv_id = str(conv.get("conversation_id") or conv.get("id") or "")
    conv_title = str(conv.get("title") or "")

    out: List[MessageItem] = []
    for node_id in node_path:
        node = mapping.get(node_id)
        if not isinstance(node, dict):
            continue

        msg = node.get("message")
        if not isinstance(msg, dict):
            continue

        author = msg.get("author")
        role = author.get("role") if isinstance(author, dict) else None
        if role not in ("user", "assistant"):
            continue

        if message_is_hidden_or_toolish(msg):
            continue

        text = extract_text_from_content(msg.get("content"))
        if not text:
            continue

        # extra safeguard: exclude assistant tool-command blobs
        if role == "assistant" and looks_like_command_blob(text):
            continue

        out.append(
            MessageItem(
                conv_id=conv_id,
                conv_title=conv_title,
                node_id=str(node_id),
                msg_id=str(msg.get("id") or ""),
                role=str(role),
                create_time=msg.get("create_time"),
                text=text,
                raw_message=msg,
            )
        )

    return out


def pair_user_assistant(messages: List[MessageItem]) -> List[Tuple[MessageItem, MessageItem]]:
    """
    Robust pairing with tolerance for export timestamp quirks.

    Many exports have assistant.create_time slightly earlier than the paired user.create_time.
    We allow small negative deltas up to MAX_NEG_DELTA_SECONDS.

    We still skip assistants that are *way* earlier than the user.
    """
    MAX_NEG_DELTA_SECONDS = 120.0  # allow up to 2 minutes of skew

    pairs: List[Tuple[MessageItem, MessageItem]] = []
    pending_user: Optional[MessageItem] = None

    for m in messages:
        if m.role == "user":
            pending_user = m
            continue

        if m.role == "assistant":
            if pending_user is None:
                continue

            ut = pending_user.create_time
            at = m.create_time

            if ut is not None and at is not None:
                delta = float(at) - float(ut)
                if delta < -MAX_NEG_DELTA_SECONDS:
                    # Too far inverted to trust; skip and keep scanning
                    continue

            pairs.append((pending_user, m))
            pending_user = None

    return pairs

def stable_client_lui_id(conv_id: str, assistant_node_id: str) -> str:
    base = f"{conv_id}:{assistant_node_id}"
    h = hashlib.sha256(base.encode("utf-8")).hexdigest()[:16]
    return f"chatgpt:{base}:{h}"


def post_json(url: str, payload: Dict[str, Any], timeout_s: int = 30) -> Tuple[int, str]:
    try:
        import requests  # type: ignore

        r = requests.post(url, json=payload, timeout=timeout_s)
        txt = r.text
        if len(txt) > 500:
            txt = txt[:499] + "…"
        return (r.status_code, txt)
    except ModuleNotFoundError:
        import urllib.request

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                if len(body) > 500:
                    body = body[:499] + "…"
                return (resp.status, body)
        except Exception as ex:
            return (0, f"ERROR: {ex}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", required=True, help="Path to conversations.json")
    ap.add_argument("--title", default="", help="Only process conversations whose title contains this substring")
    ap.add_argument("--limit-conversations", type=int, default=0, help="Stop after N conversations (0 = no limit)")
    ap.add_argument("--limit-events", type=int, default=0, help="Stop after N spool events total (0 = no limit)")
    ap.add_argument("--dry-run", action="store_true", help="Do not POST; print summary + sample payloads")
    ap.add_argument("--emit-ndjson", default="", help="Write spool payloads to this NDJSON file instead of POSTing")
    ap.add_argument(
        "--spool-url",
        default=os.environ.get("IAM_SPOOL_URL", "http://localhost:8000/v1/spool"),
        help="Spooler endpoint URL (or set IAM_SPOOL_URL)",
    )
    ap.add_argument("--timeout", type=int, default=30)
    args = ap.parse_args()

    path = Path(args.path).expanduser().resolve()
    if not path.exists():
        eprint(f"FILE NOT FOUND: {path}")
        return 2

    eprint(f"Loading: {path} (large file; may take time)")
    data = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(data, list):
        eprint("Expected root list in conversations.json")
        return 2

    title_filter = args.title.lower().strip()
    conv_count = 0
    event_count = 0

    ndjson_fp = None
    if args.emit_ndjson:
        outp = Path(args.emit_ndjson).expanduser().resolve()
        outp.parent.mkdir(parents=True, exist_ok=True)
        ndjson_fp = outp.open("w", encoding="utf-8")
        eprint(f"Emitting NDJSON to: {outp}")

    try:
        for conv in data:
            if not isinstance(conv, dict):
                continue

            title = str(conv.get("title") or "")
            if title_filter and title_filter not in title.lower():
                continue

            conv_id = str(conv.get("conversation_id") or conv.get("id") or "")
            if not conv_id:
                continue

            node_path = linearize_main_branch(conv)
            if not node_path:
                continue

            msgs = extract_messages(conv, node_path)
            pairs = pair_user_assistant(msgs)

            conv_count += 1

            for (u, a) in pairs:
                payload: Dict[str, Any] = {
                    "client_lui_id": stable_client_lui_id(conv_id, a.node_id),
                    "timestamp": unix_to_iso8601_utc(a.create_time) or unix_to_iso8601_utc(u.create_time),
                    "message_raw": u.text,
                    "response_generated": a.text,
                    "source": {
                        "type": "chatgpt_export",
                        "conversation_id": conv_id,
                        "conversation_title": u.conv_title,
                        "user_node_id": u.node_id,
                        "assistant_node_id": a.node_id,
                        "user_message_id": u.msg_id,
                        "assistant_message_id": a.msg_id,
                        "chatgpt_create_time_user": u.create_time,
                        "chatgpt_create_time_assistant": a.create_time,
                    },
                }

                event_count += 1

                if args.dry_run:
                    print(f"[DRY] conv='{title}' event#{event_count} id={payload['client_lui_id']}")
                    if event_count <= 3:
                        print(json.dumps(payload, ensure_ascii=False, indent=2)[:4000])
                elif ndjson_fp is not None:
                    ndjson_fp.write(json.dumps(payload, ensure_ascii=False) + "\n")
                else:
                    status, resp = post_json(args.spool_url, payload, timeout_s=args.timeout)
                    print(f"[POST] {status} id={payload['client_lui_id']} conv='{title}' resp='{resp}'")

                if args.limit_events and event_count >= args.limit_events:
                    break

            if args.limit_events and event_count >= args.limit_events:
                break

            if args.limit_conversations and conv_count >= args.limit_conversations:
                break

        eprint(f"Done. Conversations processed: {conv_count}. Spool events: {event_count}.")
        return 0

    finally:
        if ndjson_fp is not None:
            ndjson_fp.close()


if __name__ == "__main__":
    raise SystemExit(main())