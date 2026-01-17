# services/spooler_v0/drain.py

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import requests

from .outbox import OutboxItem, ack, fetch_batch, mark_attempt


@dataclass(frozen=True)
class DrainResult:
    attempted: int
    acked: int
    failed: int
    conflicts: int


def _post(ingest_url: str, envelope_json: str, timeout_seconds: int) -> Tuple[int, str]:
    r = requests.post(
        ingest_url,
        data=envelope_json.encode("utf-8"),
        headers={"Content-Type": "application/json"},
        timeout=timeout_seconds,
    )
    return r.status_code, r.text


def drain_once(*, db_path, ingest_url: str, batch_size: int, timeout_seconds: int) -> DrainResult:
    batch: List[OutboxItem] = fetch_batch(db_path, batch_size)
    if not batch:
        return DrainResult(attempted=0, acked=0, failed=0, conflicts=0)

    ids = [it.id for it in batch]
    mark_attempt(db_path, ids, err=None)

    ack_ids: List[int] = []
    failed = 0
    conflicts = 0

    for it in batch:
        try:
            code, body = _post(ingest_url, it.envelope_json, timeout_seconds)
        except Exception as e:
            failed += 1
            mark_attempt(db_path, [it.id], err=str(e))
            continue

        if 200 <= code < 300:
            ack_ids.append(it.id)
        elif code == 409:
            conflicts += 1
            mark_attempt(db_path, [it.id], err=f"conflict:{body[:200]}")
            break
        else:
            failed += 1
            mark_attempt(db_path, [it.id], err=f"http:{code}:{body[:200]}")

    acked = ack(db_path, ack_ids)
    return DrainResult(attempted=len(batch), acked=acked, failed=failed, conflicts=conflicts)
