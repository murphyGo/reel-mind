"""Structured exception contract for the Reel-Mind shared foundation."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Self


class ReelMindError(Exception):
    """Base class for all Reel-Mind domain errors."""

    retryable = False

    def __init__(self, message: str, **fields: Any) -> None:
        super().__init__(message)
        self.message = message
        self.fields = fields

    def to_log_dict(self) -> dict[str, Any]:
        cause = self.__cause__
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "retryable": self.retryable,
            "fields": self.fields,
            "cause": repr(cause) if cause is not None else None,
        }

    def with_cause(self, cause: BaseException) -> Self:
        self.__cause__ = cause
        return self


class RetryableError(ReelMindError):
    """Base class for transient errors that callers may retry."""

    retryable = True


class TerminalError(ReelMindError):
    """Base class for permanent errors that should not be retried."""


class ConfigError(TerminalError):
    def __init__(self, field_path: str, reason: str) -> None:
        super().__init__(
            f"invalid config at {field_path}: {reason}",
            field_path=field_path,
            reason=reason,
        )


class SecretError(TerminalError):
    def __init__(self, env_var_name: str) -> None:
        super().__init__(f"missing secret: {env_var_name}", env_var_name=env_var_name)


class StorageError(ReelMindError):
    def __init__(self, message: str, operation: str, **fields: Any) -> None:
        super().__init__(message, operation=operation, **fields)
        self.operation = operation


class RetryableStorageError(StorageError, RetryableError):
    def __init__(self, operation: str, attempts: int) -> None:
        super().__init__(
            f"retryable storage failure after {attempts} attempts: {operation}",
            operation=operation,
            attempts=attempts,
        )


class TerminalStorageError(StorageError, TerminalError):
    def __init__(self, operation: str, reason: str) -> None:
        super().__init__(
            f"terminal storage failure during {operation}: {reason}",
            operation=operation,
            reason=reason,
        )


class BudgetExceeded(TerminalError):  # noqa: N818 - AIDLC contract name
    def __init__(
        self,
        *,
        channel_id: str,
        cap_usd: Decimal,
        attempted_usd: Decimal,
        current_spend_usd: Decimal,
    ) -> None:
        super().__init__(
            f"budget exceeded for {channel_id}",
            channel_id=channel_id,
            cap_usd=str(cap_usd),
            attempted_usd=str(attempted_usd),
            current_spend_usd=str(current_spend_usd),
        )


class IdempotencyConflict(TerminalError):  # noqa: N818 - AIDLC contract name
    def __init__(self, existing_run_id: str) -> None:
        super().__init__(
            f"run already completed: {existing_run_id}",
            existing_run_id=existing_run_id,
        )
