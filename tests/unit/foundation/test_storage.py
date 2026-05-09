"""Tests for SDK wrappers using boto3-compatible fake method signatures."""

# ruff: noqa: N803

from decimal import Decimal
from io import BytesIO
from typing import Any

import pytest

from reel_mind.foundation import ArtifactKind, R2Client, SupabaseClient, r2_key, validate_r2_key


class ImmediateRetry:
    def run(self, operation: str, func: Any) -> Any:
        return func()


class Response:
    def __init__(self, data: Any) -> None:
        self.data = data


class FakeQuery:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows
        self.inserted: dict[str, Any] | None = None
        self.updated: dict[str, Any] | None = None
        self.eq: dict[str, Any] = {}
        self.limit_value: int | None = None

    def select(self, columns: str) -> "FakeQuery":
        return self

    def match(self, eq: dict[str, Any]) -> "FakeQuery":
        self.eq = eq
        return self

    def limit(self, value: int) -> "FakeQuery":
        self.limit_value = value
        return self

    def order(self, value: str) -> "FakeQuery":
        return self

    def insert(self, row: dict[str, Any]) -> "FakeQuery":
        self.inserted = row
        return self

    def update(self, row: dict[str, Any]) -> "FakeQuery":
        self.updated = row
        return self

    def execute(self) -> Response:
        if self.inserted is not None:
            return Response([self.inserted])
        filtered = [row for row in self.rows if all(row.get(k) == v for k, v in self.eq.items())]
        if self.limit_value is not None:
            filtered = filtered[: self.limit_value]
        return Response(filtered)


class FakeSupabaseSdk:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows

    def table(self, name: str) -> FakeQuery:
        return FakeQuery(self.rows)

    def rpc(self, function: str, params: dict[str, Any]) -> FakeQuery:
        return FakeQuery([{"function": function, "params": params}])


class FakeS3:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    def put_object(self, *, Bucket: str, Key: str, Body: bytes, ContentType: str) -> dict[str, str]:
        self.objects[Key] = Body
        return {"ETag": "etag-1"}

    def get_object(self, *, Bucket: str, Key: str) -> dict[str, BytesIO]:
        return {"Body": BytesIO(self.objects[Key])}

    def head_object(self, *, Bucket: str, Key: str) -> dict[str, Any]:
        return {
            "ContentType": "video/mp4",
            "ContentLength": len(self.objects[Key]),
            "ETag": "etag-1",
        }

    def generate_presigned_url(
        self,
        operation: str,
        *,
        Params: dict[str, str],
        ExpiresIn: int,
    ) -> str:
        return f"https://r2.example/{Params['Key']}?ttl={ExpiresIn}"

    def delete_object(self, *, Bucket: str, Key: str) -> None:
        self.objects.pop(Key, None)


def test_supabase_client_select_and_sum() -> None:
    client = SupabaseClient(
        FakeSupabaseSdk(
            [
                {"id": "one", "channel_id": "ko-shorts-tech", "usd_cost": "1.25"},
                {"id": "two", "channel_id": "ko-shorts-tech", "usd_cost": "2.75"},
            ]
        ),
        ImmediateRetry(),
    )

    assert client.select_one("cost_ledger", eq={"id": "one"}) == {
        "id": "one",
        "channel_id": "ko-shorts-tech",
        "usd_cost": "1.25",
    }
    assert client.aggregate_sum(
        "cost_ledger",
        column="usd_cost",
        eq={"channel_id": "ko-shorts-tech"},
    ) == Decimal("4.00")


def test_r2_client_put_get_head_and_presign() -> None:
    s3 = FakeS3()
    client = R2Client(s3, "reel-mind-test", ImmediateRetry())
    key = r2_key("ko-shorts-tech", "run-1", ArtifactKind.COMPOSED, "final.mp4")

    artifact = client.put(key, b"video", "video/mp4")

    assert artifact.etag == "etag-1"
    assert client.get(key) == b"video"
    assert client.head(key).size_bytes == 5  # type: ignore[union-attr]
    assert client.presigned_url(key, ttl_seconds=60).endswith("ttl=60")


def test_r2_key_validation_rejects_invalid_shapes() -> None:
    with pytest.raises(ValueError, match="invalid R2 key"):
        validate_r2_key("bad/key")

    with pytest.raises(ValueError, match="invalid artifact filename"):
        r2_key("ko-shorts-tech", "run-1", ArtifactKind.PLAN, "../plan.json")


def test_presigned_url_rejects_out_of_range_ttl() -> None:
    client = R2Client(FakeS3(), "reel-mind-test", ImmediateRetry())
    key = r2_key("ko-shorts-tech", "run-1", ArtifactKind.PLAN, "plan.json")

    with pytest.raises(ValueError, match="ttl_seconds"):
        client.presigned_url(key, ttl_seconds=0)
