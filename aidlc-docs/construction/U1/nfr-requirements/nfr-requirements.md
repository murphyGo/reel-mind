# U1 Shared Foundation — NFR Requirements

**Unit**: U1 Shared Foundation
**Stage**: NFR Requirements Assessment
**Created**: 2026-04-14
**Source plan**: `aidlc-docs/construction/plans/U1-nfr-requirements-plan.md`
**Functional design baseline**: `aidlc-docs/construction/U1/functional-design/`
**Extensions enforced**: Security Baseline (blocking), Property-Based Testing — full (blocking)

---

## Scope

U1 is a Python 3.12 library consumed by:
- Pipelines A/B/C (GHA ephemeral runners, max 6h)
- Telegram bot worker (long-poll/webhook, persistent host)
- Ops scripts (manual CLI)

U1 is **not** consumed by the Next.js Web UI (U7). U1 has no service surface of its own; its availability is the availability of its dependencies (Supabase, Cloudflare R2).

NFR IDs in this document use the form `NFR-UNIT-U1-NNN` and are independent of the project-level `NFR-###` ids in `docs/requirements.md`. Where a U1 NFR refines a project-level NFR, the project ID is cited under **Source**.

---

## Categories Index

| Category | Range | Count |
|----------|-------|-------|
| Scalability | 001–003 | 3 |
| Performance | 010–015 | 6 |
| Availability | 020–022 | 3 |
| Security | 030–039 | 10 |
| Reliability | 050–055 | 6 |
| Observability | 060–063 | 4 |
| Maintainability | 070–074 | 5 |
| Compliance (Extensions) | 090–093 | 4 |

---

## 1. Scalability

### NFR-UNIT-U1-001 — Steady-state channel capacity
**Requirement**: U1 must support up to **10 active channels** with publish frequency of 1/day and ≤2 approval cycles/publish without architectural redesign.
**Source**: Q1.1; Project NFR — single-operator portfolio target ($1K/mo).
**Acceptance metric**: Concurrent invocations of `ConfigLoader.load_channel_config`, `CostLedger.record`, and `R2Client.put` from 10 distinct `channel_id` values complete with no shared-resource contention errors and with per-call latencies meeting NFR-UNIT-U1-010..013.
**Verification**: Load test in Build & Test stage — 10 channels × 3 pipeline invocations interleaved.

### NFR-UNIT-U1-002 — Burst concurrency for backfill
**Requirement**: U1 must handle a burst of **5 parallel Pipeline A runs against a single new channel** during StyleProfile backfill.
**Source**: Q1.2.
**Acceptance metric**: 5 concurrent `RunRecorder.start_run(pipeline=A)` + `R2Client.put` operations on the same `channel_id` complete without lock contention exceptions, deadlocks, or partial-write inconsistency.
**Verification**: PBT property — `forall n in 1..5, parallel runs of A produce 5 distinct run_ids and 5 well-formed run rows`.

### NFR-UNIT-U1-003 — No global singletons that prevent horizontal scale
**Requirement**: U1 must not introduce process-global mutable state (e.g. module-level connection pools without per-channel keying) that would prevent running multiple GHA jobs in parallel.
**Source**: Derived from NFR-UNIT-U1-001/002.
**Acceptance metric**: Static review checklist; clients (`SupabaseClient`, `R2Client`) are constructable per-invocation, not module-level singletons.

---

## 2. Performance (thresholds, not SLOs)

Thresholds are p95 unless stated otherwise. Measured locally against staging Supabase + R2 under no other load.

### NFR-UNIT-U1-010 — `ConfigLoader.load_channel_config` p95 ≤ 1.0 s
**Source**: Q2.1.
**Notes**: One Supabase round-trip plus YAML merge dominates. Failure to meet → introduce a short-TTL in-process cache for `channels` row (revisit at NFR Design).

