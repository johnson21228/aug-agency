from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

router = APIRouter()


# --- Updated payload model ---
class IAMPayload(BaseModel):
    message_raw: str               # the iam... message (prompt)
    response_generated: str        # the assistant's current reply
    timestamp: datetime            # UTC timestamp when sent


@router.post("/spool")
async def spool(payload: IAMPayload):
    log_entry = {
        "message_raw": payload.message_raw,
        "response_generated": payload.response_generated,
        "timestamp": payload.timestamp.isoformat(),
    }

    print("📥 Received from GPT:", log_entry)

    return jsonable_encoder(
        {
            "status": "success",
            "message": "✅ Current prompt and response logged successfully.",
            "echo": log_entry,
        }
    )