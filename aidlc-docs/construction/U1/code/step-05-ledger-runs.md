# U1 Code Generation Step 5 — Cost Ledger and Run Recorder

## Summary

Implemented:

- `src/reel_mind/foundation/cost.py`
  - `CostLedger.record`
  - `month_spend_all_providers`
  - `remaining_budget`
- `src/reel_mind/foundation/runs.py`
  - `RunRecorder.start_run`
  - `record_stage`
  - `finish_run`

The implementation uses the U1 model contracts and Supabase wrapper interface, generates ULID ledger IDs, derives deterministic scheduled run IDs, and rejects repeated terminal transitions with `IdempotencyConflict`.

## Tests

Added:

- `tests/unit/foundation/test_cost.py`
- `tests/unit/foundation/test_runs.py`

The tests cover append-only ledger insertion, non-negative remaining budget, deterministic scheduled run IDs, terminal-transition protection, and stage record insertion.
