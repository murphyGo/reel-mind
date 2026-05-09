# U1 Code Generation Step 1 — Foundation Models and Errors

## Summary

Implemented the first shared foundation contracts:

- `src/reel_mind/foundation/models.py`
  - Strict frozen Pydantic models for channel config, artifacts, ledger entries, pipeline runs, stage records, and error records.
  - Shared enums and `ChannelId` validation.
- `src/reel_mind/foundation/errors.py`
  - `ReelMindError` base class and structured U1 exception hierarchy.
  - `to_log_dict()` for deterministic structured logging.
- `src/reel_mind/foundation/__init__.py`
  - Public exports for the Step 1 foundation surface.

## Tests

Added:

- `tests/unit/foundation/test_models.py`
- `tests/unit/foundation/test_errors.py`

The tests cover slug validation, approval timeout validation, non-negative ledger costs, terminal run timestamp requirements, artifact references, secret error redaction posture, retryable storage log shape, and structured budget errors.

## Notes

No storage, config loading, logging processor, retry logic, or SDK wrappers were implemented in this step. Those remain in later code-generation plan steps.
