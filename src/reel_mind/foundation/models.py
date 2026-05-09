"""Domain models for the Reel-Mind shared foundation."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

ChannelId = Annotated[str, StringConstraints(pattern=r"^[a-z0-9][a-z0-9-]{0,31}$")]


class FrozenModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)


class Pipeline(StrEnum):
    A = "A"
    B = "B"
    C = "C"
    BOT = "bot"
    OPS = "ops"
    UI = "ui"


class Trigger(StrEnum):
    CRON = "cron"
    MANUAL = "manual"
    RETRY = "retry"
    WEBHOOK = "webhook"


class ApprovalMode(StrEnum):
    REQUIRED = "required"
    OPTIONAL_TIMEOUT = "optional_timeout"
    OFF = "off"


class RunState(StrEnum):
    STARTED = "started"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELED = "canceled"


class StageStatus(StrEnum):
    OK = "ok"
    ERROR = "error"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class CostBucket(StrEnum):
    GENERATIVE_VIDEO = "generative_video"
    TTS = "tts"
    STOCK_MEDIA = "stock_media"
    CLAUDE = "claude"
    OTHER = "other"


class ArtifactKind(StrEnum):
    SAMPLES = "samples"
    PLAN = "plan"
    SCENES = "scenes"
    AUDIO = "audio"
    BGM = "bgm"
    COMPOSED = "composed"
    PUBLISHED = "published"


class WarmupPhase(FrozenModel):
    days: int = Field(ge=0)
    posts_per_day: int = Field(ge=0)


class AdaptersConfig(FrozenModel):
    source: tuple[str, ...]
    tts: str
    stock: str
    publish: dict[str, str]
    generative_video: str | None = None

    @field_validator("source")
    @classmethod
    def source_names_are_non_empty(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if not value or any(not item.strip() for item in value):
            msg = "at least one non-empty source adapter is required"
            raise ValueError(msg)
        return value


class ChannelConfig(FrozenModel):
    channel_id: ChannelId
    display_name: str
    subject_lock: str
    language: str = "ko"
    timezone: str = "Asia/Seoul"
    posting_schedule: tuple[str, ...]
    warmup_phase: WarmupPhase | None = None
    approval_mode: ApprovalMode = ApprovalMode.REQUIRED
    approval_timeout_seconds: int | None = None
    generative_video_enabled: bool = False
    monthly_budget_cap_usd: Decimal = Field(default=Decimal("20.00"), ge=Decimal("0"))
    active: bool = True
    adapters: AdaptersConfig
    feature_flags: dict[str, bool] = Field(default_factory=dict)
    version_hash: str

    @model_validator(mode="after")
    def validate_activation_rules(self) -> ChannelConfig:
        if self.active and not self.posting_schedule:
            msg = "posting_schedule is required when channel is active"
            raise ValueError(msg)
        timeout_required = self.approval_mode is ApprovalMode.OPTIONAL_TIMEOUT
        if timeout_required and self.approval_timeout_seconds is None:
            msg = "approval_timeout_seconds is required for optional_timeout approval mode"
            raise ValueError(msg)
        return self


class ArtifactRef(FrozenModel):
    bucket: str
    key: str
    content_type: str
    size_bytes: int | None = Field(default=None, ge=0)
    etag: str | None = None
    created_at: datetime


class ErrorRecord(FrozenModel):
    type: str
    message: str
    retryable: bool
    fields: dict[str, Any] = Field(default_factory=dict)
    cause: str | None = None


class LedgerEntry(FrozenModel):
    entry_id: str
    timestamp: datetime
    channel_id: ChannelId
    pipeline: Pipeline
    run_id: str
    provider: str
    bucket: CostBucket
    units: Decimal = Field(ge=Decimal("0"))
    unit_kind: str
    usd_cost: Decimal = Field(ge=Decimal("0"))
    metadata: dict[str, Any] = Field(default_factory=dict)


class PipelineRun(FrozenModel):
    run_id: str
    channel_id: ChannelId
    pipeline: Pipeline
    scheduled_slot: str | None = None
    trigger: Trigger
    state: RunState
    started_at: datetime
    finished_at: datetime | None = None
    outcome: str | None = None
    force_retry_of: str | None = None
    config_version_hash: str | None = None

    @model_validator(mode="after")
    def validate_terminal_timestamp(self) -> PipelineRun:
        if self.state is not RunState.STARTED and self.finished_at is None:
            msg = "finished_at is required for terminal runs"
            raise ValueError(msg)
        return self


class StageRecord(FrozenModel):
    run_id: str
    stage_name: str
    sequence: int = Field(ge=1)
    status: StageStatus
    attempt: int = Field(default=1, ge=1)
    started_at: datetime
    finished_at: datetime | None = None
    artifacts: tuple[ArtifactRef, ...] = Field(default_factory=tuple)
    error: ErrorRecord | None = None
