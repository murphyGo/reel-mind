"""Secret resolution gateway."""

from __future__ import annotations

import os
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from reel_mind.foundation.errors import SecretError
from reel_mind.foundation.models import ChannelId

SECRET_KEY_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")


@dataclass(frozen=True)
class OAuthRefreshResult:
    access_token: str
    refresh_token_rotated: bool = False


class SecretsProvider:
    def __init__(self, environ: Mapping[str, str] | None = None) -> None:
        self._environ = environ if environ is not None else os.environ

    def get(self, channel_id: ChannelId | None, key: str) -> str:
        env_name = secret_env_name(channel_id, key)
        value = self._environ.get(env_name)
        if value is None or value == "":
            raise SecretError(env_name)
        return value

    def get_with_refresh(
        self,
        channel_id: ChannelId,
        access_key: str,
        refresh_key: str,
        refresh_callback: Callable[[str], OAuthRefreshResult],
    ) -> str:
        access_token = self.get(channel_id, access_key)
        refresh_token = self.get(channel_id, refresh_key)
        result = refresh_callback(refresh_token)
        if result.access_token:
            return result.access_token
        return access_token


def secret_env_name(channel_id: ChannelId | None, key: str) -> str:
    if not SECRET_KEY_RE.fullmatch(key):
        msg = f"invalid secret key: {key}"
        raise ValueError(msg)
    if channel_id is None:
        return f"REEL_MIND_{key}"
    channel_part = str(channel_id).upper().replace("-", "_")
    return f"REEL_MIND_{channel_part}_{key}"
