import pytest

from reel_mind.foundation import OAuthRefreshResult, SecretError, SecretsProvider, secret_env_name


def test_secret_env_name_global_and_channel_scoped() -> None:
    assert secret_env_name(None, "SUPABASE_SERVICE_KEY") == "REEL_MIND_SUPABASE_SERVICE_KEY"
    assert (
        secret_env_name("ko-shorts-tech", "YT_REFRESH_TOKEN")
        == "REEL_MIND_KO_SHORTS_TECH_YT_REFRESH_TOKEN"
    )


def test_secret_env_name_rejects_invalid_key() -> None:
    with pytest.raises(ValueError, match="invalid secret key"):
        secret_env_name(None, "bad-key")


def test_get_returns_secret_without_logging_or_caching() -> None:
    provider = SecretsProvider({"REEL_MIND_KO_SHORTS_TECH_TTS_API_KEY": "secret-value"})

    assert provider.get("ko-shorts-tech", "TTS_API_KEY") == "secret-value"


def test_get_missing_secret_raises_named_error() -> None:
    provider = SecretsProvider({})

    with pytest.raises(SecretError, match="REEL_MIND_SUPABASE_SERVICE_KEY"):
        provider.get(None, "SUPABASE_SERVICE_KEY")


def test_get_with_refresh_uses_refresh_callback_result() -> None:
    provider = SecretsProvider(
        {
            "REEL_MIND_KO_SHORTS_TECH_YT_ACCESS_TOKEN": "old-access",
            "REEL_MIND_KO_SHORTS_TECH_YT_REFRESH_TOKEN": "refresh",
        }
    )

    value = provider.get_with_refresh(
        "ko-shorts-tech",
        "YT_ACCESS_TOKEN",
        "YT_REFRESH_TOKEN",
        lambda token: OAuthRefreshResult(access_token=f"new-{token}"),
    )

    assert value == "new-refresh"
