from pathlib import Path

import pytest

from reel_mind.foundation.config import ConfigLoader, config_version_hash, deep_merge
from reel_mind.foundation.errors import TerminalStorageError


class FakeSupabase:
    def __init__(self, rows: dict[str, dict]) -> None:
        self.rows = rows

    def select_one(self, table: str, *, eq: dict) -> dict | None:
        assert table == "channels"
        return self.rows.get(eq["id"])

    def select_many(
        self,
        table: str,
        *,
        eq: dict | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[dict]:
        assert table == "channels"
        return [row for row in self.rows.values() if row.get("active") is True]


def test_deep_merge_is_right_biased_without_mutating_inputs() -> None:
    base = {"a": {"b": 1, "c": 2}, "items": [1]}
    overlay = {"a": {"b": 3}, "items": [2]}

    merged = deep_merge(base, overlay)

    assert merged == {"a": {"b": 3, "c": 2}, "items": [2]}
    assert base == {"a": {"b": 1, "c": 2}, "items": [1]}


def test_config_version_hash_is_stable_for_key_order() -> None:
    assert config_version_hash({"b": 2, "a": 1}) == config_version_hash({"a": 1, "b": 2})


def test_load_channel_config_merges_defaults_and_row(tmp_path: Path) -> None:
    defaults = tmp_path / "defaults.yaml"
    defaults.write_text(
        """
channel_defaults:
  language: ko
  timezone: Asia/Seoul
  subject_lock: korean food
  approval_mode: required
  posting_schedule_cron_kst:
    - "0 8 * * *"
  generative_video_budget_cap_usd: 20
  active: true
  adapters:
    source: [youtube_trends]
    tts: korean_tts
    stock: pexels
    publish:
      youtube: youtube_shorts
""",
        encoding="utf-8",
    )
    loader = ConfigLoader(
        FakeSupabase(
            {
                "ko-shorts-tech": {
                    "id": "ko-shorts-tech",
                    "display_name": "Korean Shorts",
                    "active": True,
                    "config": {"subject_lock": "korean street food"},
                }
            }
        ),
        defaults_path=defaults,
    )

    config = loader.load_channel_config("ko-shorts-tech")

    assert config.subject_lock == "korean street food"
    assert config.display_name == "Korean Shorts"
    assert config.posting_schedule == ("0 8 * * *",)
    assert config.adapters.publish == {"youtube": "youtube_shorts"}
    assert len(config.version_hash) == 16


def test_load_channel_config_unknown_channel_raises(tmp_path: Path) -> None:
    defaults = tmp_path / "defaults.yaml"
    defaults.write_text("channel_defaults: {}\n", encoding="utf-8")
    loader = ConfigLoader(FakeSupabase({}), defaults_path=defaults)

    with pytest.raises(TerminalStorageError):
        loader.load_channel_config("ko-shorts-tech")
