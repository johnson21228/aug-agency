# services/spooler_v0/lui_normalize.py

from __future__ import annotations

import json
from typing import Any, Dict


def canonical_json(obj: Any) -> str:
	return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def normalize_any_rest_payload_to_lui(payload: Dict[str, Any]) -> Dict[str, Any]:
	"""
	v0 rule:
	- If it already looks like an LUI envelope (client_lui_id, captured_at, source, kind), accept as-is.
	- Otherwise wrap as a minimal event LUI.
	The spooler still requires client_lui_id.
	"""
	required = {"client_lui_id", "captured_at", "source", "kind"}
	if required.issubset(payload.keys()):
		return payload

	if "client_lui_id" not in payload:
		raise ValueError("client_lui_id required for spooler intake")

	return {
		"client_lui_id": payload["client_lui_id"],
		"captured_at": payload.get("captured_at") or payload.get("ts") or payload.get("timestamp") or "1970-01-01T00:00:00Z",
		"source": payload.get("source") or {"client": "unknown", "device_id": "unknown"},
		"kind": payload.get("kind") or "event",
		"title": payload.get("title"),
		"notes": payload.get("notes"),
		"tags": payload.get("tags"),
		"collection_ids": payload.get("collection_ids"),
		"favorite": payload.get("favorite"),
		"payload": payload.get("payload") or {"text": payload.get("text"), "json": payload},
		"privacy": payload.get("privacy") or {"payload_mode": "plaintext"},
	}
