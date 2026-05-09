# U1 Code Generation Step 6 — Bootstrap and CLI

## Summary

Implemented:

- `src/reel_mind/foundation/bootstrap.py`
  - `Runtime` dataclass
  - `build_runtime()` wiring for secrets, Supabase, R2, config, cost ledger, and run recorder
- `src/reel_mind/cli/main.py`
  - `list-active-channels`
  - `validate-channel-config`

## Tests

Added:

- `tests/unit/foundation/test_bootstrap.py`
- `tests/unit/test_cli.py`

The tests cover the runtime grouping contract and CLI command behavior with injected fake runtime objects.
