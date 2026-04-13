# U1 Shared Foundation — NFR Design Patterns

**Unit**: U1 Shared Foundation
**Stage**: NFR Design
**Created**: 2026-04-14
**Inputs**: `aidlc-docs/construction/U1/nfr-requirements/` (41 NFRs + 16 tech-stack decisions)
**Companion**: `logical-components.md`

This document specifies **how** U1 realizes its NFRs as concrete design patterns. Implementation lives in U1 Code Generation; this is the contract.

---

## Pattern Index

| # | Pattern | Realizes NFRs |
|---|---------|---------------|
| P-01 | Retry-with-Classification (RetryExecutor) | 050, 051 |
| P-02 | Critical-Write Extended Retry | 052 |
| P-03 | Redaction Pipeline Processor | 032 |
| P-04 | Structured Log Processor Chain | 060, 061, 062, 063 |
| P-05 | Single-Gateway Secret Resolution | 030, 031, 033, 039 |
| P-06 | Pydantic Boundary Validation | 035, 036 |
| P-07 | Live-SUM Cost Aggregation | 011 |
| P-08 | Multipart Upload with Custom Threshold | 012 |
| P-09 | Local SigV4 Presigning | 013 |
| P-10 | Per-Invocation Client Construction | 003, 015 |
| P-11 | Deterministic Idempotency Derivation | 054 |
| P-12 | Run-State Monotonic Transition Guard | 055 |
| P-13 | Structured Exception Contract | 053 |
| P-14 | Fail-Fast on Storage Outage | 020, 021, 022 |
| P-15 | PBT Property Catalog (specifications) | 091, 092, 093 |

---

## P-01 — Retry-with-Classification (`RetryExecutor`)

**Realizes**: NFR-050, NFR-051.

**Shape**:
```
RetryExecutor(
  policy: RetryPolicy,             # max_attempts, backoff_seq, jitter_pct
  classify: Callable[[Exception], Classification],
  sleep: Callable[[float], None] = time.sleep,
).run(callable_, *args) -> T
```

**`RetryPolicy` profiles**:
| Profile | Attempts | Backoff (s) | Jitter | Used by |
|---------|----------|-------------|--------|---------|
| `STORAGE_DEFAULT` | 3 | [0.2, 0.6, 1.2] | ±20% | SupabaseClient, R2Client |
| `LEDGER_CRITICAL` | 5 | [0.2, 0.5, 1.5, 4.0, 10.0] | ±20% | CostLedger.record |

**`Classification`** = `Retryable | Terminal | RetryAfter(seconds)`.

**Default classifier** for HTTP-shaped errors:
- 5xx, network errors (`ConnectionError`, `Timeout`, `DNSError`) → `Retryable`
- 408 → `Retryable`
- 429 → `RetryAfter(min(header_value, 10s))` if `Retry-After` present, else `Retryable` (Q3.1)
- 4xx (other) → `Terminal`
- DB unique-violation (Postgres `23505`), RLS denial (`42501`), Pydantic ValidationError → `Terminal`
- For `LEDGER_CRITICAL`: any `Terminal` short-circuits remaining attempts (Q3.2)

**Behavior**:
- After exhaustion, raise `RetryableStorageError` with `__cause__` set to the **last** underlying exception (Q6.2).
- Emit one `WARN` log per retry with `event=retry`, `attempt`, `next_backoff_s`, `error.type`.
- Sleep wrapper is injected for testability.

**PBT spec** (catalog P-15):
- `forall (attempts, backoff_seq), total wall time ≤ sum(backoff_seq) * (1 + jitter)`.
- `forall Terminal classification, attempts == 1`.
- `forall RetryAfter(s), s is honored before next attempt`.

---

## P-02 — Critical-Write Extended Retry

**Realizes**: NFR-052.

