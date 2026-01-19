from __future__ import annotations

import json
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from .adapters.openai_actions.gpt_handler import router as openai_actions_router
from .config import load_config
from .drain import drain_once
from .lui_normalize import canonical_json, normalize_any_rest_payload_to_lui
from .outbox import (
    CapacityError,
    ConflictError,
    OutboxError,
    enqueue,
    init_outbox,
    peek_queued,
    queued_count,
)

# ------------------------------------------------------------------------------
# Init
# ------------------------------------------------------------------------------

cfg = load_config()
init_outbox(cfg.outbox_db_path)

app = FastAPI(
    title="IAM Spooler v0",
    version="0.1",
    description=(
        "Durable, replay-safe outbox intake boundary for IAM.\n\n"
        "Primary canonical intake: POST /v1/spool\n"
        "- Requires stable idempotency key: client_lui_id\n"
        "- Persists durably before acknowledging\n"
        "- Downstream ingest may be unavailable\n\n"
        "Adapter endpoints (e.g. GPT Actions) converge to this intake."
    ),
)

# Adapter plane (GPT Actions)
app.include_router(openai_actions_router, tags=["actions"])

# ------------------------------------------------------------------------------
# OpenAPI handling (stable + GPT-friendly)
# ------------------------------------------------------------------------------

def _custom_openapi():
    """
    Generate OpenAPI schema WITHOUT baked-in servers.
    servers[] will be injected dynamically by /openai.json.
    """
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    app.openapi_schema = schema
    return schema


app.openapi = _custom_openapi  # type: ignore[assignment]


@app.get("/openai.json", include_in_schema=False)
def openai_json(request: Request):
    """
    OpenAPI document endpoint for GPT Actions import.

    Injects a valid servers[0].url derived from the incoming request
    (ngrok, reverse proxy, local dev, etc.).
    """
    schema = app.openapi()

    proto = request.headers.get("x-forwarded-proto") or request.url.scheme or "https"
    host = request.headers.get("x-forwarded-host") or request.headers.get("host")

    if host:
        base_url = f"{proto}://{host}".rstrip("/")
    else:
        base_url = str(request.base_url).rstrip("/")

    schema["servers"] = [{"url": base_url}]
    return JSONResponse(schema)

# ------------------------------------------------------------------------------
# Internal / operational endpoints
# ------------------------------------------------------------------------------

@app.get(
    "/health",
    summary="Liveness check",
    description="Returns ok if the spooler process is running.",
    tags=["internal"],
)
def health():
    return {"status": "ok"}


@app.get(
    "/v1/status",
    summary="Outbox queued counts",
    description="Returns observable queued counts (queued items only).",
    tags=["internal"],
)
def status():
    return {"queued": queued_count(cfg.outbox_db_path)}


def _summarize_envelope(envelope: Dict[str, Any], *, max_text: int = 400) -> Dict[str, Any]:
    source = envelope.get("source") if isinstance(envelope.get("source"), dict) else {}
    payload = envelope.get("payload") if isinstance(envelope.get("payload"), dict) else {}

    text: Optional[str] = None
    if isinstance(payload.get("text"), str):
        text = payload["text"]
    elif isinstance(payload.get("message_raw"), str):
        text = payload["message_raw"]

    if text is not None and len(text) > max_text:
        text = text[: max_text - 3] + "..."

    return {
        "captured_at": envelope.get("captured_at"),
        "kind": envelope.get("kind"),
        "source_client": source.get("client"),
        "source_agent": source.get("agent"),
        "payload_keys": sorted(list(payload.keys())) if isinstance(payload, dict) else [],
        "payload_text_preview": text,
    }


@app.get(
    "/v1/peek",
    include_in_schema=False,
    summary="Peek queued outbox items (read-only)",
    description="Read-only inspection of queued outbox items. Does not mutate state.",
    tags=["internal"],
)
def peek(limit: int = 10, offset: int = 0, full: bool = False):
    rows = peek_queued(cfg.outbox_db_path, limit=limit, offset=offset)

    items = []
    for r in rows:
        try:
            env = json.loads(r["envelope_json"])
        except Exception:
            env = None

        item = {
            "id": r["id"],
            "client_lui_id": r["client_lui_id"],
            "envelope_bytes": r["envelope_bytes"],
            "created_at": r["created_at"],
            "attempt_count": r["attempt_count"],
            "last_attempt_at": r["last_attempt_at"],
            "last_error": r["last_error"],
        }

        if isinstance(env, dict):
            item["summary"] = _summarize_envelope(env)
            if full:
                item["envelope"] = env
                item["envelope_json"] = r["envelope_json"]
        else:
            item["summary"] = {"parse_error": True}
            if full:
                item["envelope_json"] = r["envelope_json"]

        items.append(item)

    return {
        "count": len(items),
        "limit": limit,
        "offset": offset,
        "items": items,
    }

# ------------------------------------------------------------------------------
# Canonical intake (non-adapter)
# ------------------------------------------------------------------------------

@app.post(
    "/v1/spool",
    include_in_schema=False,
    summary="Durably enqueue an IAM LUI envelope",
    description=(
        "Canonical intake endpoint.\n\n"
        "Requires stable idempotency key (client_lui_id).\n"
        "Persists before acknowledgment.\n"
        "Replay-safe and capacity-aware."
    ),
    tags=["internal"],
)
async def spool(request: Request):
    raw = await request.body()
    if len(raw) > cfg.max_request_bytes:
        return JSONResponse(
            status_code=413,
            content={"error": {"code": "REQUEST_TOO_LARGE"}},
        )

    try:
        payload = await request.json()
        if not isinstance(payload, dict):
            raise ValueError("JSON object required")
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"error": {"code": "INVALID_JSON"}},
        )

    try:
        lui = normalize_any_rest_payload_to_lui(payload)
        envelope_json = canonical_json(lui)
        envelope_bytes = len(envelope_json.encode("utf-8"))

        enqueue(
            cfg.outbox_db_path,
            envelope=lui,
            envelope_json=envelope_json,
            envelope_bytes=envelope_bytes,
            max_envelope_bytes=cfg.max_envelope_bytes,
            outbox_max_items=cfg.outbox_max_items,
            outbox_max_bytes=cfg.outbox_max_bytes,
        )

        return {"status": "queued", "client_lui_id": lui.get("client_lui_id")}

    except CapacityError as e:
        return JSONResponse(
            status_code=507,
            content={"error": {"code": "OUTBOX_CAPACITY", "message": str(e)}},
        )
    except ConflictError as e:
        return JSONResponse(
            status_code=409,
            content={"error": {"code": "CONFLICT", "message": str(e)}},
        )
    except (ValueError, OutboxError) as e:
        return JSONResponse(
            status_code=400,
            content={"error": {"code": "INVALID_LUI", "message": str(e)}},
        )

# ------------------------------------------------------------------------------
# Drain
# ------------------------------------------------------------------------------

@app.post(
    "/v1/drain",
    summary="Attempt drain to ingest server",
    description=(
        "Attempts delivery of queued outbox items to the configured INGEST_URL.\n"
        "Safe to call repeatedly; failures do not drop queued items."
    ),
    tags=["internal"],
)
def drain():
    res = drain_once(
        db_path=cfg.outbox_db_path,
        ingest_url=cfg.ingest_url,
        batch_size=cfg.drain_batch_size,
        timeout_seconds=cfg.drain_timeout_seconds,
    )
    return {
        "attempted": res.attempted,
        "acked": res.acked,
        "failed": res.failed,
        "conflicts": res.conflicts,
    }