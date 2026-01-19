from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ...config import load_config
from ...lui_normalize import canonical_json, normalize_any_rest_payload_to_lui
from ...outbox import CapacityError, ConflictError, OutboxError, enqueue

router = APIRouter()


class IAMPayload(BaseModel):
    # GPT Actions payload (adapter plane)
    message_raw: str
    response_generated: str
    timestamp: datetime  # required by schema (date-time)


def _stable_client_lui_id(payload: IAMPayload) -> str:
    """
    Deterministic idempotency key derived from the incoming payload.

    If the GPT Action retries the same call, this ID remains stable, enabling
    replay safety at the outbox boundary.
    """
    # Normalize timestamp to an ISO string with timezone
    ts = payload.timestamp
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)

    material = canonical_json(
        {
            "message_raw": payload.message_raw,
            "response_generated": payload.response_generated,
            "timestamp": ts.isoformat(),
        }
    )
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()
    return f"gpt:{digest}"


@router.post("/spool")
async def spool(payload: IAMPayload):
    cfg = load_config()

    # Ensure timestamp is timezone-aware for consistent downstream handling
    ts = payload.timestamp
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)

    client_lui_id = _stable_client_lui_id(payload)

    # Build a canonical LUI envelope for the spooler boundary
    envelope_in: Dict[str, Any] = {
        "client_lui_id": client_lui_id,
        "captured_at": ts.isoformat(),
        "source": {
            "client": "chatgpt",
            "agent": "gpt-actions",
            "transport": "openai_actions",
        },
        "kind": "gpt_action",
        "payload": {
            "message_raw": payload.message_raw,
            "response_generated": payload.response_generated,
            "timestamp": ts.isoformat(),
        },
        "privacy": {"payload_mode": "plaintext"},
    }

    try:
        lui = normalize_any_rest_payload_to_lui(envelope_in)
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

        return jsonable_encoder(
            {
                "status": "queued",
                "client_lui_id": client_lui_id,
            }
        )

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