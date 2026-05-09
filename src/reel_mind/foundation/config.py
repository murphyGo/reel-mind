"""Channel configuration loading and validation."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
from typing import Any, Protocol, cast

from ruamel.yaml import YAML

from reel_mind.foundation.errors import ConfigError, TerminalStorageError
from reel_mind.foundation.models import (
    AdaptersConfig,
    ApprovalMode,
    ChannelConfig,
    ChannelId,
    WarmupPhase,
)


class ConfigSupabaseClient(Protocol):
    def select_one(self, table: str, *, eq: dict[str, Any]) -> dict[str, Any] | None: ...

    def select_many(
        self,
        table: str,
        *,
        eq: dict[str, Any] | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]: ...


def deep_merge(base: Mapping[str, Any], overlay: Mapping[str, Any]) -> dict[str, Any]:
    """Return a right-biased deep merge without mutating inputs."""

    result = deepcopy(dict(base))
    for key, value in overlay.items():
        existing = result.get(key)
        if isinstance(existing, dict) and isinstance(value, Mapping):
            result[key] = deep_merge(existing, value)
        else:
            result[key] = deepcopy(value)
    return result


def canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def config_version_hash(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()[:16]


class ConfigLoader:
    def __init__(
        self,
        supabase: ConfigSupabaseClient,
        defaults_path: Path = Path("config/defaults.yaml"),
    ) -> None:
        self._supabase = supabase
        self._defaults_path = defaults_path

    def load_channel_config(self, channel_id: ChannelId) -> ChannelConfig:
        defaults = self._read_defaults()
        row = self._supabase.select_one("channels", eq={"id": channel_id})
        if row is None:
            raise TerminalStorageError(
                operation="channels.select_one",
                reason=f"unknown channel {channel_id}",
            )

        row_config = row.get("config")
        if not isinstance(row_config, Mapping):
            row_config = {}

        merged = deep_merge(defaults, cast(Mapping[str, Any], row_config))
        merged["channel_id"] = channel_id
        merged["display_name"] = row.get("display_name", merged.get("display_name", channel_id))
        merged["active"] = row.get("active", merged.get("active", True))

        try:
            normalized = _normalize_channel_config(merged)
            normalized["version_hash"] = config_version_hash(normalized)
            return ChannelConfig.model_validate(normalized)
        except ValueError as exc:
            raise ConfigError("channel_config", str(exc)) from exc

    def list_active_channels(self) -> list[ChannelId]:
        rows = self._supabase.select_many("channels", eq={"active": True}, order="id")
        return [cast(ChannelId, row["id"]) for row in rows]

    def _read_defaults(self) -> dict[str, Any]:
        yaml = YAML(typ="safe")
        with self._defaults_path.open() as handle:
            loaded = yaml.load(handle) or {}
        if not isinstance(loaded, dict):
            raise ConfigError(str(self._defaults_path), "defaults file must contain a mapping")
        channel_defaults = loaded.get("channel_defaults", loaded)
        if not isinstance(channel_defaults, dict):
            raise ConfigError("channel_defaults", "must contain a mapping")
        return channel_defaults


def _normalize_channel_config(raw: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(raw)

    if "approval_timeout_hours" in data and "approval_timeout_seconds" not in data:
        data["approval_timeout_seconds"] = int(data["approval_timeout_hours"]) * 3600

    if "posting_schedule_cron_kst" in data and "posting_schedule" not in data:
        data["posting_schedule"] = tuple(data["posting_schedule_cron_kst"])

    if "generative_video_budget_cap_usd" in data and "monthly_budget_cap_usd" not in data:
        data["monthly_budget_cap_usd"] = data["generative_video_budget_cap_usd"]
    if "monthly_budget_cap_usd" in data and not isinstance(data["monthly_budget_cap_usd"], Decimal):
        data["monthly_budget_cap_usd"] = Decimal(str(data["monthly_budget_cap_usd"]))
    if "approval_mode" in data and not isinstance(data["approval_mode"], ApprovalMode):
        data["approval_mode"] = ApprovalMode(str(data["approval_mode"]))

    warmup = data.get("warmup")
    if isinstance(warmup, Mapping) and "warmup_phase" not in data:
        data["warmup_phase"] = WarmupPhase(
            days=int(warmup.get("duration_days", 0)),
            posts_per_day=int(warmup.get("videos_per_day", 0)),
        )

    adapters = data.get("adapters")
    if isinstance(adapters, Mapping):
        source = adapters.get("source", ())
        data["adapters"] = AdaptersConfig(
            source=tuple(source),
            tts=str(adapters["tts"]),
            stock=str(adapters["stock"]),
            publish=dict(adapters["publish"]),
            generative_video=adapters.get("generative_video"),
        )

    removable_keys = {
        "approval_timeout_hours",
        "posting_schedule_cron_kst",
        "generative_video_budget_cap_usd",
        "fallback_to_asset_assembly_on_budget_breach",
        "platform",
        "style_profile_cadence_cron_kst",
        "measure_cadence_cron_kst",
        "warmup",
    }
    return {key: value for key, value in data.items() if key not in removable_keys}
