from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _log_path() -> Path:
    p = os.environ.get("INGEST_LOG_PATH", "ingest_log.jsonl")
    return Path(p).expanduser().resolve()


app = FastAPI(
    title="IAM Ingest Server v0 (logger)",
    version="0.1",
    description="Minimal dev ingest sink: accepts LUIs at POST /v1/luis and logs JSONL.",
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/luis")
async def ingest_lui(request: Request):
    try:
        envelope = await request.json()
        if not isinstance(envelope, dict):
            raise ValueError("JSON object required")
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"error": {"code": "INVALID_JSON", "message": "Request must be a JSON object"}},
        )

    received_at = _utc_now_iso()

    record: Dict[str, Any] = {
        "received_at": received_at,
        "client_lui_id": envelope.get("client_lui_id"),
        "captured_at": envelope.get("captured_at"),
        "kind": envelope.get("kind"),
        "source": envelope.get("source"),
        "privacy": envelope.get("privacy"),
        "payload_keys": sorted(list(envelope.get("payload", {}).keys()))
        if isinstance(envelope.get("payload"), dict)
        else [],
        "envelope": envelope,
    }

    lp = _log_path()
    lp.parent.mkdir(parents=True, exist_ok=True)
    with lp.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print("📥 INGEST RECEIVED:", {"client_lui_id": record["client_lui_id"], "kind": record["kind"], "received_at": received_at})
    return {"status": "ok", "received_at": received_at, "client_lui_id": record["client_lui_id"]}