# U1 Code Generation Step 3 — Logging, Retry, and Idempotency Primitives

## Summary

Implemented:

- `src/reel_mind/foundation/logging.py`
  - recursive `RedactionProcessor`
  - list/string secret-pattern redaction
  - JSON structlog setup helpers
- `src/reel_mind/foundation/retry.py`
  - retry classifications and policies
  - `RetryExecutor`
  - HTTP-like classifier with 429 `Retry-After` support
- `src/reel_mind/foundation/idempotency.py`
  - KST slot canonicalization
  - deterministic 24-hex-character run IDs

## Tests

Added:

- `tests/unit/foundation/test_logging.py`
- `tests/unit/foundation/test_retry.py`
- `tests/unit/foundation/test_idempotency.py`
- `tests/property/test_foundation_properties.py`

The tests cover redaction recursion/idempotence, list pattern masking, retry success/terminal/exhaustion paths, HTTP 429 classification, KST canonicalization, deterministic run IDs, and Hypothesis properties for idempotency primitives.
