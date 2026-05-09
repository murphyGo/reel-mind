from datetime import UTC, datetime

from hypothesis import given
from hypothesis import strategies as st

from reel_mind.foundation import canonicalize_slot, run_id_for


@given(st.datetimes(timezones=st.just(UTC)))
def test_canonicalize_slot_is_idempotent(slot: datetime) -> None:
    canonical = canonicalize_slot(slot)

    assert canonicalize_slot(datetime.fromisoformat(canonical)) == canonical


@given(st.text(min_size=1, max_size=32, alphabet=st.characters(whitelist_categories=("Ll", "Nd"))))
def test_run_id_for_is_stable_for_idempotency_key(key: str) -> None:
    first = run_id_for("ko-shorts-tech", "B", idempotency_key=key)
    second = run_id_for("ko-shorts-tech", "B", idempotency_key=key)

    assert first == second
    assert len(first) == 24
