# U1 Shared Foundation — Infrastructure Design

**Unit**: U1 Shared Foundation
**Stage**: Infrastructure Design
**Created**: 2026-05-10
**Source plan**: `aidlc-docs/construction/plans/U1-infrastructure-design-plan.md`

This document maps U1 logical components to concrete infrastructure contracts. It is a design contract; executable SQL migrations and application code are produced during Code Generation.

---

## 1. Environment Model

U1 supports three named environments from the start:

| Environment | Purpose | Supabase | R2 | Secrets |
|-------------|---------|----------|----|---------|
| `local` | Developer tests and smoke runs | local/mocked or staging project by explicit opt-in | local/mocked or staging bucket by explicit opt-in | local `.env` outside git |
| `staging` | Migration, RLS, and integration validation | separate Supabase project | separate R2 bucket | GitHub Actions staging secrets |
| `production` | Real channel runs | production Supabase project | production R2 bucket | GitHub Actions production secrets |

Staging uses separate Supabase and R2 infrastructure, not prefixed production resources. This keeps schema/RLS tests from risking production rows or objects.

---

## 2. Logical Component Mapping

| U1 component | Infrastructure dependency | Contract |
|--------------|---------------------------|----------|
| `ConfigLoader` | Supabase `channels` table plus repo `config/defaults.yaml` | Reads channel config rows and merges them with defaults |
| `SecretsProvider` | GitHub Actions encrypted secrets, bot-host env, local untracked env | Single gateway for secret resolution |
| `SupabaseClient` | Supabase Postgres + PostgREST | Server-side service-role client for pipeline/bot/ops contexts |
| `R2Client` | Cloudflare R2 private buckets | Artifact put/get/head/presign under canonical object prefixes |
| `Logger` / `RedactionProcessor` | stdout log streams | JSON logs only; environment-native retention |
| `RetryExecutor` | none | In-process retry wrapper; no queue infrastructure |
| `CostLedger` | Supabase `cost_ledger` table | Append-only accounting rows and live monthly SUM |
| `RunRecorder` | Supabase `pipeline_runs`, `stage_records` tables | Run and stage lifecycle persistence |
| `IdempotencyGuard` | deterministic hashing plus DB uniqueness | Deterministic `run_id` for scheduled Pipeline B slots |

---

## 3. Supabase Schema Contract

U1 owns the base shared tables and conventions. Later units may add tables, columns, or views, but should not redefine U1-owned lifecycle, config, budget, or artifact conventions without an ADR.

### 3.1 `channels`

Stores channel configuration and operator-visible channel metadata.

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| `id` | `text` | yes | Channel slug, primary key, matches `^[a-z0-9][a-z0-9-]{0,31}$` |
| `display_name` | `text` | yes | Human-readable label |
| `active` | `boolean` | yes | Included by GHA matrix generation when true |
| `config` | `jsonb` | yes | Per-channel overrides; merged over `config/defaults.yaml` |
| `created_at` | `timestamptz` | yes | Default `now()` |
| `updated_at` | `timestamptz` | yes | Updated on config edits |

Constraints:
- `id` channel slug check.
- `config` must be an object.

Indexes:
- Primary key on `id`.
- Partial index on `active` for matrix generation.

### 3.2 `pipeline_runs`

Persists one pipeline invocation.

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| `run_id` | `text` | yes | Primary key |
| `channel_id` | `text` | yes | FK to `channels(id)` |
| `pipeline` | `text` | yes | `A`, `B`, or `C` |
| `scheduled_slot` | `text` | no | Canonical KST ISO-8601 slot for scheduled runs |
| `trigger` | `text` | yes | `cron`, `manual`, or `retry` |
| `state` | `text` | yes | `started`, `succeeded`, `failed`, `skipped`, `canceled` |
| `started_at` | `timestamptz` | yes | UTC |
| `finished_at` | `timestamptz` | no | UTC |
| `outcome` | `text` | no | Human-readable terminal outcome |
| `force_retry_of` | `text` | no | Prior `run_id` for operator-forced retry |
| `config_version_hash` | `text` | no | Resolved config hash used for the run |

