"""Pipeline run and stage lifecycle recording."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from typing import Any, Protocol

from ulid import ULID

from reel_mind.foundation.errors import IdempotencyConflict
from reel_mind.foundation.idempotency import run_id_for
from reel_mind.foundation.models import (
    ArtifactRef,
    ChannelId,
    ErrorRecord,
    Pipeline,
    PipelineRun,
    RunState,
    StageRecord,
    StageStatus,
    Trigger,
)


class RunStore(Protocol):
    def insert(self, table: str, row: dict[str, Any]) -> dict[str, Any]: ...

    def update_where(
        self,
        table: str,
        *,
        eq: dict[str, Any],
        set_: dict[str, Any],
        returning: bool = True,
    ) -> list[dict[str, Any]]: ...


class RunRecorder:
    def __init__(self, store: RunStore) -> None:
        self._store = store

    def start_run(
        self,
        *,
        channel_id: ChannelId,
        pipeline: Pipeline,
        trigger: Trigger,
        scheduled_slot: datetime | None = None,
        force_retry_of: str | None = None,
        config_version_hash: str | None = None,
    ) -> PipelineRun:
        run_id = self._new_run_id(
            channel_id=channel_id,
            pipeline=pipeline,
            scheduled_slot=scheduled_slot,
            force_retry_of=force_retry_of,
        )
        run = PipelineRun(
            run_id=run_id,
            channel_id=channel_id,
            pipeline=pipeline,
            scheduled_slot=scheduled_slot.isoformat() if scheduled_slot else None,
            trigger=trigger,
            state=RunState.STARTED,
            started_at=datetime.now(UTC),
            force_retry_of=force_retry_of,
            config_version_hash=config_version_hash,
        )
        self._store.insert("pipeline_runs", run.model_dump(mode="json"))
        return run

    def record_stage(
        self,
        *,
        run_id: str,
        stage_name: str,
        sequence: int,
        status: StageStatus,
        artifacts: Sequence[ArtifactRef] = (),
        attempt: int = 1,
        error: ErrorRecord | None = None,
        started_at: datetime | None = None,
        finished_at: datetime | None = None,
    ) -> StageRecord:
        record = StageRecord(
            run_id=run_id,
            stage_name=stage_name,
            sequence=sequence,
            status=status,
            attempt=attempt,
            started_at=started_at or datetime.now(UTC),
            finished_at=finished_at,
            artifacts=tuple(artifacts),
            error=error,
        )
        self._store.insert("stage_records", record.model_dump(mode="json"))
        return record

    def finish_run(self, run_id: str, state: RunState, outcome: str | None = None) -> PipelineRun:
        if state is RunState.STARTED:
            msg = "finish_run requires a terminal state"
            raise ValueError(msg)
        updates: Mapping[str, Any] = {
            "state": state.value,
            "finished_at": datetime.now(UTC).isoformat(),
            "outcome": outcome,
        }
        rows = self._store.update_where(
            "pipeline_runs",
            eq={"run_id": run_id, "state": RunState.STARTED.value},
            set_=dict(updates),
        )
        if not rows:
            raise IdempotencyConflict(run_id)
        return _pipeline_run_from_row(rows[0])

    def _new_run_id(
        self,
        *,
        channel_id: ChannelId,
        pipeline: Pipeline,
        scheduled_slot: datetime | None,
        force_retry_of: str | None,
    ) -> str:
        if force_retry_of is not None:
            return f"{pipeline.value.lower()}-{ULID()}"
        if scheduled_slot is not None:
            return run_id_for(channel_id, pipeline, scheduled_slot=scheduled_slot)
        return f"{pipeline.value.lower()}-{ULID()}"


def _pipeline_run_from_row(row: Mapping[str, Any]) -> PipelineRun:
    normalized = dict(row)
    normalized["pipeline"] = Pipeline(normalized["pipeline"])
    normalized["trigger"] = Trigger(normalized["trigger"])
    normalized["state"] = RunState(normalized["state"])
    for key in ("started_at", "finished_at"):
        if isinstance(normalized.get(key), str):
            normalized[key] = datetime.fromisoformat(normalized[key].replace("Z", "+00:00"))
    return PipelineRun.model_validate(normalized)
