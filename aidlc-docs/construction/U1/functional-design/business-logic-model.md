# U1 Shared Foundation — Business Logic Model

**Unit**: U1 Shared Foundation
**Stage**: Functional Design
**Scope**: Algorithms and workflows per component, technology-agnostic.

---

## 1. `ConfigLoader` — config merge

### Inputs
- Repo file `config/defaults.yaml` (read once per process; treated as immutable input).
- Row `channels[channel_id]` from Supabase.

### Algorithm

```
load_channel_config(channel_id):
    defaults   ← parse(config/defaults.yaml)
    row        ← supabase.select("channels").where(id=channel_id).one()
    if row is None:                       raise ConfigError("unknown channel")
    merged     ← deep_merge(defaults, row.config)      # row wins on every conflict
    validated  ← validate(merged)                      # see §Validation rules
    identity   ← ChannelIdentity(channel_id, row.display_name)
    version_hash ← sha256(canonical_json(validated))[:16]
    return ChannelConfig(**validated, version_hash=version_hash)
```

### Merge semantics
- **Deep merge** on nested dicts; lists are **replaced** (no append).
- **No runtime overrides** (MVP choice). If a one-off rerun needs different behavior, operator edits the `channels` row, not env vars.
- Channel row wins on every conflict — no "locked defaults" in MVP.

### Validation rules

| Rule | Fail mode |
|------|-----------|
| `channel_id` slug matches `^[a-z0-9][a-z0-9-]{0,31}$` | `ConfigError` |
| `language` is a BCP-47 string | `ConfigError` |
| `timezone` is a valid IANA zone | `ConfigError` |
| `approval_mode` ∈ enum | `ConfigError` |
| `approval_timeout_seconds` required iff `approval_mode = optional_timeout` | `ConfigError` |
| `monthly_budget_cap_usd >= 0` | `ConfigError` |
| `posting_schedule` non-empty when `active=true` | `ConfigError` |
| Adapter names are non-empty strings | `ConfigError` |

`validate()` returns a `ValidationResult` with `ok` / `errors[]` for `ConfigLoader.validate(config)` public API; `load_channel_config` raises on error.

### `list_active_channels()`

```
SELECT id FROM channels WHERE active = true
```

No merge, no validation — just slug list. Used by GHA matrix generator (U8).

---

## 2. `SecretsProvider` — secret resolution

### Secret naming convention

- **Channel-scoped**: `{KEY}_CHANNEL_{CHANNEL_SLUG_UPPER}`
  - `channel_id` slug is uppercased and `-` → `_`.
  - Example: `channel_id=ko-shorts-tech`, `key=YT_REFRESH_TOKEN` → env var `YT_REFRESH_TOKEN_CHANNEL_KO_SHORTS_TECH`.
- **Global**: `{KEY}` as-is.
  - Example: `SUPABASE_SERVICE_KEY`, `R2_ACCESS_KEY`, `ANTHROPIC_API_KEY`.

### `get(scope_or_channel_id, key) -> str`

Accepts either a `channel_id` slug OR the literal `None` (or string `"global"`) for global scope.

```
get(channel_id, key):
    env_name ← resolve_env_name(channel_id, key)
    value ← os.environ.get(env_name)
    if value is None or value == "":
        raise SecretError(f"missing secret: {env_name}")
    log.debug("secret.resolved", env_var=env_name)   # NEVER log value
    return value
```

- Values are **never cached** in a module-level dict — process memory only, per call.
- Values are **never logged**; only the env var NAME.

### `get_with_refresh(channel_id, key, refresh_fn) -> str`

For OAuth tokens (YouTube).

```
get_with_refresh(channel_id, key, refresh_fn):
    try:
        token ← get(channel_id, key)
        if is_expired(token):
            token ← refresh_fn(token)    # adapter-provided
            emit_alert_if(refresh_succeeded, "operator must update GHA secret")
        return token                     # in-process only; not persisted
    except SecretError: re-raise
```

- Refreshed token is used by the adapter for the remainder of the process.
- Operator receives a Telegram alert (via `AlertPublisher`, U6) when refresh occurs, prompting manual GHA-secret update.
- **No DB write**, **no file write** of the refreshed token.

---

## 3. `SupabaseClient` — schema-validated writes

### Connection

- Uses **service-role key** for all pipeline + bot contexts.
- Web UI uses a separate Supabase client with anon/JWT (out of U1 scope — U7 concern).

