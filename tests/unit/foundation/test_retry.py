import pytest

from reel_mind.foundation import Classification, RetryExecutor, RetryPolicy
from reel_mind.foundation.errors import RetryableStorageError, TerminalStorageError
from reel_mind.foundation.retry import classify_http_like


class HttpError(Exception):
    def __init__(self, status_code: int, retry_after: int | None = None) -> None:
        self.status_code = status_code
        self.retry_after = retry_after
        super().__init__(str(status_code))


def test_retry_executor_retries_then_succeeds() -> None:
    sleeps: list[float] = []
    calls = 0

    def flaky() -> str:
        nonlocal calls
        calls += 1
        if calls < 2:
            raise ConnectionError("temporary")
        return "ok"

    executor = RetryExecutor(
        RetryPolicy(3, (0.1, 0.2), jitter_pct=0),
        lambda exc: Classification.retryable(),
        sleep=sleeps.append,
        jitter=lambda value: value,
    )

    assert executor.run("flaky", flaky) == "ok"
    assert sleeps == [0.1]


def test_retry_executor_short_circuits_terminal_errors() -> None:
    executor = RetryExecutor(
        RetryPolicy(3, (0.1,)),
        lambda exc: Classification.terminal(),
        sleep=lambda value: None,
    )

    with pytest.raises(TerminalStorageError):
        executor.run("terminal", lambda: (_ for _ in ()).throw(ValueError("bad")))


def test_retry_executor_raises_retryable_after_exhaustion() -> None:
    executor = RetryExecutor(
        RetryPolicy(2, (0.1,), jitter_pct=0),
        lambda exc: Classification.retryable(),
        sleep=lambda value: None,
        jitter=lambda value: value,
    )

    with pytest.raises(RetryableStorageError):
        executor.run("exhausted", lambda: (_ for _ in ()).throw(ConnectionError("down")))


def test_http_classifier_honors_retry_after() -> None:
    classification = classify_http_like(HttpError(429, retry_after=15))

    assert classification == Classification.retry_after(15)
