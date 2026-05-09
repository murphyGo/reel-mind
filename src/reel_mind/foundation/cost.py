"""Cost ledger accounting."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any, Protocol

from ulid import ULID

from reel_mind.foundation.models import ChannelId, CostBucket, LedgerEntry, Pipeline


class CostStore(Protocol):
    def insert(self, table: str, row: dict[str, Any]) -> dict[str, Any]: ...

    def aggregate_sum(self, table: str, *, column: str, eq: dict[str, Any]) -> Decimal: ...


class CostLedger:
    def __init__(self, store: CostStore) -> None:
        self._store = store

    def record(
        self,
        *,
        channel_id: ChannelId,
        pipeline: Pipeline,
        run_id: str,
        provider: str,
        bucket: CostBucket,
        units: Decimal,
        unit_kind: str,
        usd_cost: Decimal,
        metadata: Mapping[str, Any] | None = None,
    ) -> LedgerEntry:
        entry = LedgerEntry(
            entry_id=str(ULID()),
            timestamp=datetime.now(UTC),
            channel_id=channel_id,
            pipeline=pipeline,
            run_id=run_id,
            provider=provider,
            bucket=bucket,
            units=units,
            unit_kind=unit_kind,
            usd_cost=usd_cost,
            metadata=dict(metadata or {}),
        )
        self._store.insert("cost_ledger", entry.model_dump(mode="json"))
        return entry

    def month_spend_all_providers(self, channel_id: ChannelId, month: date) -> Decimal:
        return self._store.aggregate_sum(
            "cost_ledger",
            column="usd_cost",
            eq={"channel_id": channel_id, "month_bucket": month.isoformat()},
        )

    def remaining_budget(self, channel_id: ChannelId, cap_usd: Decimal, month: date) -> Decimal:
        spent = self.month_spend_all_providers(channel_id, month)
        return max(Decimal("0"), cap_usd - spent)