`CostLedger.record(entry)` wraps the Supabase INSERT in `RetryExecutor(policy=LEDGER_CRITICAL)`. On exhaustion → raise `TerminalStorageError` (Q1.2 accepts up to one in-flight call past cap, but record itself MUST raise — caller surfaces the failure).

**No** local-file fallback for MVP (Q5.2 of NFR Requirements).

---

## P-03 — Redaction Pipeline Processor

**Realizes**: NFR-032, NFR-037.

**Shape**: a `structlog` processor injected into the chain (P-04).

**Deny-list** (case-insensitive key match):
```
api_key, token, secret, refresh_token, authorization, email, telegram_chat_id
```

**Traversal scope** (Q4.1):
- Recursively walk `dict` keys at every nesting level.
- Walk `list` / `tuple` values element-by-element. For string elements, apply the **string-pattern matcher** (see below). For dict elements, recurse normally.
- Tuples/lists of bytes are not traversed (binary payloads excluded; should not be in logs anyway).

**String-pattern matcher** (for list elements and free-form `message` strings):
- Regex: `(?i)\b(authorization|bearer|token|secret|api[_-]?key|refresh[_-]?token)\s*[:=]\s*[^\s,;'"]+`
- Replace match with `"<key>: ***"`.

**Replacement format** (Q4.2): `"***(len=N)"` where `N` is the length of the redacted value (`str(value).__len__()`).

**Edge cases**:
- `None` value → no redaction, no length annotation.
- Non-string scalar (int, bool) → still redact when key matches: `"***(len=N)"` of `str(value)`.
- Pydantic models / dataclasses → coerced to dict via `model_dump()` / `asdict()` before traversal.
- Pre-existing `"***(len=...)"` values are left untouched (idempotent).

**Idempotence requirement** (testable via PBT P-15): redaction is a fixed point — `redact(redact(x)) == redact(x)`.

---

## P-04 — Structured Log Processor Chain

**Realizes**: NFR-060, NFR-061, NFR-062, NFR-063.

**Chain** (Q4.3 confirmed):
```
1. structlog.contextvars.merge_contextvars
2. structlog.stdlib.add_log_level
3. structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp")
4. structlog.processors.CallsiteParameterAdder(parameters=[FILENAME, LINENO])
5. add_static_context(service, git_sha, python_version, gha_run_id)
6. RedactionProcessor (P-03)
7. structlog.processors.dict_tracebacks
8. structlog.processors.JSONRenderer(serializer=orjson.dumps, sort_keys=True)
```

**Static context** (initialized once at logger init):
- `service`: caller-supplied (`"reel-mind/u1"`, `"pipelines/B"`, etc.).
- `git_sha`: read from `GIT_SHA` env or `subprocess git rev-parse HEAD` (cached).
- `python_version`: `f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"`.
- `gha_run_id`: from `GITHUB_RUN_ID` env when present, else omitted.

**Bound context** (via `logger.bind(...)`): `channel_id, pipeline, run_id, stage, trigger, operator_id, thread_id` — bound by callers when in scope.

**`event` field convention**: every log call sets `event="<snake_case_key>"` (e.g. `event="config_load"`, `event="ledger_record"`, `event="retry"`).

**`metric_*` convention** (NFR-062): logs-as-metrics are emitted by adding `metric_name`, `metric_type ∈ {counter, gauge, histogram}`, `metric_value` to the event's `fields`.

**Flush guarantee** (NFR-063): an `atexit` handler calls `sys.stdout.flush()`. Public-API methods that catch-and-reraise also `flush()` before reraising.

---

## P-05 — Single-Gateway Secret Resolution

**Realizes**: NFR-030, NFR-031, NFR-033, NFR-039.

`SecretsProvider.get(channel_id, key) -> str` is the **only** code path that may read secret-shaped env vars.

**Env-var name template**:
- Channel-scoped: `REEL_MIND_<CHANNEL_ID_UPPER_UNDERSCORE>_<KEY>`
  - `channel_id` lowercased per NFR-036; uppercased + hyphens→underscores for env-var compat: `ko-shorts-tech` → `KO_SHORTS_TECH`.