Constraints and indexes:
- FK `channel_id -> channels(id)`.
- CHECK for valid `pipeline`, `trigger`, and `state`.
- CHECK `finished_at is not null` when state is terminal.
- Unique partial index on `(channel_id, pipeline, scheduled_slot)` where `scheduled_slot is not null` and `force_retry_of is null`.
- Index `(channel_id, pipeline, started_at desc)` for Web UI timelines.

### 3.3 `stage_records`

Append-only stage timeline rows for a run.

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| `id` | `bigint generated always as identity` | yes | Primary key |
| `run_id` | `text` | yes | FK to `pipeline_runs(run_id)` |
| `stage_name` | `text` | yes | Pipeline-specific stage key |
| `sequence` | `integer` | yes | Monotonic within run |
| `status` | `text` | yes | `ok`, `error`, `skipped`, `retrying` |
| `attempt` | `integer` | yes | 1-based |
| `started_at` | `timestamptz` | yes | UTC |
| `finished_at` | `timestamptz` | no | UTC |
| `artifacts` | `jsonb` | yes | Array of `ArtifactRef`-shaped objects |
| `error` | `jsonb` | no | `ErrorRecord`-shaped object |

Constraints and indexes:
- FK `run_id -> pipeline_runs(run_id)`.
- Unique `(run_id, sequence)`.
- CHECK for valid `status`.
- CHECK `attempt >= 1`.
- Index `(run_id, sequence)`.

Database triggers may reject new `stage_records` when the parent run is already terminal. If trigger complexity is deferred, `RunRecorder` must enforce the same invariant in Code Generation with tests.

### 3.4 `cost_ledger`

Append-only paid API accounting rows.

| Column | Type | Required | Notes |
|--------|------|----------|-------|
| `entry_id` | `text` | yes | ULID primary key |
| `timestamp` | `timestamptz` | yes | UTC |
| `month_bucket` | `date` | yes | Generated UTC month bucket |
| `channel_id` | `text` | yes | Channel attribution; see retention note below |
| `pipeline` | `text` | yes | `A`, `B`, `C`, `bot`, or `ops` |
| `run_id` | `text` | yes | Real or synthetic run id |
| `provider` | `text` | yes | Provider key |
| `bucket` | `text` | yes | `generative_video`, `tts`, `stock_media`, `claude`, or `other` |
| `units` | `numeric(18,6)` | yes | Provider-native quantity |
| `unit_kind` | `text` | yes | Unit label |
| `usd_cost` | `numeric(12,6)` | yes | Recorded actual cost |
| `metadata` | `jsonb` | yes | Provider/model details |

Cost rows are append-only and retained permanently for MVP. `channel_id` is validated by U1 and indexed for fast monthly SUM. To preserve accounting history even if channel metadata is later changed, Code Generation may use either a non-cascading FK or no FK on `cost_ledger.channel_id`; it must not allow channel deletion to delete ledger rows.

Indexes:
- Primary key on `entry_id`.
- Composite index `(channel_id, month_bucket)` for `month_spend_all_providers`.
- Index `(channel_id, timestamp desc)` for audit/debugging.

Privileges:
- Pipeline/bot service-role contexts may insert/select.
- No update/delete paths in U1.

---

## 4. Supabase Security Boundary

Pipeline, bot, and ops contexts use server-side service-role credentials through `SupabaseClient`. The Web UI never receives service-role credentials and uses Supabase Auth + RLS in U7.

RLS baseline:
- Enable RLS on shared tables.
- Service-role bypass is accepted for server contexts.
- Authenticated Web UI policies are defined in U7, but U1 reserves table shape and owner conventions.

MVP does not require Supabase IP allow-listing. The security baseline is enforced through secret isolation, RLS, server-only service-role usage, input validation, and redacted logging.

---

## 5. R2 Bucket Contract

Each environment has a separate private R2 bucket:

| Environment | Bucket role |
|-------------|-------------|
| `staging` | staging artifacts and integration-test media |
| `production` | production artifacts and published-video media |
| `local` | mock filesystem or explicit staging bucket opt-in |

Object key convention:

```text
channels/{channel_id}/runs/{run_id}/{artifact_kind}/{filename}
```

Allowed initial `artifact_kind` values:
- `samples`
- `plan`
- `scenes`
- `audio`
- `bgm`
- `composed`
- `published`

