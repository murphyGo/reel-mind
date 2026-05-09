"""Supabase and R2 storage client wrappers."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any, Protocol, cast

from boto3.s3.transfer import TransferConfig  # type: ignore[import-untyped]

from reel_mind.foundation.models import ArtifactKind, ArtifactRef, ChannelId

R2_MULTIPART_CONFIG = TransferConfig(
    multipart_threshold=16 * 1024 * 1024,
    multipart_chunksize=8 * 1024 * 1024,
    max_concurrency=4,
    use_threads=True,
)


class RetryRunner(Protocol):
    def run(self, operation: str, func: Callable[[], Any]) -> Any: ...


class SupabaseClient:
    def __init__(self, client: Any, retry: RetryRunner) -> None:
        self._client = client
        self._retry = retry

    def select_one(self, table: str, *, eq: dict[str, Any]) -> dict[str, Any] | None:
        def operation() -> dict[str, Any] | None:
            response = self._client.table(table).select("*").match(eq).limit(1).execute()
            rows = _response_data(response)
            return rows[0] if rows else None

        result = self._retry.run(f"supabase.select_one({table})", operation)
        return cast(dict[str, Any] | None, result)

    def select_many(
        self,
        table: str,
        *,
        eq: dict[str, Any] | None = None,
        order: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        def operation() -> list[dict[str, Any]]:
            query = self._client.table(table).select("*")
            if eq:
                query = query.match(eq)
            if order:
                query = query.order(order)
            if limit:
                query = query.limit(limit)
            return list(_response_data(query.execute()))

        result = self._retry.run(f"supabase.select_many({table})", operation)
        return cast(list[dict[str, Any]], result)

    def insert(self, table: str, row: dict[str, Any]) -> dict[str, Any]:
        def operation() -> dict[str, Any]:
            response = self._client.table(table).insert(row).execute()
            rows = _response_data(response)
            return rows[0] if rows else row

        return cast(dict[str, Any], self._retry.run(f"supabase.insert({table})", operation))

    def update_where(
        self,
        table: str,
        *,
        eq: dict[str, Any],
        set_: dict[str, Any],
        returning: bool = True,
    ) -> list[dict[str, Any]]:
        def operation() -> list[dict[str, Any]]:
            query = self._client.table(table).update(set_).match(eq)
            if not returning:
                query = query.select("")
            return list(_response_data(query.execute()))

        return cast(list[dict[str, Any]], self._retry.run(f"supabase.update({table})", operation))

    def rpc(self, function: str, params: dict[str, Any]) -> Any:
        return self._retry.run(
            f"supabase.rpc({function})",
            lambda: _response_data(self._client.rpc(function, params).execute()),
        )

    def aggregate_sum(self, table: str, *, column: str, eq: dict[str, Any]) -> Decimal:
        def operation() -> Decimal:
            response = self._client.table(table).select(column).match(eq).execute()
            return sum(
                (Decimal(str(row.get(column, "0"))) for row in _response_data(response)),
                Decimal("0"),
            )

        result = self._retry.run(f"supabase.aggregate_sum({table}.{column})", operation)
        return cast(Decimal, result)


class R2Client:
    def __init__(self, s3_client: Any, bucket: str, retry: RetryRunner) -> None:
        self._s3 = s3_client
        self._bucket = bucket
        self._retry = retry

    def put(self, key: str, body: bytes, content_type: str) -> ArtifactRef:
        validate_r2_key(key)

        def operation() -> ArtifactRef:
            response = self._s3.put_object(
                Bucket=self._bucket,
                Key=key,
                Body=body,
                ContentType=content_type,
            )
            return ArtifactRef(
                bucket=self._bucket,
                key=key,
                content_type=content_type,
                size_bytes=len(body),
                etag=response.get("ETag"),
                created_at=datetime.now(UTC),
            )

        return cast(ArtifactRef, self._retry.run(f"r2.put({key})", operation))

    def get(self, key: str) -> bytes:
        validate_r2_key(key)

        def operation() -> bytes:
            response = self._s3.get_object(Bucket=self._bucket, Key=key)
            return cast(bytes, response["Body"].read())

        return cast(bytes, self._retry.run(f"r2.get({key})", operation))

    def head(self, key: str) -> ArtifactRef | None:
        validate_r2_key(key)

        def operation() -> ArtifactRef | None:
            response = self._s3.head_object(Bucket=self._bucket, Key=key)
            return ArtifactRef(
                bucket=self._bucket,
                key=key,
                content_type=response.get("ContentType", "application/octet-stream"),
                size_bytes=response.get("ContentLength"),
                etag=response.get("ETag"),
                created_at=response.get("LastModified", datetime.now(UTC)),
            )

        return cast(ArtifactRef | None, self._retry.run(f"r2.head({key})", operation))

    def presigned_url(self, key: str, ttl_seconds: int = 3600) -> str:
        validate_r2_key(key)
        if not 1 <= ttl_seconds <= 86400:
            msg = "ttl_seconds must be between 1 and 86400"
            raise ValueError(msg)
        return cast(
            str,
            self._s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": self._bucket, "Key": key},
                ExpiresIn=ttl_seconds,
            ),
        )

    def delete(self, key: str) -> None:
        validate_r2_key(key)
        self._retry.run(
            f"r2.delete({key})",
            lambda: self._s3.delete_object(Bucket=self._bucket, Key=key),
        )


def validate_r2_key(key: str) -> None:
    parts = key.split("/")
    valid_kinds = {kind.value for kind in ArtifactKind}
    if (
        len(parts) < 6
        or parts[0] != "channels"
        or parts[2] != "runs"
        or parts[4] not in valid_kinds
        or not parts[1]
        or not parts[3]
        or not parts[5]
    ):
        msg = f"invalid R2 key: {key}"
        raise ValueError(msg)


def r2_key(channel_id: ChannelId, run_id: str, artifact_kind: ArtifactKind, filename: str) -> str:
    if "/" in filename or filename in {"", ".", ".."}:
        msg = f"invalid artifact filename: {filename}"
        raise ValueError(msg)
    return f"channels/{channel_id}/runs/{run_id}/{artifact_kind.value}/{filename}"


def _response_data(response: Any) -> list[dict[str, Any]]:
    data = getattr(response, "data", response)
    if data is None:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]
    return list(data)
