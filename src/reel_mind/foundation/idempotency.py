"""Idempotency helpers for deterministic pipeline run IDs."""

from __future__ import annotations

import hashlib
from datetime import datetime
from zoneinfo import ZoneInfo

from reel_mind.foundation.models import ChannelId, Pipeline

KST = ZoneInfo("Asia/Seoul")


def canonicalize_slot(slot: datetime) -> str:
    if slot.tzinfo is None:
        slot = slot.replace(tzinfo=KST)
    normalized = slot.astimezone(KST).replace(second=0, microsecond=0)
    return normalized.isoformat()


def run_id_for(
    channel_id: ChannelId,
    pipeline: Pipeline | str,
    scheduled_slot: datetime | None = None,
    idempotency_key: str | None = None,
) -> str:
    if scheduled_slot is None and idempotency_key is None:
        msg = "either scheduled_slot or idempotency_key is required"
        raise ValueError(msg)
    pipeline_value = pipeline.value if isinstance(pipeline, Pipeline) else pipeline
    slot_part = canonicalize_slot(scheduled_slot) if scheduled_slot else f"key:{idempotency_key}"
    raw = f"{channel_id}|{pipeline_value}|{slot_part}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]  # noqa: S324
