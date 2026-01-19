from __future__ import annotations

import os
from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from .config import load_config
from .drain import drain_once
from .lui_normalize import canonical_json, normalize_any_rest_payload_to_lui
from .outbox import (
    CapacityError,
    ConflictError,
    OutboxError,
    enqueue,
    init_outbox,
    queued_count,
)

from .adapters.openai_actions.gpt_handler import router as openai_actions_router


# -----------------------------------------------------------------------------
# App initialization
# -----------------------------------------------------------------------------

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


# -----------------------------------------------------------------------------
# Routers (adapters)
# -----------------------------------------------------------------------------

# GPT Actions adapter (POST /spool)
app.include_router(openai_actions_router, tags=["actions"])


# -----------------------------------------------------------------------------
# OpenAPI handling
# -----------------------------------------------------------------------------

def _custom_openapi():
    """
    Generate OpenAPI schema without injecting servers.

    Base URL is inferred from the request origin (ngrok / proxy friendly).
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
    schema = app.openapi()

    # Prefer proxy headers (ngrok sets these)
    proto = request.headers.get("x-forwarded-proto") or request.url.scheme or "https"
    host = request.headers.get("x-forwarded-host") or request.headers.get("host")

    if host:
        base_url = f"{proto}://{host}".rstrip("/")
    else:
        base_url = str(request.base_url).rstrip("/")

    schema["servers"] = [{"url": base_url}]
    return JSONResponse(schema)


# -----------------------------------------------------------------------------
# Health & observability
# -----------------------------------------------------------------------------

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


# -----------------------------------------------------------------------------
# Canonical intake (HIDDEN from GPT Actions)
# -----------------------------------------------------------------------------

@app.post(
    "/v1/spool",
    include_in_schema=False,
    summary="Durably enqueue an IAM LUI envelope",
    description=(
        "Canonical intake endpoint.\n\n"
        "Requires a stable idempotency key (client_lui_id).\n"
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


# -----------------------------------------------------------------------------
# Drain
# -----------------------------------------------------------------------------

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