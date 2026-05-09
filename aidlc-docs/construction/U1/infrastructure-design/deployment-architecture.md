# U1 Shared Foundation — Deployment Architecture

**Unit**: U1 Shared Foundation
**Stage**: Infrastructure Design
**Created**: 2026-05-10
**Companion**: `infrastructure-design.md`

This document describes how U1 is deployed and used at runtime. U1 is a shared Python library, not a standalone service. The deployment architecture is therefore the shape of the processes that import U1 and the managed infrastructure they access.

---

## 1. Runtime Topology

```text
GitHub Actions pipeline jobs
  -> U1 Python library
  -> Supabase Postgres/PostgREST
  -> Cloudflare R2
  -> stdout JSON logs captured by GitHub Actions

Telegram bot host
  -> U1 Python library
  -> Supabase Postgres/PostgREST
  -> Cloudflare R2 for preview refs when needed
  -> stdout JSON logs captured by bot host

Operator ops scripts
  -> U1 Python library
  -> Supabase Postgres/PostgREST
  -> Cloudflare R2
  -> local stdout JSON logs

Next.js Web UI
  -> Supabase client with user auth and RLS
  -> R2 presigned URLs generated server-side in U7
  -> Vercel logs
```

There is no HTTP API between pipelines and the Web UI. Supabase rows and R2 objects are the integration boundary.

---

## 2. Pipeline Job Flow

Pipeline jobs run on GitHub-hosted runners in MVP.

1. GitHub Actions starts a matrix job for one `(pipeline, channel_id)` pair.
2. The job checks out the repository and installs Python `>=3.12,<3.13` dependencies from `uv.lock`.
3. Environment variables are injected from GitHub Actions encrypted secrets.
4. U1 bootstrap constructs:
   - `Logger`
   - `SecretsProvider`
   - `SupabaseClient`
   - `R2Client`
   - `ConfigLoader`
   - `RunRecorder`
   - `CostLedger`
   - `IdempotencyGuard`
5. `ConfigLoader` reads `config/defaults.yaml` and the Supabase `channels` row.
6. `RunRecorder.start_run` inserts a `pipeline_runs` row.
7. Pipeline-specific code writes `stage_records`, `cost_ledger`, and R2 artifacts through U1.
8. On terminal outcome, `RunRecorder.finish_run` updates `pipeline_runs`.
9. The job exits zero on success or non-zero on unhandled failure.

Failure behavior:
- Storage failures retry through `RetryExecutor`.
- Exhausted storage failures surface as U1 exceptions and fail the job.
- There is no local queue or spool.

---

## 3. Telegram Bot Flow

The exact bot host is deferred to U6, but U1 requires the host to provide:

- Python `>=3.12,<3.13`
- U1 package and locked dependencies
- Bot-host environment variables using the canonical `REEL_MIND_*` secret layout
- stdout capture for JSON logs
- Network egress to Supabase and Cloudflare R2

Bot process responsibilities that touch U1:
- Read approval-related Supabase rows.
- Write approval decisions and alert delivery state through U1/Supabase wrappers where applicable.
- Generate or consume R2 presigned URLs as defined by U6/U7.
- Emit redacted stdout JSON logs.

The bot must not become a general-purpose write path for pipeline internals. It acts only on approval, alert, and operator-command state.

---

## 4. Ops Script Flow

Ops scripts are manual tools for the operator.

Allowed U1 uses:
- Listing active channels.
- Validating channel config.
- Running schema or smoke checks.
- Inspecting run/cost state.
- Generating dry-run IDs and artifact paths.

Ops scripts use the same `SecretsProvider` and logging conventions as pipeline jobs. They must not read secret-shaped environment variables directly.

Synthetic run IDs are used for paid manual operations:

```text
manual-<iso8601_utc>
ops-cron-<iso8601_utc>
```

Global paid calls without a channel attribution are rejected.

---

## 5. Web UI Boundary

The Web UI is not a U1 consumer in MVP. It shares the same Supabase and R2 infrastructure but uses its own Next.js/Supabase client layer.

Boundary rules:
- Web UI uses Supabase anon/JWT credentials, never service-role credentials.
- Web UI RLS policies are designed in U7.
- Web UI can read pipeline state and write config/approval state according to RLS.
- Pipelines do not call a Web UI API.
- U1 does not expose a public HTTP endpoint.

This preserves the project invariant that pipelines communicate only through persisted state.

---

## 6. Secrets Injection

GitHub Actions:
- Production jobs use production `REEL_MIND_*` secrets.
- Staging jobs use staging `REEL_MIND_*` secrets and staging infrastructure.
- Matrix `channel_id` values are not secret and may appear in logs.

Bot host:
- Uses the same logical secret names.
- Host-specific secret storage is selected in U6.

Local:
- Uses an untracked local env file or shell environment.
- Local tests should prefer mocks unless explicitly targeting staging.

Secret values are resolved only by `SecretsProvider`. Logs may include env var names for diagnostics but never values.

---

## 7. Data and Artifact Flow

Pipeline B example:

```text
start_run(channel_id, "B", scheduled_slot)
  -> pipeline_runs row

trend_scout / plan / assemble stages
  -> stage_records rows
  -> R2 objects under channels/{channel_id}/runs/{run_id}/...

paid provider calls
  -> cost_ledger rows

approval/publish outcome
  -> stage_records rows
  -> pipeline_runs terminal state
```

R2 artifacts are referenced by immutable `ArtifactRef` objects stored in Supabase rows. Supabase stores metadata and lineage; R2 stores binary payloads.

---

## 8. Environment Isolation

Staging and production are isolated at both storage layers:

| Layer | Staging | Production |
|-------|---------|------------|
| Supabase | Separate project | Separate project |
| R2 | Separate bucket | Separate bucket |
| Secrets | Separate GitHub Actions secrets | Separate GitHub Actions secrets |
| Logs | Separate workflow runs / host logs | Separate workflow runs / host logs |

Local runs use mocks by default. Any local run pointed at staging must require explicit environment selection so test writes are not accidental.

---

## 9. Observability Flow

U1 emits stdout JSON in every process:

- GitHub Actions captures pipeline logs.
- Bot host captures bot logs.
- Local shell captures ops logs.
- Vercel captures Web UI logs separately.

U1 does not write logs to Supabase. Durable run status lives in `pipeline_runs` and `stage_records`; verbose diagnostic detail lives in environment-native log streams.

Logs-as-metrics events use:

```json
{
  "metric_name": "cost_ledger_recorded",
  "metric_type": "counter",
  "metric_value": 1
}
```

---

## 10. Deployment Constraints for Code Generation

Code Generation must keep U1 deployable as an importable Python package. It should not add:

- A web server
- A worker daemon
- A queue consumer
- A custom metrics backend
- A local persistence fallback for failed storage writes

The only runtime side effects U1 should perform are calls explicitly requested by its public methods: Supabase reads/writes, R2 object operations, stdout logging, and deterministic local computation.