### NFR-UNIT-U1-011 — `CostLedger.month_spend_all_providers(channel_id)` p95 ≤ 200 ms
**Source**: Q2.2.
**Notes**: Called by `BudgetGovernor.preflight` before every generative plan. If the live `SUM(usd_cost) GROUP BY channel_id WHERE month=...` cannot meet 200ms at scale, NFR Design must specify a `cost_summary_monthly` materialized view or trigger-maintained roll-up table.

### NFR-UNIT-U1-012 — `R2Client.put` for composed video p95 ≤ 60 s
**Source**: Q2.3.
**Scope**: 1080×1920 @ ~30s shorts, 10–30 MB payload.
**Notes**: Multipart upload threshold to be set in NFR Design.

### NFR-UNIT-U1-013 — `R2Client.presigned_url` p95 ≤ 100 ms
**Source**: Q2.4.
**Notes**: Local SigV4 signing only; no network round-trip required.

### NFR-UNIT-U1-014 — `RunRecorder.start_run` and `mark_*` p95 ≤ 500 ms
**Source**: Derived; not explicitly asked but required for fail-fast Telegram alert latency target (project NFR for operator notification).
**Notes**: Single-row INSERT/UPDATE on Supabase.

### NFR-UNIT-U1-015 — Cold-start overhead ≤ 1.5 s
**Requirement**: From `python -m reel_mind.bootstrap` to first U1 logger emit, including supabase/R2 client construction.
**Notes**: GHA runners start cold every job; this dominates short-run pipeline UX.

---

## 3. Availability

### NFR-UNIT-U1-020 — Reliance on upstream SLAs
**Requirement**: U1 has no fallback infrastructure (no local queue, no disk spool, no secondary backend). U1's availability is `min(SupabaseSLA, R2SLA) ≈ 99.9%` paid-tier.
**Source**: Q3.1.
**Acceptance metric**: NFR Design must NOT introduce a buffering layer; deviation requires an ADR.

### NFR-UNIT-U1-021 — Fail-fast on storage unreachability
**Requirement**: When Supabase or R2 is unreachable for the duration of NFR-UNIT-U1-050 retry budget, U1 raises `RetryableStorageError` (after exhaustion → caller sees `TerminalStorageError`). The pipeline run is marked `failed`, the GHA job exits non-zero, and `AlertPublisher.fire` (U6) is invoked with `severity=storage_outage`.
**Source**: Q3.2.

### NFR-UNIT-U1-022 — No degraded-mode operation
**Requirement**: U1 must not silently degrade (e.g. skipping ledger writes, skipping run records) when its dependencies fail. Either the operation succeeds with full state recorded, or it raises.
**Source**: Derived; load-bearing for budget integrity (NFR-UNIT-U1-052).

---

## 4. Security  *(Blocking — Security Baseline extension)*

### NFR-UNIT-U1-030 — Single-gateway secret resolution
**Requirement**: All secret access in any U1-consuming code MUST go through `SecretsProvider.get(channel_id, key)` / `get_with_refresh(...)`. Direct `os.environ` reads of secret-shaped keys are forbidden.
**Source**: Q4.1, Q10.1; Security Baseline.
**Verification**: ruff custom rule or grep gate in CI: `os.environ\[['\"](.*TOKEN|.*SECRET|.*API_KEY|.*REFRESH).*['\"]]` outside `secrets/` module = build failure.

### NFR-UNIT-U1-031 — Secret storage boundary
**Requirement**: Secrets exist only in (a) GHA encrypted secrets, (b) the bot host's environment, (c) process memory for the duration of one invocation. Secrets MUST NOT be written to Supabase, R2, disk, or stdout.
**Source**: Q4.1, Q4.3, Q10.1.
**Acceptance metric**: Static review checklist + redaction tests (NFR-UNIT-U1-032).

### NFR-UNIT-U1-032 — Log redaction deny-list
**Requirement**: `Logger` MUST redact (replace value with `"***"`) any field whose key matches the deny-list:
```
api_key, token, secret, refresh_token, authorization, email, telegram_chat_id
```
Match is case-insensitive on the JSON key, applied recursively to nested dicts inside `fields` and `error.cause_chain`.
**Source**: Q4.2, Q4.3.
**Verification**: PBT property — `forall log_event with deny-listed key, the serialized JSON contains "***" and not the original value`.

