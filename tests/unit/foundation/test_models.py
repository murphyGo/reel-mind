from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from reel_mind.foundation import (
    AdaptersConfig,
    ApprovalMode,
    ArtifactRef,
    ChannelConfig,
    CostBucket,
    LedgerEntry,
    Pipeline,
    PipelineRun,
    RunState,
    StageRecord,
    StageStatus,
    Trigger,
)


def _adapters() -> AdaptersConfig:
    return AdaptersConfig(
        source=("youtube_trends",),
        tts="korean_tts",
        stock="pexels",
        publish={"youtube": "youtube_shorts"},
    )


def test_channel_config_requires_slug_channel_id() -> None:
    with pytest.raises(ValidationError):
        ChannelConfig(
            channel_id="Bad_Channel",
            display_name="Bad",
            subject_lock="food",
            posting_schedule=("09:00",),
            adapters=_adapters(),
            version_hash="abc123",
        )


def test_channel_config_requires_optional_timeout_seconds() -> None:
    with pytest.raises(ValidationError, match="approval_timeout_seconds"):
        ChannelConfig(
            channel_id="ko-shorts-tech",
            display_name="Korean Shorts",
            subject_lock="food",
            posting_schedule=("09:00",),
            approval_mode=ApprovalMode.OPTIONAL_TIMEOUT,
            adapters=_adapters(),
            version_hash="abc123",
        )


def test_ledger_entry_rejects_negative_cost() -> None:
    with pytest.raises(ValidationError):
        LedgerEntry(
            entry_id="01HX0000000000000000000000",
            timestamp=datetime.now(UTC),
            channel_id="ko-shorts-tech",
            pipeline=Pipeline.B,
            run_id="run-1",
            provider="anthropic",
            bucket=CostBucket.CLAUDE,
            units=Decimal("10"),
            unit_kind="tokens",
            usd_cost=Decimal("-0.01"),
        )


def test_terminal_pipeline_run_requires_finished_at() -> None:
    with pytest.raises(ValidationError, match="finished_at"):
        PipelineRun(
            run_id="run-1",
            channel_id="ko-shorts-tech",
            pipeline=Pipeline.B,
            trigger=Trigger.CRON,
            state=RunState.SUCCEEDED,
            started_at=datetime.now(UTC),
        )


def test_stage_record_accepts_artifact_refs() -> None:
    artifact = ArtifactRef(
        bucket="reel-mind-production",
        key="channels/ko-shorts-tech/runs/run-1/composed/final.mp4",
        content_type="video/mp4",
        size_bytes=123,
        created_at=datetime.now(UTC),
    )

    record = StageRecord(
        run_id="run-1",
        stage_name="compose",
        sequence=1,
        status=StageStatus.OK,
        started_at=datetime.now(UTC),
        finished_at=datetime.now(UTC),
        artifacts=(artifact,),
    )

    assert record.artifacts[0].key.endswith("final.mp4")
