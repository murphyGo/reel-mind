# U1 Shared Foundation — Tech Stack Decisions

**Unit**: U1 Shared Foundation
**Stage**: NFR Requirements Assessment
**Created**: 2026-04-14
**Source**: `aidlc-docs/construction/plans/U1-nfr-requirements-plan.md` Q8–Q9
**Companion**: `nfr-requirements.md`

All version pins below are **floors with compatible-release upper bounds** (`~=`) unless noted otherwise. Exact transitive versions are locked via `uv.lock` (NFR-UNIT-U1-DEP-001).

---

## Decision Index

| # | Concern | Choice | Pin | Mode |
|---|---------|--------|-----|------|
| TS-01 | Language runtime | CPython | `>=3.12,<3.13` | — |
| TS-02 | Dependency manager / lockfile | `uv` + `uv.lock` (committed) | latest | enforced in CI |
| TS-03 | Supabase client | `supabase` (`supabase-py` v2) | `~=2.0` | sync |
| TS-04 | Cloudflare R2 client | `boto3` (S3-compatible endpoint) | `~=1.34` | sync |
| TS-05 | Validation / data models | `pydantic` | `~=2.6` | strict mode |
| TS-06 | Structured logging | `structlog` | `~=24.1` | bound-logger, JSON renderer |
| TS-07 | Money / decimals | stdlib `decimal.Decimal` | n/a | `ROUND_HALF_UP` |
| TS-08 | Unique IDs | `python-ulid` | `~=2.2` | — |
| TS-09 | Config file format / parser | `ruamel.yaml` | `~=0.18` | round-trip mode |
| TS-10 | Test runner | `pytest` | `~=8.0` | — |
| TS-11 | Property-based tests | `hypothesis` | `~=6.99` | — |
| TS-12 | Coverage | `pytest-cov` | `~=5.0` | gate ≥90% lines |
| TS-13 | Mocking | `pytest-mock` | `~=3.12` | — |
| TS-14 | Type checker | `mypy` | `~=1.9` | `--strict` |
| TS-15 | Linter / formatter | `ruff` | `~=0.4` | rule sets `E,F,I,B,UP,SIM,RUF,S` |
| TS-16 | External error tracker | none for MVP | — | — |

---

## TS-01 — CPython 3.12.x

- **Choice**: CPython, pinned `>=3.12,<3.13`.
- **Rationale**: Reel-Mind project baseline; PEP 695 type aliases and `typing.override` improve U1's strict-typing ergonomics. Pinning to a single minor avoids surprise typing changes in 3.13.
- **Alternatives**: 3.11 (older typing); 3.13 (too new — wheel availability for some deps unproven).
- **Satisfies**: NFR-UNIT-U1-070 (`mypy --strict`).
- **Re-eval trigger**: 3.13 GA + ≥6 months of wheel maturity.
- **Source**: Q9.2.

---

## TS-02 — `uv` + committed `uv.lock`

- **Choice**: `uv` for env + dependency management. `uv.lock` committed. CI gate: `uv lock --check`.
- **Rationale**: Reproducible builds across GHA / bot host / local dev; deterministic installs for the security baseline (no surprise transitive upgrade introducing a vulnerable package between commits).
- **Alternatives**: `poetry` (slower, heavier), `pip-tools` (less ergonomic for monorepo).
- **Satisfies**: Security Baseline (supply-chain stability), NFR-UNIT-U1-073 (internal-only — fast iteration).
- **Source**: Q9.1.
- **Action item**: `uv.lock` is currently untracked in git (per opening `git status`); commit it as part of U1 Code Generation.

---

## TS-03 — `supabase-py` v2 (sync mode)

- **Choice**: `supabase ~=2.0`, synchronous client.
- **Rationale**: Pipelines are synchronous-per-step; async would force colored-function spread without throughput gain at MVP scale (NFR-UNIT-U1-001).
- **Alternatives**: Raw `postgrest-py` + custom auth (rejected — reinvents the wheel); `asyncpg` direct (rejected — bypasses Supabase RLS conventions).
- **Satisfies**: NFR-UNIT-U1-010 (config p95), NFR-UNIT-U1-011 (ledger sum p95), NFR-UNIT-U1-014 (run record latency).
- **Source**: Q8.1.

---

## TS-04 — `boto3` against R2 S3-compatible endpoint

- **Choice**: `boto3 ~=1.34` configured with R2 endpoint URL + access keys via `SecretsProvider`.
- **Rationale**: Industry-standard S3 client; well-tested multipart upload + SigV4 signing; matches synchronous library shape.
- **Alternatives**: `aiobotocore` (rejected — async colors), `cloudflare`-specific SDK (less mature for object storage).
- **Satisfies**: NFR-UNIT-U1-012 (R2 put p95), NFR-UNIT-U1-013 (presigned URL p95 — local SigV4).
- **Source**: Q8.2.
- **Note**: Multipart threshold to be specified in NFR Design (probably 8 MiB part size).

---

## TS-05 — `pydantic` v2 (strict)

- **Choice**: `pydantic ~=2.6`. All public-API inputs validated through Pydantic models. Use `model_config = ConfigDict(strict=True, extra='forbid')`.
- **Rationale**: Industry default for Supabase-adjacent Python; runtime validation closes the gap that `mypy --strict` cannot (external data crossing process boundary).
- **Alternatives**: `attrs + cattrs` (smaller community for this use case), msgspec (faster but smaller ecosystem).
- **Satisfies**: NFR-UNIT-U1-035 (input validation at every public API), NFR-UNIT-U1-036 (channel_id allow-list).
- **Source**: Q8.3.

---

## TS-06 — `structlog` with bound-logger + JSON renderer

