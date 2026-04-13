# U1 Shared Foundation — Domain Entities

**Unit**: U1 Shared Foundation
**Stage**: Functional Design
**Scope**: Technology-agnostic domain model. Storage types / DDL are NFR + Infrastructure Design concerns.

---

## Entity Catalog

| Entity | Owner component | Lifecycle | Mutability |
|--------|-----------------|-----------|------------|
| `ChannelConfig` | `ConfigLoader` | Built per-invocation from `defaults.yaml` + `channels` row | Immutable value object after load |
| `ChannelIdentity` | `ConfigLoader` | Identity slug + display name | Immutable |
| `SecretRef` | `SecretsProvider` | Reference to an env-resolved secret | Value-resolved per call; never stored |
| `ArtifactRef` | `R2Client` | Points to an object in R2 | Immutable (object keys are content-addressed by convention) |
| `LogEvent` | `Logger` | Single structured log record | Immutable |
| `LedgerEntry` | `CostLedger` | One paid-API call record | Append-only (immutable after write) |
| `PipelineRun` | `RunRecorder` | Full pipeline invocation | State machine; see §Run Lifecycle |
| `StageRecord` | `RunRecorder` | One stage inside a run | State machine; see §Stage Lifecycle |
| `IdempotencyKey` | `IdempotencyGuard` | Deterministic `run_id` | Derived; immutable |

---

## 1. `ChannelConfig`

Merged, validated configuration for one channel for one invocation.

| Field | Type | Notes |
|-------|------|-------|
| `channel_id` | `str` (slug, `[a-z0-9-]+`) | e.g. `ko-shorts-tech`. Used for env var suffixing and R2 prefixing |
| `display_name` | `str` | Human-readable |
| `subject_lock` | `str` | Single subject the channel covers (FR invariant) |
| `language` | `str` (BCP-47) | MVP: `ko` |
| `timezone` | `str` (IANA) | MVP: `Asia/Seoul` |
| `posting_schedule` | `list[TimeOfDay]` | Allowed publish slots (channel TZ) |
| `warmup_phase` | `WarmupPhase \| None` | Controls early-lifecycle cadence |
| `approval_mode` | `enum {required, optional_timeout, off}` | Gate behavior |
| `approval_timeout_seconds` | `int \| None` | Only meaningful when `optional_timeout` |
| `generative_video_enabled` | `bool` | Opt-in per channel |
| `monthly_budget_cap_usd` | `Decimal` | Hard cap; default `20.00` |
| `active` | `bool` | Driven by `channels.active` |
| `adapters` | `AdaptersConfig` | Nested: source/tts/stock/publish/generative names |
| `feature_flags` | `dict[str, bool]` | Loose bag for operator toggles |
| `version_hash` | `str` | Hash of the resolved config for audit |

**Invariants:**
- `channel_id` matches `^[a-z0-9][a-z0-9-]{0,31}$` (env var suffix safety).
- `approval_timeout_seconds` is required iff `approval_mode == optional_timeout`.
- `monthly_budget_cap_usd >= 0`.
- `posting_schedule` is non-empty when `active`.

### `AdaptersConfig`

| Field | Type |
|-------|------|
| `source` | `list[str]` — ordered adapter names |
| `tts` | `str` |
| `stock` | `str` |
| `publish` | `dict[platform, str]` — platform → adapter name |
| `generative_video` | `str \| None` |

---

## 2. `SecretRef`

A request to resolve a secret. Never a stored value.

| Field | Type | Notes |
|-------|------|-------|
| `scope` | `enum {global, channel}` | Determines env-var-name template |
| `channel_id` | `str \| None` | Required iff `scope=channel` |
| `key` | `str` | Logical key, e.g. `YT_REFRESH_TOKEN`, `TTS_API_KEY` |
| `resolved_env_var` | `str` | Computed (see §Secret Naming) |

**Resolution outputs** are plain `str` values returned to the caller and NOT retained.

### OAuth refresh flow (`get_with_refresh`)

- Refreshed token is held **in process memory only** for the remainder of the invocation.
- Persistence of the new refresh token is **out-of-band** (operator manually updates the GHA secret).
- No DB write, no disk write, no R2 write of secret material.

---

## 3. `ArtifactRef`

Pointer to an R2 object.

| Field | Type | Notes |
|-------|------|-------|
| `bucket` | `str` | Logical bucket name |
| `key` | `str` | See §R2 Key Convention |
| `content_type` | `str` | MIME |
| `size_bytes` | `int \| None` | Known after put |
| `etag` | `str \| None` | From R2 response |
| `created_at` | `datetime` (UTC) | |

**Key convention:** `channels/{channel_id}/runs/{run_id}/{artifact_kind}/{filename}`
where `artifact_kind ∈ {samples, plan, scenes, audio, bgm, composed, published}`.

**Presigned URL TTL:** default `3600s` (1 hour), configurable per call with upper bound enforced in U7.

---

## 4. `LogEvent`

Structured log record. Emitted to stdout as JSON in MVP (no DB sink).

| Field | Type | Notes |
|-------|------|-------|
| `timestamp` | `datetime` (UTC, ISO-8601) | |
| `level` | `enum {DEBUG, INFO, WARN, ERROR}` | |
| `message` | `str` | Static-ish template, not f-string-expanded values |
| `channel_id` | `str \| None` | Bound |
| `pipeline` | `enum {A, B, C, bot, ui, ops} \| None` | Bound |
| `run_id` | `str \| None` | Bound |
| `stage` | `str \| None` | Bound |
| `trigger` | `enum {cron, manual, retry, webhook} \| None` | Bound |
| `operator_id` | `str \| None` | Bound (for manual / UI actions) |
| `fields` | `dict[str, Any]` | Arbitrary key/values |
| `error` | `ErrorRecord \| None` | `type`, `message`, `retryable`, `cause_chain` |