### `insert(table, row, idempotency_key=None) -> Row`

```
insert(table, row, idempotency_key):
    validated ← validate_against_schema(table, row)        # pydantic model per table
    if idempotency_key:
        existing ← query(table, {"idempotency_key": idempotency_key}).first()
        if existing: return existing                        # no-op
    inserted ← supabase_py.table(table).insert(validated).execute()
    return inserted
```

- Schema validation uses Pydantic models generated per table (tables defined in Infrastructure Design).
- `idempotency_key` is an optional second-layer guard for write-once tables like `published_videos`.

### `query`, `update`, `subscribe`

- `query` and `update` exist for administrative / Web-UI paths; pipeline code should avoid `update` (write-only invariant).
- `subscribe` is a pass-through to Realtime; Web UI only. Pipelines MUST NOT subscribe.

---

## 4. `R2Client` — artifact storage

### `put(key, bytes, content_type) -> ArtifactRef`

```
put(key, data, content_type):
    assert key matches channels/{channel_id}/runs/{run_id}/{kind}/{file}
    response ← s3_client.put_object(Bucket=bucket, Key=key, Body=data, ContentType=content_type)
    return ArtifactRef(bucket, key, content_type, len(data), response.etag, now_utc())
```

### `presigned_url(key, ttl_seconds=3600) -> str`

- Default TTL: `3600s` (1 hour) for Web UI approval preview.
- Max TTL enforced: `86400s` (24h). Beyond raises `ValueError`.

### `get(key) -> bytes`

Plain fetch for server-side consumers (e.g. `FfmpegComposer` in U4 reads stock media clips).

---

## 5. `Logger` — structured logging

### Context binding

```
logger = Logger.root()                                 # unbound
logger = logger.bind(channel_id="ko-shorts-tech",
                     pipeline="B",
                     run_id="B-ko-shorts-tech-2026-04-13T09-00-KST",
                     stage="plan",
                     trigger="cron",
                     operator_id=None)
logger.info("plan.generated", scenes=6, style_profile_version=3)
```

- `bind()` returns a **new** logger (immutable; no shared mutation).
- Emits JSON to stdout. GHA captures stdout; Vercel captures stdout for Web UI. No Supabase log sink in MVP.

### Redaction

- A fixed deny-list of key names (`api_key`, `token`, `secret`, `refresh_token`, `authorization`) causes values to be replaced with `"***"` even if passed into `fields`.
- Error records' `__cause__` chain is walked, but message strings are not regex-scrubbed (accepted risk; adapters must format their own errors).

---

## 6. `CostLedger` — budget accounting

### `record(channel_id, pipeline, run_id, provider, units, usd_cost, metadata) -> LedgerEntry`

```
record(...):
    entry ← LedgerEntry(
        entry_id=ulid_now(),
        timestamp=now_utc(),
        channel_id=channel_id,
        pipeline=pipeline,
        run_id=run_id,                      # real run_id OR synthetic (see below)
        provider=provider,
        bucket=bucket_for(provider),        # mapping table
        units=units, usd_cost=usd_cost,
        metadata=metadata)
    supabase.insert("cost_ledger", entry)
    log.info("cost.recorded", provider=provider, usd_cost=str(usd_cost))
    return entry
```

### Synthetic run_ids for non-pipeline paid calls

- Cron health check: `run_id = "ops-cron-<iso8601_utc>"`, `pipeline = "ops"`.
- Manual CLI call: `run_id = "manual-<iso8601_utc>"`, `pipeline = "ops"`.
- `channel_id` is still required — a global paid call must be attributed to some channel OR rejected.

### `month_spend(channel_id, provider, month) -> Decimal`

- `month` is a `(year, month)` pair in **UTC**.
- Month boundary: `[YYYY-MM-01T00:00:00Z, YYYY-(MM+1)-01T00:00:00Z)`.
- Sums `usd_cost` where `channel_id` and `provider` match and `timestamp` is in range.
- Variant `month_spend_all_providers(channel_id, month)` returns aggregate — used for the $20 cap.

### `remaining_budget(channel_id, cap_usd, month) -> Decimal`

- `cap_usd` is the **aggregate** cap per channel per month (not per-provider).
- Returns `max(Decimal(0), cap_usd - month_spend_all_providers(channel_id, month))`.
- Consumed by `BudgetGovernor.preflight` in U4.

---

## 7. `RunRecorder` — run + stage lifecycle