- Global: `REEL_MIND_<KEY>`.

**Behavior**:
- Missing env var → raise `SecretError(env_var_name)` (no value in message — NFR-033).
- Successful resolution → return the value as plain `str`. **Never cache** in module state.
- Token never written to logs (deny-list P-03 covers `secret/token/api_key/refresh_token/authorization`).

**`get_with_refresh(channel_id, key, refresh_url, refresh_token_key)`** (OAuth):
- If access token expired (caller decides via try/refresh-on-401), fetch a fresh one using the refresh token.
- New access token held in **process-local memory only** for the rest of the invocation.
- New refresh token (if rotated by provider) is **logged at INFO** as `event=oauth_token_rotated, channel_id=...` (no token value) — operator must update the GHA secret out-of-band.

**CI gate**: ruff custom rule / grep check `os.environ\[['\"](.*TOKEN|.*SECRET|.*API_KEY|.*REFRESH).*['\"]]` outside `secrets/` module = build failure.

---

## P-06 — Pydantic Boundary Validation

**Realizes**: NFR-035, NFR-036.

Every U1 public-API method that accepts caller input MUST validate via a Pydantic v2 model with `model_config = ConfigDict(strict=True, extra='forbid', frozen=True)`.

**Channel-id allow-list** is enforced in a single shared `ChannelId = Annotated[str, StringConstraints(pattern=r"^[a-z0-9][a-z0-9-]{0,31}$")]` type (NFR-036). Reused across `ChannelConfig`, `LedgerEntry`, `ArtifactRef`, `PipelineRun`.

Validation failures raise `ConfigError` (for `ConfigLoader`) or propagate Pydantic `ValidationError` (other call sites).

---

## P-07 — Live-SUM Cost Aggregation

**Realizes**: NFR-011.

**Pattern** (Q1.1 = option a): live `SELECT SUM(usd_cost) FROM cost_ledger WHERE channel_id=? AND month_bucket=?`.

**Schema requirement** (passed to Infrastructure Design):
- `cost_ledger.month_bucket` — generated column `date_trunc('month', timestamp)` typed as `date`.
- Composite index `(channel_id, month_bucket)`.
- Optional partial index on `(channel_id, month_bucket) WHERE timestamp > now() - interval '90 days'` if cardinality grows.

**Overshoot tolerance** (Q1.2): "up to one in-flight call past cap" — `BudgetGovernor.preflight` reads the SUM, then the paid call may complete and `record` after another concurrent caller has already recorded. Acceptable for MVP; not a transactional guarantee.

**Re-eval trigger** (logged as TECH-DEBT candidate, not raised today): if p95 of `month_spend_all_providers` exceeds 200ms in production, switch to trigger-maintained roll-up table (Q1.1 option c).

---

## P-08 — Multipart Upload with Custom Threshold

**Realizes**: NFR-012.

**`R2Client.put`** uses `boto3.s3.transfer.TransferConfig`:
```python
TransferConfig(
  multipart_threshold = 16 * 1024 * 1024,   # 16 MiB (Q2.1)
  multipart_chunksize = 8 * 1024 * 1024,    # 8 MiB parts when multipart
  max_concurrency = 4,
  use_threads = True,
)
```

**Integrity** (Q2.2): rely on R2's ETag and S3 `x-amz-checksum-*` headers. No client-side MD5/SHA256 computation.

**Returned `ArtifactRef`** populated from R2 response (`size_bytes`, `etag`, `created_at=now()`).

---

## P-09 — Local SigV4 Presigning

**Realizes**: NFR-013.

`R2Client.presigned_url(artifact_ref, ttl_seconds=3600)` calls `boto3.client('s3').generate_presigned_url('get_object', Params=..., ExpiresIn=ttl_seconds)`. **No network call**; signing is entirely local. Default TTL 3600s; max enforced by caller (U7).

