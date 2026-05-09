from datetime import UTC, datetime

import pytest

from reel_mind.foundation import Pipeline, canonicalize_slot, run_id_for


def test_canonicalize_slot_uses_kst_minute_precision() -> None:
    slot = datetime(2026, 5, 9, 23, 1, 45, tzinfo=UTC)

    assert canonicalize_slot(slot) == "2026-05-10T08:01:00+09:00"


def test_run_id_for_is_deterministic() -> None:
    slot = datetime.fromisoformat("2026-05-10T09:00:00+09:00")

    first = run_id_for("ko-shorts-tech", Pipeline.B, scheduled_slot=slot)
    second = run_id_for("ko-shorts-tech", "B", scheduled_slot=slot)

    assert first == second
    assert len(first) == 24


def test_run_id_for_requires_slot_or_key() -> None:
    with pytest.raises(ValueError, match="scheduled_slot or idempotency_key"):
        run_id_for("ko-shorts-tech", Pipeline.B)
