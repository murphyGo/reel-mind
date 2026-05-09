from decimal import Decimal

from reel_mind.foundation import BudgetExceeded, RetryableStorageError, SecretError


def test_secret_error_does_not_include_value() -> None:
    error = SecretError("REEL_MIND_SUPABASE_SERVICE_KEY")

    assert "secret-value" not in str(error)
    assert error.to_log_dict()["fields"] == {
        "env_var_name": "REEL_MIND_SUPABASE_SERVICE_KEY",
    }
    assert error.to_log_dict()["retryable"] is False


def test_retryable_storage_error_log_shape() -> None:
    error = RetryableStorageError(operation="supabase.insert(cost_ledger)", attempts=3)

    assert error.to_log_dict()["retryable"] is True
    assert error.to_log_dict()["fields"]["attempts"] == 3


def test_budget_exceeded_has_structured_decimal_fields() -> None:
    error = BudgetExceeded(
        channel_id="ko-shorts-tech",
        cap_usd=Decimal("20.00"),
        attempted_usd=Decimal("4.25"),
        current_spend_usd=Decimal("18.50"),
    )

    assert error.to_log_dict()["fields"] == {
        "channel_id": "ko-shorts-tech",
        "cap_usd": "20.00",
        "attempted_usd": "4.25",
        "current_spend_usd": "18.50",
    }