### `start_run(channel_id, pipeline, trigger, scheduled_slot=None, force_retry_of=None) -> run_id`

```
start_run(channel_id, pipeline, trigger, scheduled_slot, force_retry_of):
    if force_retry_of:
        run_id ← new_random_run_id(channel_id, pipeline)
    elif scheduled_slot:
        run_id ← IdempotencyGuard.run_id_for(channel_id, pipeline, scheduled_slot)
        if already_ran(run_id): raise IdempotencyConflict(run_id)
    else:
        run_id ← new_random_run_id(channel_id, pipeline)    # Pipeline A / C
    insert "pipeline_runs" (run_id, channel_id, pipeline, scheduled_slot,
                           trigger, state="started", started_at=now_utc(),
                           force_retry_of=force_retry_of)
    return run_id
```

### `stage(run_id, name, status, artifacts, attempt=1, error=None) -> StageRecord`

```
stage(...):
    sequence ← next stage sequence for run_id
    if status == "retrying":
        attempt ← attempt + 1 on retry transition (caller-managed)
    insert "stage_records" (run_id, stage_name=name, sequence, status,
                            attempt, started_at, finished_at, artifacts, error)
```

**State rules enforced at insert time:**
- Reject stage write if run is in a terminal state.
- A stage's final status in a run must be `ok | error | skipped`. `retrying` rows are intermediate.

### `finish_run(run_id, state, outcome=None)`

```
finish_run(run_id, state):
    assert state in {succeeded, failed, skipped, canceled}
    current ← query pipeline_runs by run_id
    assert current.state == "started"       # one terminal transition
    update pipeline_runs set state=state, finished_at=now_utc(), outcome=outcome
```

---

## 8. `IdempotencyGuard` — deterministic run_id

### Canonical slot representation

- `scheduled_slot: str` in ISO-8601 with **KST offset**, minute-truncated.
- Format: `YYYY-MM-DDTHH:MM:00+09:00`.
- Example: `2026-04-13T09:00:00+09:00`.
- Any `datetime` input is normalized: convert to `Asia/Seoul`, truncate to minute, format.

### `run_id_for(channel_id, pipeline, scheduled_slot) -> str`

```
run_id_for(channel_id, pipeline, scheduled_slot):
    slot_canonical ← canonicalize(scheduled_slot)           # KST, minute-truncated
    seed ← f"{channel_id}|{pipeline}|{slot_canonical}"
    hash ← sha256(seed).hexdigest()[:16]
    return f"{pipeline}-{channel_id}-{slot_canonical_compact}-{hash}"
    # where slot_canonical_compact = "2026-04-13T09-00-KST"
```

- **Pipeline B** always supplies `scheduled_slot` (publish idempotency matters).
- **Pipelines A / C** call `new_random_run_id` instead — retries intentionally get a fresh id.

### `already_ran(run_id) -> bool`

```
already_ran(run_id):
    row ← supabase.select("pipeline_runs").where(run_id=run_id).first()
    return row is not None and row.state in {succeeded, failed, skipped, canceled}
```

- `started` (in-flight) runs are **not** treated as "already ran" — a concurrent second invocation for the same slot SHOULD collide on DB unique constraint, which surfaces as `IdempotencyConflict` and is retried by GHA.

### Force-retry escape hatch

- `start_run(force_retry_of=<prior_run_id>)` mints a fresh random `run_id`.
- Used by the operator via a manual CLI after a terminal failure when they explicitly want a re-attempt on the same slot.
- Previous run is preserved in `pipeline_runs`; `force_retry_of` links the chain for audit.
- Authorization: single-operator MVP — whoever holds the GHA/CLI credentials. Revisit when multi-user.

---

## 9. Cross-cutting: timezone discipline

| Purpose | Timezone | Reason |
|---------|----------|--------|
| Database timestamps (`timestamp`, `started_at`, `finished_at`, `ledger.timestamp`) | UTC | SQL simplicity, cross-channel comparisons |
| Cost-ledger month boundary | UTC | Consistent monthly rollup |
| `scheduled_slot` (idempotency + posting cadence) | KST (channel tz in MVP) | Operator-facing; posting windows are local |
| Log `timestamp` | UTC | Uniform |
| Web UI display | Channel TZ | Rendering concern (U7) |

The only place KST appears in stored form is `scheduled_slot` strings, precisely because they are operator-semantic ("the 9am slot") rather than measurement-semantic.
