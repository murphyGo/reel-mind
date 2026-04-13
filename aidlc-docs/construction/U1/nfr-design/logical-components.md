# U1 Shared Foundation — Logical Components

**Unit**: U1 Shared Foundation
**Stage**: NFR Design
**Created**: 2026-04-14
**Companion**: `nfr-design-patterns.md`

This document enumerates U1's internal sub-components: their public interfaces, dependencies, and the NFR / pattern surface each one realizes. Implementation lives in U1 Code Generation; method signatures here are the **contract** consumed by U2/U4/U6/U8.

---

## Component Map

```
                       ┌──────────────────────┐
                       │      Logger          │  (P-04, P-03)
                       └──────────▲───────────┘
                                  │ used by all
┌──────────────┐  reads  ┌────────┴───────────┐  uses  ┌─────────────────┐
│ ConfigLoader │────────▶│    SecretsProvider │◀───────│ All call sites  │
└──────┬───────┘         └────────────────────┘        └─────────────────┘
       │ produces ChannelConfig
       ▼
┌──────────────┐
│ AdaptersConf │ (consumed by U2)
└──────────────┘

┌──────────────────┐         ┌──────────────────┐
│  SupabaseClient  │         │     R2Client     │   (P-08, P-09)
└──────────▲───────┘         └─────────▲────────┘
           │ wraps with                │
           ▼                           ▼
   ┌───────────────┐ ┌──────────────┐ ┌────────────────┐
   │   CostLedger  │ │ RunRecorder  │ │ ArtifactStore  │
   └───────────────┘ └──────────────┘ └────────────────┘
            ▲              ▲
            └──────┬───────┘
                   │ uses
            ┌──────┴────────┐
            │ RetryExecutor │  (P-01, P-02)
            └───────────────┘

┌────────────────────┐         ┌─────────────────────┐
│ IdempotencyGuard   │         │ RedactionProcessor  │  (P-03)
└────────────────────┘         └─────────────────────┘
```

10 components total. All live in `reel_mind/u1/` (Code Generation will finalize module layout).

---

## Component Index

| # | Component | Module (planned) | Realizes |
|---|-----------|------------------|----------|
| C-01 | `ConfigLoader` | `reel_mind.u1.config` | NFR-010, 035, 036, P-06 |
| C-02 | `SecretsProvider` | `reel_mind.u1.secrets` | NFR-030, 031, 033, 038, 039, P-05 |
| C-03 | `Logger` (factory) | `reel_mind.u1.logging` | NFR-032, 060, 061, 062, 063, P-03, P-04 |
| C-04 | `RedactionProcessor` | `reel_mind.u1.logging.redaction` | NFR-032, 037, P-03, PBT-009..011 |
| C-05 | `SupabaseClient` | `reel_mind.u1.storage.supabase` | NFR-014, 020, 021, 050, 051, P-10 |
| C-06 | `R2Client` | `reel_mind.u1.storage.r2` | NFR-012, 013, P-08, P-09, P-10 |
| C-07 | `RetryExecutor` | `reel_mind.u1.retry` | NFR-050, 051, 052, P-01, P-02, PBT-040..042 |
| C-08 | `CostLedger` | `reel_mind.u1.cost` | NFR-011, 052, 093, P-07, PBT-020..022 |
| C-09 | `RunRecorder` | `reel_mind.u1.runs` | NFR-014, 055, P-12, PBT-030..033 |
| C-10 | `IdempotencyGuard` | `reel_mind.u1.idempotency` | NFR-054, P-11, PBT-001, 002, 006..008 |

A bootstrap module `reel_mind.u1.bootstrap` wires the dependency graph (P-10).

---

## C-01 — `ConfigLoader`

**Purpose**: Build a validated `ChannelConfig` for one channel for one invocation, by merging `config/defaults.yaml` with the `channels` row from Supabase.

**Public interface**:
```python
class ConfigLoader:
    def __init__(self, supabase: SupabaseClient, defaults_path: Path = Path("config/defaults.yaml")): ...

    def load_channel_config(self, channel_id: ChannelId) -> ChannelConfig: ...
    def list_active_channels(self) -> list[ChannelId]: ...
```

**Dependencies**: `SupabaseClient` (read `channels` row), `ruamel.yaml` (parse defaults), `pydantic` (validate `ChannelConfig`).

**Key behaviors**:
- `load_channel_config`: read defaults YAML → fetch `channels` row → `deep_merge(defaults, row.config)` → `ChannelConfig.model_validate(merged)` → set `version_hash = sha256(canonical_json)`.
- Raises `ConfigError(field_path, reason)` on validation failure.
- Raises `TerminalStorageError` if `channels` row missing.

**Realizes**: NFR-010 (p95 ≤ 1s — single Supabase round-trip + local YAML parse), NFR-035/036 (Pydantic validation, ChannelId allow-list).