---

## P-10 — Per-Invocation Client Construction

**Realizes**: NFR-003, NFR-015.

(Q5.1, Q5.2 confirmed)
- `SupabaseClient` and `R2Client` are constructed **once per process** at bootstrap, passed via dependency injection.
- They internally hold a single connection pool (`httpx` for Supabase, `urllib3` for boto3).
- No per-channel multiplexing.
- No thread-safe internal pool needed — GHA matrix supplies process-level parallelism (NFR-002).

**Bootstrap module** (`reel_mind.bootstrap`) wires:
```
ConfigLoader → SecretsProvider → SupabaseClient → R2Client → Logger
                                  ↓
                       CostLedger, RunRecorder
```

Cold-start budget (NFR-015, ≤1.5s): client construction is lazy — no network calls until first use.

---

## P-11 — Deterministic Idempotency Derivation

**Realizes**: NFR-054.

```python
def run_id_for(
  channel_id: ChannelId,
  pipeline: Literal["A", "B", "C"],
  scheduled_slot: datetime | None,
  idempotency_key: str | None = None,
) -> str:
    if scheduled_slot is None and idempotency_key is None:
        raise ValueError("either scheduled_slot or idempotency_key required")  # Q7.2 option (c) for safety; (a) is satisfied via idempotency_key arg
    slot_part = canonicalize(scheduled_slot) if scheduled_slot else f"key:{idempotency_key}"
    raw = f"{channel_id}|{pipeline}|{slot_part}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
```

(Q7.1: 24 hex chars / 96 bits confirmed sufficient.)
(Q7.2: support both `scheduled_slot` AND `idempotency_key`; reject when neither — combines option (a) with option (c) safety.)

`canonicalize(slot)` → ISO-8601 with explicit offset, minute-truncated:
`"2026-04-13T09:00:00+09:00"`. Pure function; PBT-tested.

---

## P-12 — Run-State Monotonic Transition Guard

**Realizes**: NFR-055.

`RunRecorder.mark_<terminal>(run_id)` issues:
```sql
UPDATE pipeline_runs
SET state = $terminal, finished_at = now(), outcome = $outcome
WHERE run_id = $run_id AND state = 'started'
RETURNING run_id;
```

Zero rows updated → raise `IdempotencyConflict(existing_run_id=run_id)`. Single-statement enforcement; no read-then-write race. PBT-tested as a state machine (catalog P-15).

---

## P-13 — Structured Exception Contract

**Realizes**: NFR-053.

(Q6.1) All U1 exceptions extend `ReelMindError` and carry **structured fields**:

```python
class BudgetExceeded(TerminalError):
    cap_usd: Decimal
    attempted_usd: Decimal
    current_spend_usd: Decimal
    channel_id: str

class IdempotencyConflict(TerminalError):
    existing_run_id: str

class SecretError(TerminalError):
    env_var_name: str       # never the value (NFR-033)

class ConfigError(TerminalError):
    field_path: str         # e.g. "channels.ko-shorts-tech.posting_schedule"
    reason: str

class RetryableStorageError(RetryableError):
    operation: str          # e.g. "supabase.insert(cost_ledger)"
    attempts: int
    # __cause__ holds the last underlying exception (Q6.2)

class TerminalStorageError(TerminalError):
    operation: str
    # __cause__ holds the underlying exception
```

Each exception's `__str__` formats fields deterministically (used by `error.message` log field). A `to_log_dict()` method emits `{type, message, retryable, fields, cause}` for Logger consumption.

**Stability** (NFR-053): adding fields is non-breaking; removing/renaming requires coordinated U2/U4/U6 update.

---

## P-14 — Fail-Fast on Storage Outage

**Realizes**: NFR-020, NFR-021, NFR-022.

