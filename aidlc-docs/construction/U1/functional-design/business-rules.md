# U1 Shared Foundation — Business Rules

**Unit**: U1 Shared Foundation
**Stage**: Functional Design
**Purpose**: Invariants and constraints the foundation enforces or guards. Violations are bugs.

---

## BR-1 · Pipelines are write-only to Supabase

- **Rule**: Pipeline code (`pipelines/*`) MUST NOT call `SupabaseClient.update` or `SupabaseClient.subscribe`.
- **Enforcement**: `SupabaseClient.update` raises `RuntimeError("update forbidden in pipeline context")` when the process-scope flag `SUPABASE_WRITE_ONLY=true` is set. GHA pipeline runners set this flag; Web UI / bot do not.
- **Rationale**: Single-writer semantics per invariant in `CLAUDE.md`.

## BR-2 · Secrets only via `SecretsProvider`

- **Rule**: Pipeline / bot code MUST NOT call `os.environ[...]` or `os.getenv(...)` directly for secret material.
- **Enforcement**: Lint rule (ruff custom rule or grep check in CI) flags `os.environ`/`os.getenv` in `pipelines/`, `bot/`. Exceptions whitelisted in `config/lint-secret-exceptions.yaml`.
- **Corollary**: Secrets are NEVER written to Supabase rows, R2 objects, logs, or stdout.

## BR-3 · Per-channel secret naming

- **Rule**: Channel-scoped env vars MUST follow `{KEY}_CHANNEL_{CHANNEL_SLUG_UPPER}` where slug `-` → `_` and is uppercased.
- **Enforcement**: `SecretsProvider` is the only code path that computes env var names. Callers pass logical keys.

## BR-4 · Every paid API call records a ledger entry

- **Rule**: Any HTTP call that charges the operator's account MUST be followed by `CostLedger.record(...)` in the same transactional unit (try/except/finally).
- **Attribution**: `(channel_id, pipeline, run_id, provider, bucket, units, usd_cost)` are all required.
- **Enforcement**: Adapters (U2) embed `CostLedger.record` in their call wrappers. Pipeline code cannot bypass because it never talks to providers directly.

## BR-5 · Monthly generative-video cap is $20 aggregate per channel

- **Rule**: `BudgetGovernor.preflight` (U4) MUST NOT approve a plan whose projected cost + month-to-date actuals would exceed `ChannelConfig.monthly_budget_cap_usd` (default `20.00`).
- **Scope**: **Aggregate** across all providers / buckets (not per-provider, not per-bucket).
- **Fallback**: Plan downgrades to asset-assembly-only when exceeded; never silently truncated.
- **Enforcement**: `CostLedger.remaining_budget(channel_id, cap_usd, month)` returns the aggregate remainder; `BudgetGovernor` gates on this.

## BR-6 · Run lifecycle invariants

- **BR-6.1**: Exactly one terminal transition per `pipeline_runs.run_id`. States `{succeeded, failed, skipped, canceled}` are mutually exclusive and final.
- **BR-6.2**: No `stage_records` insert is allowed after the run is in a terminal state.
- **BR-6.3**: A stage's final record status is `ok | error | skipped`. `retrying` is intermediate only and accompanies `attempt` increments.
- **BR-6.4**: `canceled` is reserved for operator rejection of an approval (Pipeline B). Not used elsewhere in MVP.
- **Enforcement**: `RunRecorder.finish_run` asserts current state is `started`; DB-level CHECK constraint on `pipeline_runs.state`.

## BR-7 · Idempotency

- **BR-7.1**: Pipeline B `run_id` is deterministic: `sha256(channel_id|pipeline|scheduled_slot)[:16]` + prefix. Same slot → same id → single completion.
- **BR-7.2**: `scheduled_slot` canonical form is ISO-8601 in KST (`+09:00`) truncated to the minute.
- **BR-7.3**: Pipelines A / C use a random `run_id`; retries intentionally get a fresh id.
- **BR-7.4**: Force-retry (`start_run(force_retry_of=<prior>)`) mints a new random id and records the link for audit.
- **BR-7.5**: A completed `run_id` (terminal state) cannot be started again without `force_retry_of`; `IdempotencyConflict` is raised.

## BR-8 · Timezone discipline

- **BR-8.1**: All DB timestamps are stored in UTC.
- **BR-8.2**: The monthly budget cap windows on UTC month boundaries.
- **BR-8.3**: `scheduled_slot` is stored and hashed in KST offset form; this is operator-semantic.
- **BR-8.4**: Presentation timezone in the Web UI is the channel's configured TZ (U7 concern).

