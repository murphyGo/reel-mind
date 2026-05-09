from reel_mind.foundation import RedactionProcessor, redact_value


def test_redacts_nested_secret_keys_with_lengths() -> None:
    event = {
        "fields": {
            "Authorization": "Bearer abc",
            "nested": {"email": "operator@example.com"},
        }
    }

    redacted = RedactionProcessor()(None, "info", event)

    assert redacted["fields"]["Authorization"] == "***(len=10)"
    assert redacted["fields"]["nested"]["email"] == "***(len=20)"


def test_redacts_secret_patterns_inside_lists() -> None:
    redacted = redact_value({"headers": ["Authorization: Bearer abc", "plain"]})

    assert redacted == {"headers": ["Authorization: ***", "plain"]}


def test_redaction_is_idempotent_for_masked_values() -> None:
    value = {"token": "***(len=12)"}

    assert redact_value(redact_value(value)) == {"token": "***(len=12)"}