### NFR-UNIT-U1-033 — No secret value in error messages
**Requirement**: Error subclasses (especially `SecretError`) MUST identify a secret only by its logical key / env-var-name, never by value.
**Source**: Security Baseline.

### NFR-UNIT-U1-034 — Service-role boundary
**Requirement**: The Supabase service-role key is consumed only by U1's `SupabaseClient` (server-side). U1 MUST NOT expose this client or its key to any caller. Web UI (U7) uses Supabase anon + RLS — out of U1 scope, but the boundary is asserted here.
**Source**: Q4.1, Q10.1; Security Baseline.

### NFR-UNIT-U1-035 — Input validation at every public API
**Requirement**: All U1 public-API entry points (functions on `ConfigLoader`, `CostLedger`, `RunRecorder`, `R2Client`, `SecretsProvider`) MUST validate inputs via Pydantic v2 models. Invalid input → `ConfigError` or `ValueError` raised before any I/O.
**Source**: Q10.1; Security Baseline.

### NFR-UNIT-U1-036 — Channel-id allow-list pattern
**Requirement**: `channel_id` MUST match `^[a-z0-9][a-z0-9-]{0,31}$` and be validated at every boundary that uses it for env-var suffixing or R2 key construction (defense-in-depth against path/key-injection).
**Source**: Functional Design invariant; Security Baseline.

### NFR-UNIT-U1-037 — PII handling
**Requirement**: Operator PII is limited to (a) Supabase auth email and (b) Telegram chat id. Both treated as regular config; no field-level encryption beyond Supabase default at-rest. Both are in the redaction deny-list (NFR-UNIT-U1-032). No additional PII may be introduced into U1 entities without an ADR.
**Source**: Q4.3.

### NFR-UNIT-U1-038 — Secret rotation cadence
**Requirement**: On-demand rotation only for MVP. U1 MUST NOT depend on a fixed rotation interval (no "secret older than N days → fail" logic). U1 MUST tolerate operator-driven rotation at any time (clean restart resolves new value via `SecretsProvider`).
**Source**: Q4.4.

### NFR-UNIT-U1-039 — Missing-secret failure mode
**Requirement**: `SecretsProvider.get` raises `SecretError` (named env var, no value) when the env var is unset. The caller (pipeline) propagates → GHA job exits non-zero. **No** `AlertPublisher.fire` from U1 itself for `SecretError` in MVP; surfacing is via GHA run failure.
**Source**: Q4.5.
**Note**: Re-evaluate post-MVP if secret-misconfiguration becomes a recurring incident class.

---

## 5. Reliability & Error Classification