**Out of scope**: caching (NFR-010 currently met without).

---

## C-02 — `SecretsProvider`

**Purpose**: Single gateway for all secret resolution (P-05).

**Public interface**:
```python
class SecretsProvider:
    def get(self, channel_id: ChannelId | None, key: str) -> str: ...
    def get_with_refresh(
        self,
        channel_id: ChannelId,
        access_key: str,
        refresh_key: str,
        refresh_callback: Callable[[str], OAuthRefreshResult],
    ) -> str: ...
```

**Env-var resolution**: `REEL_MIND_<CHANNEL_UPPER>_<KEY>` for channel scope; `REEL_MIND_<KEY>` for global.

**Dependencies**: `os.environ` only (no Supabase, no R2 — secrets never persisted).

**Failure mode**: `SecretError(env_var_name)` — value never in message (NFR-033).

**Realizes**: NFR-030/031/033/038/039, P-05.

**CI gate**: forbid `os.environ` reads of secret-shaped keys outside this module.

---

## C-03 — `Logger` (factory)

**Purpose**: Configure structlog and provide a bound logger per call site.

**Public interface**:
```python
def init_logger(service: str) -> structlog.BoundLogger: ...    # called once per process
def get_logger() -> structlog.BoundLogger: ...                  # per-call-site retrieval

# Usage:
log = get_logger().bind(channel_id="ko-shorts-tech", run_id="abc...", pipeline="B")
log.info("config_loaded", event="config_load", fields={"version_hash": "..."})
```

**Static context** added at `init_logger`: `service`, `git_sha`, `python_version`, `gha_run_id` (when env present).

**Processor chain**: per P-04, with `RedactionProcessor` (C-04) in position 6.

**Output**: stdout JSON via `orjson.dumps`. **No** pretty mode (NFR-060).

**Flush guarantee**: `atexit.register(sys.stdout.flush)` plus explicit flush in error paths (NFR-063).

**Realizes**: NFR-060/061/062/063, P-04.

---

## C-04 — `RedactionProcessor`

**Purpose**: structlog processor implementing the redaction pipeline (P-03).

**Public interface**:
```python
class RedactionProcessor:
    DENY_KEYS: frozenset[str] = frozenset({
        "api_key", "token", "secret", "refresh_token",
        "authorization", "email", "telegram_chat_id",
    })
    SECRET_PATTERN: re.Pattern = re.compile(
        r"(?i)\b(authorization|bearer|token|secret|api[_-]?key|refresh[_-]?token)"
        r"\s*[:=]\s*[^\s,;'\"]+"
    )

    def __call__(self, logger, method_name, event_dict: dict) -> dict: ...
```

**Behavior** (P-03):
- Recursive on `dict` keys (case-insensitive match against `DENY_KEYS`).
- Recursive on `list`/`tuple` element-by-element.
- For matched keys: replace value with `f"***(len={len(str(value))})"`.
- For free-form strings (in lists or `message`): apply `SECRET_PATTERN` substitution.
- Idempotent (PBT-009): repeated application is a no-op.

**Dependencies**: stdlib only (`re`).

**Realizes**: NFR-032/037, P-03, PBT-009..011.

---

## C-05 — `SupabaseClient`

**Purpose**: Thin wrapper around `supabase-py` v2 with retry, error classification, and structured logging.

**Public interface**:
```python
class SupabaseClient:
    def __init__(self, url: str, service_key: str, retry: RetryExecutor, log: BoundLogger): ...

    def select_one(self, table: str, *, eq: dict[str, Any]) -> dict | None: ...
    def select_many(self, table: str, *, eq: dict[str, Any] | None = None,
                    order: str | None = None, limit: int | None = None) -> list[dict]: ...
    def insert(self, table: str, row: dict) -> dict: ...
    def update_where(self, table: str, *, eq: dict, set_: dict, returning: bool = True) -> list[dict]: ...
    def rpc(self, function: str, params: dict) -> Any: ...
    def aggregate_sum(self, table: str, *, column: str, eq: dict) -> Decimal: ...
```

**Dependencies**: `supabase` v2 (sync), `RetryExecutor` (C-07) with `STORAGE_DEFAULT` profile.

**Error mapping**: HTTPError 5xx / network → `Retryable` → wrapped in `RetryableStorageError` after exhaustion. 4xx (except 408/429) → `TerminalStorageError`. Unique-violation 23505, RLS 42501 → `Terminal` (short-circuit).

**Service-role boundary**: only this class holds the service-role key (NFR-034). Constructed once per process from `SecretsProvider`.

**Realizes**: NFR-014/020/021/050/051, P-10.

---

## C-06 — `R2Client`

**Purpose**: Wrap `boto3` S3 client against the R2 endpoint with retry + multipart configuration.

