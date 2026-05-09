from datetime import date
from decimal import Decimal
from typing import Any

from reel_mind.foundation import CostBucket, CostLedger, Pipeline


class FakeCostStore:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def insert(self, table: str, row: dict[str, Any]) -> dict[str, Any]:
        assert table == "cost_ledger"
        self.rows.append(row)
        return row

    def aggregate_sum(self, table: str, *, column: str, eq: dict[str, Any]) -> Decimal:
        assert table == "cost_ledger"
        return sum(
            Decimal(str(row[column]))
            for row in self.rows
            if row["channel_id"] == eq["channel_id"]
        )


def test_cost_ledger_records_append_only_entry() -> None:
    store = FakeCostStore()
    ledger = CostLedger(store)

    entry = ledger.record(
        channel_id="ko-shorts-tech",
        pipeline=Pipeline.B,
        run_id="run-1",
        provider="anthropic",
        bucket=CostBucket.CLAUDE,
        units=Decimal("100"),
        unit_kind="tokens",
        usd_cost=Decimal("0.012345"),
        metadata={"model": "claude"},
    )

    assert len(entry.entry_id) == 26
    assert store.rows[0]["metadata"] == {"model": "claude"}


def test_remaining_budget_never_goes_negative() -> None:
    store = FakeCostStore()
    ledger = CostLedger(store)
    ledger.record(
        channel_id="ko-shorts-tech",
        pipeline=Pipeline.B,
        run_id="run-1",
        provider="anthropic",
        bucket=CostBucket.CLAUDE,
        units=Decimal("1"),
        unit_kind="call",
        usd_cost=Decimal("25.00"),
    )

    remaining = ledger.remaining_budget("ko-shorts-tech", Decimal("20.00"), date(2026, 5, 1))

    assert remaining == Decimal("0")