### NFR-UNIT-U1-050 — Internal storage retry budget
**Requirement**: `SupabaseClient` and `R2Client` MUST retry transient failures (network errors, 5xx, R2 throttling) up to **3 attempts total** with exponential backoff: 200 ms, 600 ms, 1.2 s (±20% jitter). On exhaustion, raise `RetryableStorageError` (terminal-for-this-call, but classifies the cause as transient for caller's diagnostic output).
**Source**: Q5.1.
**Out of scope**: Cross-call retry — that's the caller's concern (pipelines / adapters).

### NFR-UNIT-U1-051 — Non-retryable classification
**Requirement**: 4xx (except 408, 429), validation errors, and authentication failures raise `TerminalStorageError` immediately without retry.
**Source**: Q5.1; standard practice.

### NFR-UNIT-U1-052 — `CostLedger.record` aggressive retry
**Requirement**: Because `CostLedger.record` is critical for budget integrity, it uses an **expanded retry budget**: 5 attempts with backoff 200ms / 500ms / 1.5s / 4s / 10s before raising. Failure after exhaustion raises `TerminalStorageError` — the caller MUST surface this as a run failure (no silent drop, no local file fallback for MVP).
**Source**: Q5.2 (option a).
**Trade-off note**: Operator accepts that ledger drift on permanent Supabase outage is preferable to silent budget breach. If pattern recurs, revisit option (c) in a future iteration (out of scope, log as TECH-DEBT candidate).

### NFR-UNIT-U1-053 — Error taxonomy stability
**Requirement**: The exception hierarchy in `aidlc-docs/construction/U1/functional-design/domain-entities.md` §9 is the **public contract** of U1. Adding new subclasses is allowed; renaming or removing is a breaking change requiring coordinated update across U2/U4/U6.
**Source**: Derived.

### NFR-UNIT-U1-054 — Idempotency contract
**Requirement**: `IdempotencyGuard.run_id_for(channel_id, pipeline, scheduled_slot)` MUST be deterministic: same inputs → same `run_id`, every time, across processes. Used by U4 to guarantee no double-publish.
**Source**: Functional Design; FR — Publishing is idempotent.
**Verification**: PBT property — `forall (channel_id, pipeline, slot), run_id_for is pure and stable`.

### NFR-UNIT-U1-055 — Run-state monotonicity
**Requirement**: A `PipelineRun` may transition `started → {succeeded, failed, skipped, canceled}` exactly once. `RunRecorder` MUST reject second-terminal-transition attempts with `IdempotencyConflict`.
**Source**: Functional Design Run Lifecycle.

---

## 6. Observability

### NFR-UNIT-U1-060 — Single log format across environments
**Requirement**: U1 emits structured JSON to stdout exclusively. **No** `pretty` / `text` mode — same format in GHA, bot host, and local dev.
**Source**: Q6.1.
**Rationale**: Eliminates "logs look different in CI" debugging class.

### NFR-UNIT-U1-061 — Mandatory log fields
**Requirement**: Every `LogEvent` MUST include:
- Always: `timestamp` (UTC, ISO-8601), `level`, `message`, `event` (structured key), `service`, `git_sha`, `python_version`
- Conditional (when in scope): `gha_run_id`, `channel_id`, `pipeline`, `run_id`, `stage`, `trigger`, `operator_id`, `thread_id`
- On error: `error.{type, message, retryable, cause_chain}`
- Free-form: `fields` (dict)

`git_sha` and `python_version` are bound at logger init from env / `sys.version_info`. `gha_run_id` is read from `GITHUB_RUN_ID` when present.
**Source**: Q6.2.

### NFR-UNIT-U1-062 — Logs-as-metrics
**Requirement**: Where U1 needs to emit a metric, it does so by adding `metric_name`, `metric_type` (`counter | gauge | histogram`), and `metric_value` to the log event's `fields`. **No** separate metrics backend (Prometheus, OTLP) in MVP.
**Source**: Q6.3.

### NFR-UNIT-U1-063 — No log loss on uncaught exception
**Requirement**: U1's logger MUST flush stdout before propagating any uncaught exception out of a public-API call (atexit handler or explicit flush in error paths).
**Source**: Derived; debugging GHA failures depends on log capture.

---

## 7. Maintainability

### NFR-UNIT-U1-070 — `mypy --strict` from day 1
**Requirement**: All U1 source code passes `mypy --strict` with zero errors. CI gate.
**Source**: Q7.1.

### NFR-UNIT-U1-071 — Lint config
**Requirement**: `ruff` configured with rule sets `E, F, I, B, UP, SIM, RUF, S` (the `S` set adds bandit-style security rules). CI gate.
**Source**: Q7.2.

### NFR-UNIT-U1-072 — Test coverage ≥ 90% lines
**Requirement**: U1 maintains ≥90% line coverage measured by `pytest-cov`. CI gate.
**Source**: Q5.3.
**Note**: Branch coverage is informational only for MVP; PBT (NFR-UNIT-U1-091) supplements line coverage on edge cases.

### NFR-UNIT-U1-073 — Internal-only API stability
**Requirement**: U1 is an internal library with a "move fast, internal-only, break freely" policy. SemVer is **not** enforced. Breaking changes to U1 public API do not require an ADR but MUST be communicated in the PR description so consumers (U2/U4/U6/U8) can be updated in the same PR or immediately after.
**Source**: Q7.3.

### NFR-UNIT-U1-074 — No external error tracker in MVP
**Requirement**: No Sentry / Honeybadger / Rollbar integration. Errors surface via stdout JSON logs only.
**Source**: Q8.9.
**Re-eval trigger**: ≥3 production errors per week that are missed by manual log review.

---

## 8. Compliance with Enabled Extensions  *(Blocking)*

### NFR-UNIT-U1-090 — Security Baseline coverage
**Requirement**: U1 satisfies all blocking rules from the Security Baseline extension. Specifically, NFR-UNIT-U1-030..039 enumerate U1's compliance surface. Any new public API added later MUST extend NFR-UNIT-U1-035 (input validation) and be reviewed against the deny-list (NFR-UNIT-U1-032).
**Source**: Q10.1; Security Baseline opt-in (`aidlc-docs/aidlc-state.md`).

### NFR-UNIT-U1-091 — PBT coverage for pure functions
**Requirement**: The following U1 pure functions MUST have Hypothesis property tests at Build & Test:
- `canonicalize(slot: datetime) -> str` (idempotent + timezone-stable)
- `deep_merge(base: dict, overlay: dict) -> dict` (associative; right-bias on conflicts; no input mutation)
- `IdempotencyGuard.run_id_for(channel_id, pipeline, slot) -> str` (pure, total, deterministic, collision-resistant on input domain)
- `Logger` redaction (NFR-UNIT-U1-032)
**Source**: Q10.2; PBT extension opt-in.

### NFR-UNIT-U1-092 — PBT coverage for state machines
**Requirement**: `PipelineRun` and `StageRecord` lifecycle transitions MUST have Hypothesis state-machine tests asserting:
- All paths from `started` reach exactly one terminal state.
- No second terminal transition is accepted (NFR-UNIT-U1-055).
- `StageRecord.attempt` strictly increases on `retrying → retrying`.
**Source**: Q10.2; PBT extension opt-in.

### NFR-UNIT-U1-093 — Money/decimal property tests
**Requirement**: `LedgerEntry.usd_cost` arithmetic (sums, monthly aggregations) MUST have PBT properties asserting:
- No floating-point drift (Decimal-only).
- `ROUND_HALF_UP` at 6 dp for unit cost, 2 dp for USD totals.
- Sum of N entries equals `Decimal` sum regardless of partition order.
**Source**: Q8.5; PBT extension.

---

## 9. Out of Scope (explicitly deferred)

| Item | Why deferred | Re-eval trigger |
|------|--------------|-----------------|
| Local fallback queue for Supabase outages | Q3.1 — rely on upstream SLA | Recurring outages > 1/quarter |
| External error tracker (Sentry) | Q8.9 — log-only sufficient at MVP scale | ≥3 missed errors/week |
| IP allow-list / scheduled key rotation | Q4.1, Q4.4 — not justified at solo-operator scale | Multi-operator setup, or compliance audit |
| Async I/O (asyncio, aiobotocore) | Q8.1, Q8.2 — pipelines are synchronous-per-step | If batch throughput per run becomes a bottleneck |
| Local file fallback for `CostLedger.record` (option c from Q5.2) | Operator accepted ledger drift on prolonged outage | Same trigger as Sentry |
| Pretty-mode local logs | Q6.1 — uniformity preferred | Operator request after 90 days of use |

---

## 10. Traceability

| U1 NFR | Project NFR (`docs/requirements.md`) | Functional Design ref |
|--------|--------------------------------------|------------------------|
| 020, 021 | Availability — 24/7 operation | Run lifecycle |
| 030–039 | Security — secrets in GHA only; per-channel isolation | `SecretRef`, `SecretsProvider` |
| 052, 054 | Cost governance — $20/channel hard cap | `LedgerEntry`, `IdempotencyKey` |
| 060–063 | Observability | `LogEvent` |
| 091–093 | PBT extension blocking constraints | §9 error taxonomy, run/stage lifecycle |