**Public interface**:
```python
class R2Client:
    def __init__(self, endpoint: str, access_key: str, secret_key: str,
                 bucket: str, retry: RetryExecutor, log: BoundLogger): ...

    def put(self, key: str, body: BinaryIO | bytes, content_type: str) -> ArtifactRef: ...
    def get(self, key: str) -> bytes: ...
    def head(self, key: str) -> ArtifactRef | None: ...
    def presigned_url(self, key: str, ttl_seconds: int = 3600) -> str: ...
    def delete(self, key: str) -> None: ...
```

**Dependencies**: `boto3` ≥1.34, `RetryExecutor` (C-07) with `STORAGE_DEFAULT`, `TransferConfig(multipart_threshold=16 MiB, multipart_chunksize=8 MiB, max_concurrency=4)` per P-08.

**Realizes**: NFR-012 (p95 ≤ 60s for ~30 MB shorts), NFR-013 (p95 ≤ 100ms presigned, fully local SigV4), P-08, P-09, P-10.

---

## C-07 — `RetryExecutor`

**Purpose**: Generic exponential-backoff executor with pluggable classifier (P-01).

**Public interface**:
```python
class RetryPolicy(NamedTuple):
    max_attempts: int
    backoff_seq: tuple[float, ...]
    jitter_pct: float = 0.20

STORAGE_DEFAULT = RetryPolicy(3, (0.2, 0.6, 1.2))
LEDGER_CRITICAL = RetryPolicy(5, (0.2, 0.5, 1.5, 4.0, 10.0))

class Classification:
    Retryable: ClassVar
    Terminal: ClassVar
    @dataclass
    class RetryAfter:
        seconds: float

class RetryExecutor:
    def __init__(self, policy: RetryPolicy,
                 classify: Callable[[Exception], Classification],
                 sleep: Callable[[float], None] = time.sleep,
                 log: BoundLogger | None = None): ...

    def run(self, fn: Callable[[], T], *, op_label: str) -> T: ...
```

**Dependencies**: stdlib `time`, `random`.

**Behavior**: on each attempt, catch exception → classify → if `Retryable` and attempts remain, sleep `backoff_seq[i] * (1 ± jitter)` and retry; if `RetryAfter(s)`, sleep `min(s, 10)`; if `Terminal`, raise immediately. After exhaustion, raise `RetryableStorageError(operation=op_label, attempts=N)` with `__cause__` set to last exception (Q6.2).

**Realizes**: NFR-050/051/052, P-01, P-02, PBT-040..042.

**Testability**: inject `sleep` to verify wall-time bounds without actual delays.

---

## C-08 — `CostLedger`

**Purpose**: Append-only ledger of paid-API calls; budget-governance read path.

**Public interface**:
```python
class CostLedger:
    def __init__(self, supabase: SupabaseClient, retry: RetryExecutor, log: BoundLogger): ...

    def record(self, entry: LedgerEntry) -> None: ...
    def month_spend_all_providers(self, channel_id: ChannelId,
                                   month: date | None = None) -> Decimal: ...
    def month_spend_by_bucket(self, channel_id: ChannelId,
                               bucket: CostBucket,
                               month: date | None = None) -> Decimal: ...
```

**`record`** uses a dedicated `RetryExecutor(LEDGER_CRITICAL)` (P-02). Failure → `TerminalStorageError`. No local-file fallback (NFR Requirements §9 deferral).

**`month_spend_*`** uses `SupabaseClient.aggregate_sum` against `cost_ledger` filtered on `(channel_id, month_bucket)` (P-07). Returns `Decimal('0')` when no rows.

**Realizes**: NFR-011/052/093, P-07, PBT-020..022.

**Schema requirement** (deferred to Infrastructure Design): `cost_ledger.month_bucket` generated column + composite index `(channel_id, month_bucket)`.

---

## C-09 — `RunRecorder`

**Purpose**: Lifecycle tracking for `PipelineRun` and `StageRecord` with monotonic state guard (P-12).

**Public interface**:
```python
class RunRecorder:
    def __init__(self, supabase: SupabaseClient, log: BoundLogger): ...

    def start_run(self, run_id: str, channel_id: ChannelId,
                  pipeline: PipelineId, scheduled_slot: datetime | None,
                  trigger: TriggerKind, force_retry_of: str | None = None) -> PipelineRun: ...

    def mark_succeeded(self, run_id: str, outcome: str | None = None) -> None: ...
    def mark_failed(self, run_id: str, outcome: str | None = None) -> None: ...
    def mark_skipped(self, run_id: str, outcome: str | None = None) -> None: ...
    def mark_canceled(self, run_id: str, outcome: str | None = None) -> None: ...

    def open_stage(self, run_id: str, stage_name: str, sequence: int) -> StageRecord: ...
    def close_stage(self, run_id: str, stage_name: str,
                    status: Literal["ok", "error", "skipped"],
                    artifacts: list[ArtifactRef] | None = None,
                    error: ErrorRecord | None = None) -> None: ...
    def increment_attempt(self, run_id: str, stage_name: str) -> int: ...
```