## BR-9 · Config precedence

- **BR-9.1**: `channels[channel_id]` row fields OVERRIDE `config/defaults.yaml` fields on every conflict. No fields are locked-by-defaults in MVP.
- **BR-9.2**: No runtime env-var overrides in MVP. To change a value for a rerun, edit the `channels` row.
- **BR-9.3**: `ChannelConfig` is immutable after `load_channel_config` returns; mutation is a programming error.

## BR-10 · Cost-ledger append-only

- **Rule**: `cost_ledger` rows are never updated nor deleted.
- **Enforcement**: DB grants allow INSERT + SELECT only for the pipeline service role on `cost_ledger`; no UPDATE/DELETE.

## BR-11 · R2 key convention

- **Rule**: All artifacts use key `channels/{channel_id}/runs/{run_id}/{artifact_kind}/{filename}`.
- **Rule**: `artifact_kind ∈ {samples, plan, scenes, audio, bgm, composed, published}` (extensible via ADR).
- **Enforcement**: `R2Client.put` asserts the key pattern; violations raise `ValueError`.

## BR-12 · Presigned URL TTL bounds

- **Rule**: Default `3600s` (1h). Maximum `86400s` (24h). Requests above max raise `ValueError`.

## BR-13 · No log of secret values

- **Rule**: `Logger` MUST redact values for keys matching a fixed deny-list (`api_key`, `token`, `secret`, `refresh_token`, `authorization`) to `"***"`.
- **Rule**: `SecretsProvider.get` MAY log the env var NAME (resolution audit) but NEVER the value.

## BR-14 · Service-role boundary

- **Rule**: Service-role Supabase credentials are used only by pipelines, bot, and ops scripts — never shipped to the Web UI bundle.
- **Enforcement**: Web UI build environment does not include `SUPABASE_SERVICE_KEY`; U7 infra asserts this.

## BR-15 · Error classification

- **Rule**: All exceptions raised by U1 inherit from `ReelMindError`.
- **Rule**: Transient/retryable failures raise subclasses of `RetryableError` (or `RetryableStorageError`); permanent failures raise `TerminalError` (or specific subclasses like `ConfigError`, `BudgetExceeded`, `IdempotencyConflict`).
- **Consumed by**: `RetryPolicy` in U2 (retries only on `RetryableError` family).

---

## Validation matrix (at the API boundary)

| Field | Rule | Failure |
|-------|------|---------|
| `channel_id` | Matches `^[a-z0-9][a-z0-9-]{0,31}$` | `ConfigError` |
| `ChannelConfig.monthly_budget_cap_usd` | `>= 0` | `ConfigError` |
| `ChannelConfig.approval_timeout_seconds` | Required iff `approval_mode=optional_timeout` | `ConfigError` |
| `ChannelConfig.posting_schedule` | Non-empty when `active=true` | `ConfigError` |
| `LedgerEntry.usd_cost` | `>= 0` | `ValueError` |
| `LedgerEntry.run_id` | Non-null (real or synthetic) | `ValueError` |
| R2 key pattern | Matches §BR-11 | `ValueError` |
| Presigned URL TTL | `1 <= ttl <= 86400` | `ValueError` |
| `scheduled_slot` | Parseable ISO-8601, normalized to KST minute | `ValueError` |

---

## Extension compliance

### Security Baseline (blocking)

| Rule | How U1 satisfies |
|------|------------------|
| Secrets never in DB/repo/logs | BR-2, BR-13; `SecretsProvider` is sole resolver |
| Per-tenant isolation | BR-3 (channel-scoped env vars); BR-14 (service role boundary) |
| Input validation at boundaries | Validation matrix above |
| Structured error handling | BR-15 (`ReelMindError` hierarchy) |
| Append-only financial records | BR-10 |

### Property-Based Testing (full, blocking at Build & Test)

Candidate properties (to be realized in U1 Build & Test):

- `IdempotencyGuard.run_id_for` is deterministic: same inputs → same output; different inputs → different output (collision probability bound).
- `canonicalize(scheduled_slot)` is idempotent and converges: canonicalize(canonicalize(x)) == canonicalize(x).
- `deep_merge(defaults, row)` is right-biased: for any key k, merge(d, r)[k] == r[k] when k in r.
- `CostLedger.remaining_budget` is monotone non-increasing in total spend for fixed `cap_usd`.
- Run lifecycle: no sequence of allowed API calls produces two terminal states.
- R2 key validation: any string matching the pattern parses; any non-matching string raises.
