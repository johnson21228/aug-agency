from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import requests


def utc_iso_from_epoch(seconds: float) -> str:
    return datetime.fromtimestamp(seconds, tz=timezone.utc).isoformat()


def stable_client_lui_id(conversation_id: str, message_id: str) -> str:
    return f"chatgpt:{conversation_id}:{message_id}"


def extract_text(message_obj: Dict[str, Any]) -> str:
    """
    Best-effort extraction for common export shapes:
    - message.content.parts: list[str]
    - message.content.text: str
    - message.text: str
    """
    content = message_obj.get("content") or {}
    if isinstance(content, dict):
        parts = content.get("parts")
        if isinstance(parts, list):
            return "\n".join([p for p in parts if isinstance(p, str)]).strip()
        txt = content.get("text")
        if isinstance(txt, str):
            return txt.strip()
    txt2 = message_obj.get("text")
    if isinstance(txt2, str):
        return txt2.strip()
    return ""


def iter_export_messages(export_json: Any) -> Iterable[Dict[str, Any]]:
    """
    Accept either:
    - a list of conversations
    - a dict with "conversations"
    Each conversation contains messages in some nested structure.
    """
    conversations = export_json
    if isinstance(export_json, dict) and "conversations" in export_json:
        conversations = export_json["conversations"]

    if not isinstance(conversations, list):
        return

    for conv in conversations:
        if not isinstance(conv, dict):
            continue
        conv_id = str(conv.get("id") or conv.get("conversation_id") or "")
        if not conv_id:
            continue

        # Common shapes: conv["mapping"] dict of node_id -> {message: {...}}
        mapping = conv.get("mapping")
        if isinstance(mapping, dict):
            for _, node in mapping.items():
                if not isinstance(node, dict):
                    continue
                msg = node.get("message")
                if isinstance(msg, dict):
                    msg["_conversation_id"] = conv_id
                    yield msg
            continue

        # Or conv["messages"] list
        msgs = conv.get("messages")
        if isinstance(msgs, list):
            for msg in msgs:
                if isinstance(msg, dict):
                    msg["_conversation_id"] = conv_id
                    yield msg


def to_lui_envelope(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    conv_id = str(msg.get("_conversation_id") or "")
    msg_id = str(msg.get("id") or msg.get("message_id") or "")
    if not conv_id or not msg_id:
        return None

    author = msg.get("author") or {}
    role = ""
    if isinstance(author, dict):
        role = str(author.get("role") or "")
    if not role:
        role = str(msg.get("role") or "")

    create_time = msg.get("create_time")
    captured_at = None
    if isinstance(create_time, (int, float)):
        captured_at = utc_iso_from_epoch(float(create_time))
    else:
        # fallback: now (still deterministic within one run is not guaranteed; avoid if possible)
        captured_at = datetime.now(timezone.utc).isoformat()

    text = extract_text(msg)
    client_lui_id = stable_client_lui_id(conv_id, msg_id)

    return {
        "client_lui_id": client_lui_id,
        "captured_at": captured_at,
        "source": {
            "client": "chatgpt",
            "transport": "chatgpt_export",
            "conversation_id": conv_id,
            "message_id": msg_id,
            "role": role,
        },
        "kind": "chatgpt.turn",
        "payload": {
            "text": text,
            "role": role,
            "conversation_id": conv_id,
            "message_id": msg_id,
        },
        "privacy": {"payload_mode": "plaintext"},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Convert ChatGPT export to LUIs and post to spooler.")
    ap.add_argument("export_json", type=Path, help="Path to ChatGPT export JSON (or conversations.json).")
    ap.add_argument("--spooler", default="http://127.0.0.1:8000/v1/spool", help="Spooler canonical intake URL.")
    ap.add_argument("--dry-run", action="store_true", help="Do not POST; print envelopes as JSONL.")
    ap.add_argument("--limit", type=int, default=0, help="Limit number of messages (0 = no limit).")
    args = ap.parse_args()

    data = json.loads(args.export_json.read_text(encoding="utf-8"))
    count = 0

    for msg in iter_export_messages(data):
        env = to_lui_envelope(msg)
        if env is None:
            continue

        if args.dry_run:
            print(json.dumps(env, ensure_ascii=False))
        else:
            r = requests.post(args.spooler, json=env, timeout=30)
            if r.status_code not in (200, 201):
                print(f"ERROR {r.status_code}: {r.text}", file=sys.stderr)
            else:
                # print minimal ack
                try:
                    print(r.json())
                except Exception:
                    print(r.text)

        count += 1
        if args.limit and count >= args.limit:
            break

    return 0


if __name__ == "__main__":
    raise SystemExit(main())