# U1 Shared Foundation — Code Generation Plan

**Unit**: U1 Shared Foundation
**Stage**: Code Generation
**Created**: 2026-05-10
**AIDLC rule**: `construction/code-generation.md`
**Plan status**: Approved by autonomous `/dev-reel-mind` continuation on 2026-05-10

This file is the single source of truth for U1 Code Generation. Execute one checked step per `/dev-reel-mind` cycle, commit and push after each completed step.

---

## Unit Context

U1 provides the shared Python foundation consumed by pipelines, the Telegram bot, and ops scripts:

- Config loading from `config/defaults.yaml` + Supabase `channels` rows
- Secret resolution through one gateway
- Structured JSON logging with redaction
- Supabase and R2 wrapper clients
- Retry classification/execution
- Cost ledger accounting
- Pipeline run and stage lifecycle recording
- Idempotency helpers

U1 is application code under the workspace root, never under `aidlc-docs/`.

Existing scaffold package:

- `src/reel_mind/foundation/`

U1 Code Generation will implement this existing package rather than creating `src/reel_mind/u1/`.

---

## Story and Requirement Traceability

U1 supports the shared foundations for:

- FR-008 Multi-Channel Orchestration
- FR-012 Per-Channel Configuration
- FR-013 Budget Governance
- NFR-002 Security
- NFR-003 Observability
- NFR-004 Cost Governance
- NFR-005 Reproducibility
- NFR-008 Testing
- NFR-009 Runtime Constraints

Unit-specific references:

- `aidlc-docs/construction/U1/functional-design/`
- `aidlc-docs/construction/U1/nfr-requirements/`
- `aidlc-docs/construction/U1/nfr-design/`
- `aidlc-docs/construction/U1/infrastructure-design/`
- `aidlc-docs/construction/shared-infrastructure.md`

---

## Dependencies and Interfaces

Runtime dependencies:

- Python `>=3.12,<3.13` target from U1 tech-stack decisions
- `pydantic` v2 for strict models and validation
- `structlog` for JSON logging
- `supabase` v2 sync client
- `boto3` for Cloudflare R2
- `python-ulid` or compatible ULID provider for ledger IDs
- `ruamel.yaml` preferred by U1 tech-stack decisions; existing `pyproject.toml` currently has `pyyaml`, so dependency alignment is included below

Consumer-facing imports should be stable under `reel_mind.foundation`.

---

## Code Generation Steps

- [ ] **Step 1 — Foundation package skeleton, domain models, and exception contract**
  - Create/update:
    - `src/reel_mind/foundation/__init__.py`
    - `src/reel_mind/foundation/models.py`
    - `src/reel_mind/foundation/errors.py`
  - Implement strict Pydantic/domain contracts for `ChannelConfig`, `ArtifactRef`, `LedgerEntry`, `PipelineRun`, `StageRecord`, `ErrorRecord`, shared enums, and `ChannelId`.
  - Implement `ReelMindError` hierarchy with structured fields and `to_log_dict()`.
  - Add focused tests:
    - `tests/unit/foundation/test_models.py`
    - `tests/unit/foundation/test_errors.py`
  - Add code summary:
    - `aidlc-docs/construction/U1/code/step-01-foundation-models.md`

- [ ] **Step 2 — Config loading and secret resolution**
  - Create/update:
    - `src/reel_mind/foundation/config.py`
    - `src/reel_mind/foundation/secrets.py`
    - `config/defaults.yaml`
    - `pyproject.toml` dependency alignment if needed
  - Implement `deep_merge`, canonical config hashing, `ConfigLoader`, and `SecretsProvider`.
  - Enforce canonical `REEL_MIND_<KEY>` / `REEL_MIND_<CHANNEL>_<KEY>` env names.
  - Add tests:
    - `tests/unit/foundation/test_config.py`
    - `tests/unit/foundation/test_secrets.py`
  - Add code summary:
    - `aidlc-docs/construction/U1/code/step-02-config-secrets.md`

- [ ] **Step 3 — Logging, redaction, retry, and idempotency primitives**
  - Create/update:
    - `src/reel_mind/foundation/logging.py`
    - `src/reel_mind/foundation/retry.py`
    - `src/reel_mind/foundation/idempotency.py`
  - Implement `RedactionProcessor`, JSON logger factory, `RetryExecutor`, retry policies, `canonicalize_slot`, and `run_id_for`.
  - Add unit and property tests:
    - `tests/unit/foundation/test_logging.py`
    - `tests/unit/foundation/test_retry.py`
    - `tests/unit/foundation/test_idempotency.py`
    - `tests/property/test_foundation_properties.py`
  - Add code summary:
    - `aidlc-docs/construction/U1/code/step-03-primitives.md`

- [ ] **Step 4 — Supabase and R2 client wrappers**
  - Create/update:
    - `src/reel_mind/foundation/storage.py`
  - Implement `SupabaseClient` and `R2Client` wrappers with injected retry/logging, R2 key validation, presigned URL TTL validation, and transfer config constants.
  - Add tests with mocked SDK clients:
    - `tests/unit/foundation/test_storage.py`
  - Add code summary:
    - `aidlc-docs/construction/U1/code/step-04-storage-clients.md`

- [ ] **Step 5 — Cost ledger and run recorder**
  - Create/update:
    - `src/reel_mind/foundation/cost.py`
    - `src/reel_mind/foundation/runs.py`
  - Implement `CostLedger` and `RunRecorder` over `SupabaseClient`, including append-only ledger rows, monthly spend queries, remaining budget, lifecycle transitions, and stage recording.
  - Add tests:
    - `tests/unit/foundation/test_cost.py`
    - `tests/unit/foundation/test_runs.py`
  - Add code summary:
    - `aidlc-docs/construction/U1/code/step-05-ledger-runs.md`

- [ ] **Step 6 — Bootstrap wiring and CLI smoke surfaces**
  - Create/update:
    - `src/reel_mind/foundation/bootstrap.py`
    - `src/reel_mind/cli/main.py` if missing or incomplete
  - Implement a lightweight `Runtime`/bootstrap factory and minimal CLI smoke commands for config validation and active-channel listing.
  - Add tests:
    - `tests/unit/foundation/test_bootstrap.py`
    - `tests/unit/test_cli.py`
  - Add code summary:
    - `aidlc-docs/construction/U1/code/step-06-bootstrap-cli.md`

- [ ] **Step 7 — Supabase migration and infrastructure artifacts**
  - Create/update:
    - `supabase/migrations/*_u1_shared_foundation.sql`
    - `.env.example`
    - any targeted docs needed for secret layout
  - Encode U1 table schema, constraints, indexes, and RLS baseline from Infrastructure Design.
  - Add SQL/static validation where feasible.
  - Add code summary:
    - `aidlc-docs/construction/U1/code/step-07-migration-infra.md`

- [ ] **Step 8 — Verification pass and U1 code-generation summary**
  - Run targeted verification:
    - `uv run pytest tests/unit/foundation tests/property -q`
    - `uv run ruff check src tests`
    - `uv run mypy src`
  - Create/update:
    - `aidlc-docs/construction/U1/code/code-generation-summary.md`
  - Record any unavailable verification honestly.

---

## Completion Criteria

U1 Code Generation is complete when:

- All plan steps are checked.
- U1 foundation imports are available from `reel_mind.foundation`.
- Unit/property tests cover the implemented U1 surfaces.
- Supabase migration artifacts exist for U1-owned tables.
- Code summary documentation exists under `aidlc-docs/construction/U1/code/`.
- Verification results are recorded.
