# services/spooler_v0/app.py

from __future__ import annotations

import os

from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from .adapters.openai_actions.gpt_handler import router as openai_actions_router

from .config import load_config
from .drain import drain_once
from .lui_normalize import canonical_json, normalize_any_rest_payload_to_lui
from .outbox import CapacityError, ConflictError, OutboxError, enqueue, init_outbox, queued_count

cfg = load_config()
init_outbox(cfg.outbox_db_path)

app = FastAPI(
	title="IAM Spooler v0",
	version="0.1",
	description=(
		"Durable, replay-safe outbox intake boundary for IAM.\n\n"
		"Primary action endpoint: POST /v1/spool\n"
		"- Requires a stable idempotency key: client_lui_id\n"
		"- Persists durably before acknowledging (200)\n"
		"- Returns 409 for conflicting replay, 507 for capacity exceeded\n\n"
		"FastAPI publishes the OpenAPI schema at /openapi.json."
	),
)

# --- Include GPT Actions adapter routes (e.g., POST /spool) ---
# Keep paths exactly as your GPT Action schema expects.
app.include_router(openai_actions_router, tags=["actions"])


def _custom_openapi():
    """Generate OpenAPI schema without injecting servers.

    This keeps the schema stable across changing ngrok hosts.
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


# Override the default OpenAPI generator
app.openapi = _custom_openapi  # type: ignore[assignment]


# Stable alias endpoint some GPT configs prefer
@app.get("/openai.json", include_in_schema=False)
def openai_json():
	return JSONResponse(app.openapi())


@app.get(
	"/health",
	summary="Liveness check",
	description="Returns ok if the spooler process is running.",
	operation_id="health_check",
	tags=["internal"],
)
def health():
	return {"status": "ok"}


@app.get(
	"/v1/status",
	summary="Outbox queued counts",
	description="Returns observable queued counts (queued items only). Does not mutate state.",
	operation_id="outbox_status",
	tags=["internal"],
)
def status():
	return {"queued": queued_count(cfg.outbox_db_path)}


@app.post(
	"/v1/spool",
	summary="Durably enqueue an IAM LUI envelope (Action endpoint)",
	description=(
		"Use this endpoint to persist a Language-Use Input (LUI) envelope into the durable outbox.\n\n"
		"Contract (4a): client_lui_id is required for replay safety.\n"
		"- 200: accepted and durably persisted\n"
		"- 400: invalid JSON or missing/invalid LUI (including missing client_lui_id)\n"
		"- 409: conflicting replay for the same client_lui_id\n"
		"- 413: request exceeds max_request_bytes\n"
		"- 507: outbox capacity exceeded\n\n"
		"Notes:\n"
		"- Payload shape may be arbitrary JSON, but MUST include client_lui_id.\n"
		"- The spooler normalizes input into an LUI envelope and stores a canonical JSON form.\n"
	),
	operation_id="iam_spool_lui",
	tags=["actions"],
	openapi_extra={
		"requestBody": {
			"required": True,
			"content": {
				"application/json": {
					"schema": {
						"type": "object",
						"required": ["client_lui_id"],
						"properties": {
							"client_lui_id": {
								"type": "string",
								"description": "Required idempotency key for replay-safe enqueue.",
							},
							"captured_at": {
								"type": "string",
								"description": "Optional capture timestamp. If omitted, normalization may assign one.",
							},
							"source": {
								"type": "object",
								"description": "Optional source descriptor; preserved or assigned during normalization.",
								"additionalProperties": True,
							},
							"kind": {
								"type": "string",
								"description": "Optional kind. If omitted, normalization assigns a default.",
							},
							"payload": {
								"type": "object",
								"description": "Arbitrary payload object to persist. The spooler does not interpret meaning.",
								"additionalProperties": True,
							},
							"privacy": {
								"type": "object",
								"description": "Optional privacy controls for payload handling.",
								"additionalProperties": True,
							},
						},
						"additionalProperties": True,
					},
					"examples": {
						"chatgpt_action_example": {
							"summary": "Example suitable for ChatGPT Actions",
							"value": {
								"client_lui_id": "chatgpt:conv123:turn17",
								"captured_at": "2026-01-17T19:42:01Z",
								"source": {
									"client": "chatgpt",
									"agent": "chatgpt-actions",
									"conversation_id": "conv123",
								},
								"kind": "message",
								"payload": {"text": "iam: save this note"},
								"privacy": {"payload_mode": "plaintext"},
							},
						}
					},
				}
			},
		},
		"responses": {
			"200": {"description": "Accepted and durably persisted"},
			"400": {"description": "Invalid JSON or missing/invalid LUI (including missing client_lui_id)"},
			"409": {"description": "Conflicting replay for client_lui_id"},
			"413": {"description": "Request exceeds max_request_bytes"},
			"507": {"description": "Outbox capacity exceeded"},
		},
	},
)
async def spool(request: Request):
	raw = await request.body()
	if len(raw) > cfg.max_request_bytes:
		return JSONResponse(
			status_code=413,
			content={"error": {"code": "REQUEST_TOO_LARGE", "message": "max_request_bytes exceeded"}},
		)

	try:
		payload = await request.json()
		if not isinstance(payload, dict):
			raise ValueError("JSON object required")
	except Exception:
		return JSONResponse(
			status_code=400,
			content={"error": {"code": "INVALID_JSON", "message": "Request must be a JSON object"}},
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
		return JSONResponse(status_code=507, content={"error": {"code": "OUTBOX_CAPACITY", "message": str(e)}})
	except ConflictError as e:
		return JSONResponse(status_code=409, content={"error": {"code": "CONFLICT", "message": str(e)}})
	except (ValueError, OutboxError) as e:
		return JSONResponse(status_code=400, content={"error": {"code": "INVALID_LUI", "message": str(e)}})


@app.post(
	"/v1/drain",
	summary="Attempt drain to ingest server",
	description=(
		"Attempts delivery of queued outbox items to the configured INGEST_URL.\n"
		"Safe to call repeatedly; failures do not drop queued items."
	),
	operation_id="outbox_drain_once",
	tags=["internal"],
)
def drain():
	res = drain_once(
		db_path=cfg.outbox_db_path,
		ingest_url=cfg.ingest_url,
		batch_size=cfg.drain_batch_size,
		timeout_seconds=cfg.drain_timeout_seconds,
	)
	return {"attempted": res.attempted, "acked": res.acked, "failed": res.failed, "conflicts": res.conflicts}