- **Choice**: `structlog ~=24.1`. Bound-logger pattern matches `logger.bind(channel_id=..., run_id=...)` already specified in functional design.
- **Rationale**: Cleanest API for context propagation; built-in JSON renderer; processor pipeline gives a natural place to insert the redaction processor (NFR-UNIT-U1-032).
- **Alternatives**: stdlib `logging` + custom JSON formatter (rejected — bind ergonomics worse), `loguru` (rejected — less suited to JSON-first output).
- **Satisfies**: NFR-UNIT-U1-060 (single format), NFR-UNIT-U1-061 (mandatory fields), NFR-UNIT-U1-032 (redaction pipeline), NFR-UNIT-U1-063 (flush on uncaught).
- **Source**: Q8.4.

---

## TS-07 — `decimal.Decimal` for money

- **Choice**: stdlib `decimal.Decimal`. `getcontext().rounding = ROUND_HALF_UP`. Internal precision: 6 decimal places (unit cost). Display / external storage of USD totals: 2 decimal places.
- **Rationale**: Float arithmetic is forbidden for budget code (NFR-UNIT-U1-093 requires bit-exact PBT); stdlib avoids extra dep; Postgres `numeric(12,6)` round-trips cleanly.
- **Alternatives**: `money` library (rejected — overkill, no multi-currency in MVP).
- **Satisfies**: NFR-UNIT-U1-093 (PBT decimal arithmetic).
- **Source**: Q8.5.

---

## TS-08 — `python-ulid` for `LedgerEntry.entry_id`

- **Choice**: `python-ulid ~=2.2`.
- **Rationale**: Sortable IDs make ledger queries (`ORDER BY entry_id` ≈ `ORDER BY timestamp`) cheap; compact (26 chars) for log readability.
- **Alternatives**: UUIDv7 via `uuid7` (newer, smaller ecosystem); UUIDv4 (not sortable).
- **Satisfies**: Functional Design `LedgerEntry.entry_id`.
- **Source**: Q8.6.

---

## TS-09 — `ruamel.yaml` (round-trip)

- **Choice**: `ruamel.yaml ~=0.18`, round-trip mode for `config/defaults.yaml` reads/writes.
- **Rationale**: Preserves operator comments and key ordering on round-trips — important for human-edited config.
- **Alternatives**: `pyyaml` (drops comments), `tomli`/TOML (would require config rewrite; out of scope).
- **Satisfies**: Functional Design `ConfigLoader`.
- **Source**: Q8.7.

---

## TS-10..13 — Test stack: `pytest` + `hypothesis` + `pytest-cov` + `pytest-mock`

- **Choice**:
  - `pytest ~=8.0` — runner.
  - `hypothesis ~=6.99` — property-based tests (NFR-UNIT-U1-091/092/093).
  - `pytest-cov ~=5.0` — coverage; CI gate at ≥90% lines (NFR-UNIT-U1-072).
  - `pytest-mock ~=3.12` — concise `mocker` fixture for Supabase / R2 client mocking.
- **Excluded for now**: `pytest-asyncio` (no async code in U1).
- **Source**: Q8.8.

---

## TS-14 — `mypy --strict`

- **Choice**: `mypy ~=1.9`, run with `--strict` from day 1. CI gate.
- **Rationale**: Strict typing catches a large class of issues at PR time; cheaper to start strict than to retrofit.
- **Satisfies**: NFR-UNIT-U1-070.
- **Source**: Q7.1.

---

## TS-15 — `ruff` with `E,F,I,B,UP,SIM,RUF,S`

- **Choice**: `ruff ~=0.4`. Rule sets: `E` (pycodestyle), `F` (pyflakes), `I` (isort), `B` (bugbear), `UP` (pyupgrade), `SIM` (simplify), `RUF` (ruff-specific), `S` (bandit-style security).
- **Rationale**: `S` set adds security linting (e.g. `S105` hard-coded password, `S324` weak hash) — directly supports the Security Baseline extension.
- **Satisfies**: NFR-UNIT-U1-071, contributes to NFR-UNIT-U1-030/033 (no hard-coded secrets).
- **Note**: `ruff format` replaces black for formatting.
- **Source**: Q7.2.

---

## TS-16 — No external error tracker

- **Choice**: No Sentry, Honeybadger, Rollbar, or equivalent in MVP.
- **Rationale**: Stdout JSON + GHA log retention is sufficient at solo-operator / 1-channel scale.
- **Satisfies**: NFR-UNIT-U1-074.
- **Re-eval trigger**: ≥3 missed-in-log production errors per week.
- **Source**: Q8.9.

---

## Summary `pyproject.toml` excerpt (illustrative — not the source of truth)

```toml
[project]
requires-python = ">=3.12,<3.13"
dependencies = [
  "supabase~=2.0",
  "boto3~=1.34",
  "pydantic~=2.6",
  "structlog~=24.1",
  "python-ulid~=2.2",
  "ruamel.yaml~=0.18",
]

[dependency-groups]
dev = [
  "pytest~=8.0",
  "hypothesis~=6.99",
  "pytest-cov~=5.0",
  "pytest-mock~=3.12",
  "mypy~=1.9",
  "ruff~=0.4",
]

[tool.mypy]
strict = true
python_version = "3.12"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM", "RUF", "S"]
```

The authoritative `pyproject.toml` and `uv.lock` are produced in U1 Code Generation.

---

## Cross-references

- Each NFR-UNIT-U1-### that constrains a library choice is cited in the **Satisfies** field above.
- Out-of-scope stack picks (Sentry, async runtime, local fallback queue) are catalogued in `nfr-requirements.md` §9.