---

## 5. `LedgerEntry`

Append-only cost record.

| Field | Type | Notes |
|-------|------|-------|
| `entry_id` | `str` (ULID) | Sortable |
| `timestamp` | `datetime` (UTC) | |
| `channel_id` | `str` | Required — global calls must synthesize or reject (see §Edge Cases) |
| `pipeline` | `enum {A, B, C, bot, ops}` | |
| `run_id` | `str` | Real run_id OR synthetic `manual-<iso8601>` / `cron-ops-<iso8601>` |
| `provider` | `str` | e.g. `sora`, `elevenlabs_ko`, `pexels`, `anthropic` |
| `bucket` | `enum {generative_video, tts, stock_media, claude, other}` | For reporting |
| `units` | `Decimal` | Provider-native unit (seconds, characters, tokens, calls) |
| `unit_kind` | `str` | Label for `units` |
| `usd_cost` | `Decimal` | Converted at time of call |
| `metadata` | `dict[str, Any]` | Free-form (model id, duration, etc.) |

**Invariants:**
- `channel_id`, `run_id`, `provider`, `bucket`, `usd_cost` non-null.
- `usd_cost >= 0`.
- Entries are never updated nor deleted.

---

## 6. `PipelineRun`

| Field | Type | Notes |
|-------|------|-------|
| `run_id` | `str` | See §Idempotency |
| `channel_id` | `str` | |
| `pipeline` | `enum {A, B, C}` | |
| `scheduled_slot` | `str \| None` | Canonical ISO-8601 with KST offset; `None` for A/C |
| `trigger` | `enum {cron, manual, retry}` | |
| `state` | `enum {started, succeeded, failed, skipped, canceled}` | |
| `started_at` | `datetime` (UTC) | |
| `finished_at` | `datetime \| None` | |
| `outcome` | `str \| None` | Free-form summary, e.g. `published:xyz`, `rejected_by_operator` |
| `force_retry_of` | `str \| None` | Previous run_id if operator forced a retry |

### Run Lifecycle

```
          ┌──────────────┐
 start ──▶│   started    │
          └──┬───────┬───┘
             │       │
       (stages)  (no stages emitted)
             │       │
   ┌─────────┼───────┴───────┐
   ▼         ▼               ▼
┌─────────┐ ┌─────────┐  ┌──────────┐  ┌──────────┐
│succeeded│ │ failed  │  │ skipped  │  │ canceled │
└─────────┘ └─────────┘  └──────────┘  └──────────┘
```

**Rules:**
- `started` is the unique entry state.
- Terminal states are `succeeded | failed | skipped | canceled`.
- Only one transition into a terminal state per run.
- `canceled` is used when an operator rejects an approval (Pipeline B only in MVP).
- `skipped` is used when the run is intentionally a no-op (e.g. no trend candidate passed filters; outside posting slot).

---

## 7. `StageRecord`

| Field | Type | Notes |
|-------|------|-------|
| `run_id` | `str` | FK |
| `stage_name` | `str` | e.g. `trend_scout`, `plan`, `assemble`, `approval`, `publish` |
| `sequence` | `int` | Order within run |
| `status` | `enum {ok, error, skipped, retrying}` | |
| `attempt` | `int` | 1-based; increments on `retrying` transitions |
| `started_at` / `finished_at` | `datetime` | |
| `artifacts` | `list[ArtifactRef]` | |
| `error` | `ErrorRecord \| None` | Populated when `status=error` |

### Stage Lifecycle

```
 enter ──▶ retrying ──▶ retrying ──▶ ... ──▶ ok | error | skipped
   │                                            ▲
   └────────────────────────────────────────────┘
```

- `retrying` is visible to the Web UI timeline and is terminal-for-the-current-attempt but not terminal-for-the-stage.
- Final stage status must be `ok | error | skipped`.

---

## 8. `IdempotencyKey`

| Field | Type | Notes |
|-------|------|-------|
| `channel_id` | `str` | |
| `pipeline` | `enum {A, B, C}` | |
| `scheduled_slot` | `str \| None` | Canonical KST ISO-8601, e.g. `2026-04-13T09:00:00+09:00` (minute-truncated) |
| `run_id` | `str` | See derivation below |

See `business-logic-model.md` for the derivation algorithm.

---

## 9. Shared error taxonomy

Concrete hierarchy lives in U1.

```
ReelMindError                      (base)
├── ConfigError                    (validation failed, missing required field)
├── SecretError                    (env var not present)
├── StorageError                   (Supabase / R2 failure)
│   ├── RetryableStorageError
│   └── TerminalStorageError
├── BudgetExceeded                 (terminal; $20/channel cap hit)
├── IdempotencyConflict            (run_id already completed)
├── RetryableError                 (generic transient; adapter-raised)
└── TerminalError                  (generic non-retryable)
```

Adapters (U2) will extend `RetryableError` / `TerminalError` with provider-specific subclasses.

---

## Cross-references

- `ChannelConfig.adapters` is consumed by `AdapterRegistry` (U2) — interface defined in U2.
- `StyleProfile` immutability is enforced by `StyleProfileRepository` (U3) — not U1.
- Per-channel RLS policies for Web UI are designed in U7 Infrastructure Design — U1 defines only the service-role write path.