Access model:
- Buckets are private-only.
- Web UI previews use `R2Client.presigned_url`.
- Default preview TTL is 3600 seconds; max TTL remains 86400 seconds.
- No public bucket paths in MVP.

Retention:
- No lifecycle deletion in MVP.
- No object versioning requirement in MVP.
- Permanent retention supports reproducibility, re-upload, and audit trails.

---

## 6. Secret Layout

The canonical naming convention is the NFR Design convention:

```text
REEL_MIND_<KEY>
REEL_MIND_<CHANNEL_ID_UPPER_UNDERSCORE>_<KEY>
```

Examples:

| Scope | Logical key | Channel | Env var |
|-------|-------------|---------|---------|
| global | `SUPABASE_URL` | n/a | `REEL_MIND_SUPABASE_URL` |
| global | `SUPABASE_SERVICE_KEY` | n/a | `REEL_MIND_SUPABASE_SERVICE_KEY` |
| global | `R2_ENDPOINT_URL` | n/a | `REEL_MIND_R2_ENDPOINT_URL` |
| global | `R2_ACCESS_KEY_ID` | n/a | `REEL_MIND_R2_ACCESS_KEY_ID` |
| global | `R2_SECRET_ACCESS_KEY` | n/a | `REEL_MIND_R2_SECRET_ACCESS_KEY` |
| global | `R2_BUCKET` | n/a | `REEL_MIND_R2_BUCKET` |
| channel | `YT_REFRESH_TOKEN` | `ko-shorts-tech` | `REEL_MIND_KO_SHORTS_TECH_YT_REFRESH_TOKEN` |
| channel | `TTS_API_KEY` | `ko-shorts-tech` | `REEL_MIND_KO_SHORTS_TECH_TTS_API_KEY` |

Secret sources:
- GitHub Actions encrypted secrets for pipeline jobs.
- Bot-host environment for the Telegram bot.
- Local untracked `.env` files for developer smoke runs.

Secrets are never persisted to Supabase, R2, logs, or repo files. Missing secrets surface as `SecretError` and fail the run.

---

## 7. Compute Runtime

Pipeline runtime:
- GitHub-hosted runners only for MVP.
- Python baseline is `>=3.12,<3.13`.
- Dependencies are installed from `uv.lock`.
- Jobs construct U1 clients once per process invocation.

Telegram bot runtime:
- Exact host is deferred to U6.
- U1 requires only a long-running Python process with the same secret naming and stdout JSON logging semantics.

Ops scripts:
- Run locally or in GitHub Actions.
- Must use `SecretsProvider`, `SupabaseClient`, and `R2Client` rather than bypassing U1.

No U1 queue or worker infrastructure is introduced. GitHub Actions, bot workflows, and later orchestration units own async execution.

---

## 8. Observability and Alerting

Authoritative MVP logs:
- Pipeline runs: GitHub Actions logs.
- Bot: bot-host logs.
- Web UI: Vercel logs.

U1 emits stdout JSON only. It does not mirror logs to Supabase and does not use an external log backend.

Metrics are emitted as structured log fields using the `metric_name`, `metric_type`, and `metric_value` convention from NFR Design.

Before U6 exists, U1 infrastructure does not add automated alerting. Failed pipeline jobs and their logs are the operator signal. U6 later adds Telegram alert delivery on top of the same run/stage state.

---

## 9. Reconciliation and Failure Posture

There is no queue, disk spool, or pending-ledger reconciliation table in MVP.

If `CostLedger.record` fails after the `LEDGER_CRITICAL` retry budget:
- U1 raises.
- The pipeline marks the run failed where possible.
- The GitHub Actions job exits non-zero.
- The operator investigates from GHA logs and Supabase state.

This preserves the existing NFR decision: do not silently accept ledger drift.

---

## 10. Code Generation Handoff

U1 Code Generation should produce:
- Supabase SQL migration files for the U1-owned shared schema.
- Pydantic models matching the table contracts.
- U1 client wrappers and repository helpers against those schemas.
- Tests for table-shape assumptions where feasible without live Supabase.
- Property tests for pure functions and state machines defined in NFR Design.

The migration step must keep the security boundary intact: service-role secrets remain server-side only, Web UI RLS policies are completed in U7, and U1 does not introduce a public HTTP API.
