"""Runtime wiring for the shared foundation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import boto3  # type: ignore[import-untyped]
from supabase import create_client

from reel_mind.foundation.config import ConfigLoader
from reel_mind.foundation.cost import CostLedger
from reel_mind.foundation.logging import init_logger
from reel_mind.foundation.retry import STORAGE_DEFAULT, RetryExecutor, classify_http_like
from reel_mind.foundation.runs import RunRecorder
from reel_mind.foundation.secrets import SecretsProvider
from reel_mind.foundation.storage import R2Client, SupabaseClient


@dataclass(frozen=True)
class Runtime:
    secrets: Any
    supabase: Any
    r2: Any
    config_loader: Any
    cost_ledger: Any
    run_recorder: Any


def build_runtime(*, service: str = "reel-mind/foundation") -> Runtime:
    init_logger(service)
    secrets = SecretsProvider()
    retry = RetryExecutor(STORAGE_DEFAULT, classify_http_like)
    supabase = SupabaseClient(
        create_client(
            secrets.get(None, "SUPABASE_URL"),
            secrets.get(None, "SUPABASE_SERVICE_KEY"),
        ),
        retry,
    )
    r2 = R2Client(_build_s3_client(secrets), secrets.get(None, "R2_BUCKET"), retry)
    return Runtime(
        secrets=secrets,
        supabase=supabase,
        r2=r2,
        config_loader=ConfigLoader(supabase),
        cost_ledger=CostLedger(supabase),
        run_recorder=RunRecorder(supabase),
    )


def _build_s3_client(secrets: SecretsProvider) -> Any:
    return boto3.client(
        "s3",
        endpoint_url=secrets.get(None, "R2_ENDPOINT_URL"),
        aws_access_key_id=secrets.get(None, "R2_ACCESS_KEY_ID"),
        aws_secret_access_key=secrets.get(None, "R2_SECRET_ACCESS_KEY"),
    )
