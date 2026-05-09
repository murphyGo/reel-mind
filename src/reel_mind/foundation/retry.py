"""Retry execution primitives."""

from __future__ import annotations

import random
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import TypeVar

from reel_mind.foundation.errors import RetryableStorageError, TerminalStorageError

T = TypeVar("T")


class ClassificationKind(StrEnum):
    RETRYABLE = "retryable"
    TERMINAL = "terminal"
    RETRY_AFTER = "retry_after"


@dataclass(frozen=True)
class Classification:
    kind: ClassificationKind
    retry_after_seconds: float | None = None

    @classmethod
    def retryable(cls) -> Classification:
        return cls(ClassificationKind.RETRYABLE)

    @classmethod
    def terminal(cls) -> Classification:
        return cls(ClassificationKind.TERMINAL)

    @classmethod
    def retry_after(cls, seconds: float) -> Classification:
        return cls(ClassificationKind.RETRY_AFTER, max(0.0, seconds))


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int
    backoff_seq: tuple[float, ...]
    jitter_pct: float = 0.20


STORAGE_DEFAULT = RetryPolicy(3, (0.2, 0.6, 1.2))
LEDGER_CRITICAL = RetryPolicy(5, (0.2, 0.5, 1.5, 4.0, 10.0))


class RetryExecutor:
    def __init__(
        self,
        policy: RetryPolicy,
        classify: Callable[[Exception], Classification],
        *,
        sleep: Callable[[float], None] = time.sleep,
        jitter: Callable[[float], float] | None = None,
    ) -> None:
        self._policy = policy
        self._classify = classify
        self._sleep = sleep
        self._jitter = jitter or self._default_jitter

    def run(self, operation: str, func: Callable[[], T]) -> T:
        attempts = 0
        last_error: Exception | None = None
        while attempts < self._policy.max_attempts:
            attempts += 1
            try:
                return func()
            except Exception as exc:
                last_error = exc
                classification = self._classify(exc)
                if classification.kind is ClassificationKind.TERMINAL:
                    terminal = TerminalStorageError(operation=operation, reason=str(exc))
                    raise terminal.with_cause(exc) from exc
                if attempts >= self._policy.max_attempts:
                    break
                self._sleep(self._delay_for(attempts - 1, classification))
        error = RetryableStorageError(operation=operation, attempts=attempts)
        if last_error is not None:
            raise error.with_cause(last_error) from last_error
        raise error

    def _delay_for(self, index: int, classification: Classification) -> float:
        if classification.kind is ClassificationKind.RETRY_AFTER:
            return min(classification.retry_after_seconds or 0.0, 10.0)
        base = self._policy.backoff_seq[min(index, len(self._policy.backoff_seq) - 1)]
        return self._jitter(base)

    def _default_jitter(self, value: float) -> float:
        spread = value * self._policy.jitter_pct
        return random.uniform(value - spread, value + spread)  # noqa: S311


def classify_http_like(exc: Exception) -> Classification:
    status = getattr(exc, "status_code", None) or getattr(exc, "status", None)
    if status == 429:
        retry_after = getattr(exc, "retry_after", None)
        if retry_after is not None:
            return Classification.retry_after(float(retry_after))
        return Classification.retryable()
    if status == 408:
        return Classification.retryable()
    if isinstance(status, int):
        if 500 <= status <= 599:
            return Classification.retryable()
        if 400 <= status <= 499:
            return Classification.terminal()
    if isinstance(exc, (ConnectionError, TimeoutError)):
        return Classification.retryable()
    return Classification.terminal()
