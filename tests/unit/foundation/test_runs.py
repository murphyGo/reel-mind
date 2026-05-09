from datetime import UTC, datetime
from typing import Any

import pytest

from reel_mind.foundation import Pipeline, RunRecorder, RunState, StageStatus, Trigger
from reel_mind.foundation.errors import IdempotencyConflict


class FakeRunStore:
    def __init__(self) -> None:
        self.tables: dict[str, list[dict[str, Any]]] = {
            "pipeline_runs": [],
            "stage_records": [],
        }

    def insert(self, table: str, row: dict[str, Any]) -> dict[str, Any]:
        self.tables[table].append(row)
        return row

    def update_where(
        self,
        table: str,
        *,
        eq: dict[str, Any],
        set_: dict[str, Any],
        returning: bool = True,
    ) -> list[dict[str, Any]]:
        updated: list[dict[str, Any]] = []
        for row in self.tables[table]:
            if all(row.get(key) == value for key, value in eq.items()):
                row.update(set_)
                updated.append(row)
        return updated


def test_start_run_uses_deterministic_slot_id() -> None:
    recorder = RunRecorder(FakeRunStore())
    slot = datetime(2026, 5, 10, 9, 0, tzinfo=UTC)

    first = recorder.start_run(
        channel_id="ko-shorts-tech",
        pipeline=Pipeline.B,
        trigger=Trigger.CRON,
        scheduled_slot=slot,
    )
    second = recorder.start_run(
        channel_id="ko-shorts-tech",
        pipeline=Pipeline.B,
        trigger=Trigger.CRON,
        scheduled_slot=slot,
    )

    assert first.run_id == second.run_id


def test_finish_run_rejects_second_terminal_transition() -> None:
    store = FakeRunStore()
    recorder = RunRecorder(store)
    run = recorder.start_run(
        channel_id="ko-shorts-tech",
        pipeline=Pipeline.B,
        trigger=Trigger.CRON,
    )

    finished = recorder.finish_run(run.run_id, RunState.SUCCEEDED, outcome="ok")

    assert finished.state is RunState.SUCCEEDED
    with pytest.raises(IdempotencyConflict):
        recorder.finish_run(run.run_id, RunState.FAILED)


def test_record_stage_inserts_stage_record() -> None:
    recorder = RunRecorder(FakeRunStore())

    record = recorder.record_stage(
        run_id="run-1",
        stage_name="plan",
        sequence=1,
        status=StageStatus.OK,
    )

    assert record.stage_name == "plan"
    assert record.sequence == 1