After `RetryExecutor` exhausts retries:
1. Raise `RetryableStorageError`/`TerminalStorageError` (caller sees terminal-for-this-call).
2. Pipeline catches at top level → marks `PipelineRun.state = failed`.
3. Pipeline's exit handler invokes `AlertPublisher.fire(severity="storage_outage", channel_id, run_id, error)` (U6 dependency — out of U1 scope, but the contract is asserted here).
4. GHA job exits non-zero.

**No degraded mode**: U1 never silently skips ledger writes or run records on outage. Either the operation completes or the pipeline run fails.

---

## P-15 — PBT Property Catalog (Specifications)

**Realizes**: NFR-091, NFR-092, NFR-093.

These are **specifications**; Hypothesis test implementations live in Build & Test (Q8.1).

### Pure functions

| Property | Function | Spec |
|----------|----------|------|
| PBT-001 | `canonicalize(slot)` | Idempotent: `canonicalize(parse(canonicalize(s))) == canonicalize(s)` for all valid datetimes |
| PBT-002 | `canonicalize(slot)` | Timezone-stable: `canonicalize(s.astimezone(UTC)) == canonicalize(s)` |
| PBT-003 | `deep_merge(base, overlay)` | Right-bias: top-level overlay key always wins on conflict |
| PBT-004 | `deep_merge(base, overlay)` | No input mutation: `base` and `overlay` unchanged after call |
| PBT-005 | `deep_merge(base, overlay)` | Identity: `deep_merge({}, x) == x`, `deep_merge(x, {}) == x` |
| PBT-006 | `run_id_for(c, p, slot, key)` | Deterministic: same inputs → same output, every call |
| PBT-007 | `run_id_for(c, p, slot, key)` | Total: defined for all valid inputs (raises only for the documented invalid case) |
| PBT-008 | `run_id_for(c, p, slot, key)` | Distinct outputs for inputs that differ in any field (collision-resistance within domain sample) |
| PBT-009 | `RedactionProcessor` | Idempotent: `redact(redact(e)) == redact(e)` |
| PBT-010 | `RedactionProcessor` | Deny-list completeness: for every `(key, value)` where `key` matches deny-list, the rendered JSON contains `"***(len="` and not the original value |
| PBT-011 | `RedactionProcessor` | List traversal: deny-listed string-patterns inside lists are also redacted |

### Decimal arithmetic (NFR-093)

| Property | Spec |
|----------|------|
| PBT-020 | Sum-order invariance: for any list of `LedgerEntry.usd_cost` values, `sum` is independent of partition order |
| PBT-021 | Rounding: `quantize` to 2 dp with `ROUND_HALF_UP` is bit-exact (no float drift) |
| PBT-022 | Non-negativity preserved: sum of non-negative entries is non-negative |

### State machines (NFR-092)

| Property | Spec |
|----------|------|
| PBT-030 | `PipelineRun`: from `started`, every reachable terminal is one of `{succeeded, failed, skipped, canceled}` |
| PBT-031 | `PipelineRun`: second terminal transition raises `IdempotencyConflict` |
| PBT-032 | `StageRecord`: `attempt` strictly increases on `retrying → retrying` |
| PBT-033 | `StageRecord`: final status ∈ `{ok, error, skipped}` |

### Retry / classification (P-01)

| Property | Spec |
|----------|------|
| PBT-040 | `RetryExecutor`: total wall time ≤ `sum(backoff_seq) * (1 + jitter_pct)` |
| PBT-041 | `RetryExecutor`: terminal classification ⇒ exactly 1 attempt |
| PBT-042 | `RetryExecutor`: `RetryAfter(s)` ⇒ `s` slept before next attempt |

---

## Cross-References

- All patterns reference NFRs in `nfr-requirements.md`.
- Component realization mapping → `logical-components.md`.
- Implementation lives in U1 Code Generation (workspace root, not aidlc-docs/).
- Schema decisions (cost_ledger month_bucket index, RLS policies) are deferred to Infrastructure Design.