**Each `mark_*`** issues a single `UPDATE ... WHERE state='started' RETURNING run_id`. Zero rows → `IdempotencyConflict(existing_run_id=run_id)` (P-12).

**Realizes**: NFR-014/055, P-12, PBT-030..033.

---

## C-10 — `IdempotencyGuard`

**Purpose**: Pure derivation of `run_id` from invocation context (P-11).

**Public interface**:
```python
class IdempotencyGuard:
    @staticmethod
    def canonicalize(slot: datetime) -> str: ...   # ISO-8601 with offset, minute-truncated

    @staticmethod
    def run_id_for(channel_id: ChannelId,
                   pipeline: PipelineId,
                   scheduled_slot: datetime | None,
                   idempotency_key: str | None = None) -> str: ...
```

**Behavior**: SHA-256 of `f"{channel_id}|{pipeline}|{slot_part}"`, hex-encoded, first 24 chars (P-11).

**Validation**: `ValueError` if both `scheduled_slot` and `idempotency_key` are `None` (Q7.2 a+c safety).

**No I/O** — fully pure, fully PBT-tested.

**Realizes**: NFR-054, P-11, PBT-001/002/006..008.

---

## Bootstrap (Wiring)

`reel_mind.u1.bootstrap.build_runtime(service: str) -> Runtime`:

```python
@dataclass(frozen=True)
class Runtime:
    config_loader: ConfigLoader
    secrets: SecretsProvider
    log: BoundLogger
    supabase: SupabaseClient
    r2: R2Client
    cost: CostLedger
    runs: RunRecorder
    idempotency: type[IdempotencyGuard]   # static-only, no instance state
```

Construction order (P-10):
1. `init_logger(service)` → bound logger
2. `SecretsProvider()` (reads env on demand)
3. `SupabaseClient(url, service_key=secrets.get(None, "SUPABASE_SERVICE_KEY"), retry=RetryExecutor(STORAGE_DEFAULT, classify_supabase, log=log), log=log)`
4. `R2Client(endpoint, access_key, secret_key, bucket, retry=RetryExecutor(STORAGE_DEFAULT, classify_r2, log=log), log=log)`
5. `CostLedger(supabase, retry=RetryExecutor(LEDGER_CRITICAL, classify_supabase, log=log), log=log)`
6. `RunRecorder(supabase, log=log)`
7. `ConfigLoader(supabase)`

All clients constructed lazily — no network call until first use (NFR-015 cold-start ≤ 1.5s).

---

## NFR → Component Realization Matrix

| NFR | Component(s) | Pattern(s) |
|-----|--------------|-----------|
| 001 (10 channels steady) | (architectural — no contention via P-10) | P-10 |
| 002 (5-burst) | (process-level via GHA matrix) | P-10 |
| 003 (no global singletons) | C-05, C-06 | P-10 |
| 010 (config p95) | C-01 | P-06 |
| 011 (ledger sum p95) | C-08 | P-07 |
| 012 (R2 put p95) | C-06 | P-08 |
| 013 (presigned p95) | C-06 | P-09 |
| 014 (run record p95) | C-05, C-09 | P-10 |
| 015 (cold-start) | bootstrap | P-10 |
| 020/021/022 (availability/fail-fast) | C-05, C-06 + caller | P-14 |
| 030..033, 037..039 (security) | C-02 | P-05 |
| 035, 036 (validation) | C-01, C-08, C-09 | P-06 |
| 050, 051 (retry) | C-07 | P-01 |
| 052 (critical-write retry) | C-08 (uses C-07 with `LEDGER_CRITICAL`) | P-02 |
| 053 (error contract) | (all error classes in `reel_mind.u1.errors`) | P-13 |
| 054 (idempotency) | C-10 | P-11 |
| 055 (run-state monotonic) | C-09 | P-12 |
| 060..063 (observability) | C-03 | P-04 |
| 032, 037 (redaction) | C-04 | P-03 |
| 070..074 (maintainability) | (CI gates, not components) | — |
| 091 (PBT pure) | C-04, C-10 | PBT-001..011 |
| 092 (PBT state machines) | C-09 | PBT-030..033 |
| 093 (PBT decimal) | C-08 | PBT-020..022 |

---

## Cross-References

- Patterns: `nfr-design-patterns.md`
- NFRs: `aidlc-docs/construction/U1/nfr-requirements/nfr-requirements.md`
- Functional model: `aidlc-docs/construction/U1/functional-design/`
- Schema decisions deferred to Infrastructure Design.
