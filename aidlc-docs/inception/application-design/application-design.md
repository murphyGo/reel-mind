# Application Design: Reel-Mind

**Generated**: 2026-04-13
**Source of truth for detailed design**: this directory (`aidlc-docs/inception/application-design/`)
**Developer summary**: `docs/DESIGN.md`

## Purpose

This document synthesizes the components, methods, services, and dependencies for Reel-Mind into an architectural narrative. See the sibling files for detailed tables:
- `components.md` — all components by layer
- `component-methods.md` — key method signatures
- `services.md` — external services + secrets layout
- `component-dependency.md` — dependency rules + build order

## Architectural narrative

Reel-Mind is organized into **three independently-scheduled Python pipelines** (Style Study / Content Production / Measure & Learn), each driven by a **single long-running Claude Agent SDK session per run**. Pipelines communicate only through **Supabase rows and Cloudflare R2 artifacts** — never in-memory, never by direct RPC.

Above the pipelines sit two **operator surfaces**:
- A **Next.js Web UI** on Vercel for pull-side observability and config/approval writes.
- A **Telegram bot** for push-side alerts and mobile approval.

Both surfaces only read/write the shared Supabase state; they have no direct knowledge of pipeline internals.

All external providers (trend sources, TTS, stock media, generative video, publishing platforms) are **pluggable adapters** conforming to versioned interfaces defined in the Adapter Framework. Adding a channel is a config-row insert + GHA secret provision; adding a provider is a new adapter class.

Pipelines run on **GitHub Actions** — one workflow per pipeline, matrix over active channels. Per-channel credentials are stored exclusively as GHA encrypted secrets with the naming convention `{KIND}_{PROVIDER}_CHANNEL_{id}`. Secrets are never persisted in Supabase or in code.

## Core data entities (to be formalized in Functional Design + Infrastructure Design)

| Entity | Key fields |
|--------|-----------|
| `channels` | id, subject, platform, language, posting_schedule, approval_mode, generative_video_budget_cap, warmup_phase, active, created_at |
| `pipeline_runs` | id, channel_id, pipeline, run_id (deterministic), trigger, status, started_at, finished_at |
| `pipeline_stages` | run_id, stage, status, started_at, finished_at, artifacts (jsonb), error |
| `style_profiles` | id, channel_id, version, features (jsonb), samples_ref, created_at — immutable |
| `trend_candidates` | id, channel_id, run_id, source_name, payload, score, picked_bool |
| `video_plans` | id, channel_id, run_id, trend_id, style_profile_version, plan (jsonb), plan_hash |
| `generated_videos` | id, plan_id, video_artifact_ref, audio_artifact_ref, cost_breakdown |
| `approval_requests` | id, video_id, channel_id, state {pending, approved, rejected, edit_requested, timed_out}, decided_by, decided_at, notes |
| `published_videos` | id, video_id, platform, platform_id, published_at, ai_disclosure |
| `metrics_snapshots` | id, published_id, captured_at, followers_delta, views, watch_time, revenue |
| `style_signals` | channel_id, feature_key, weight, updated_at |
| `trend_signals` | channel_id, topic_key, weight, updated_at |
| `cost_ledger` | id, channel_id, pipeline, run_id, provider, units, usd_cost, created_at |

## Key design decisions

| # | Decision | Source |
|---|----------|--------|
| AD-01 | GHA workflow-per-pipeline × matrix-over-channels | Q1 |
| AD-02 | One Claude Agent SDK session per pipeline run | Q2 |
| AD-03 | Pipelines write-only to Supabase; Web UI reads + writes config/approval; no HTTP middle tier | Q3 |
| AD-04 | Approval state machine: pending → approved / rejected / edit_requested (→ new pending) / timed_out | Q4 |
| AD-05 | Pre-flight cost estimate with fallback to asset-assembly + post-call reconciliation | Q5 |
| AD-06 | Retries live inside adapters (exp backoff, jitter, max 3); pipeline sees terminal outcome only | Q6 |
| AD-07 | Videos retained permanently in R2 | Q7 |
| AD-08 | Per-channel config in Supabase; global defaults in `config/defaults.yaml`; secrets only in GHA | Q8 |
| AD-09 | Opus for creative stages, Haiku for mechanical | Q9 |
| AD-10 | Determinism: `run_id = hash(channel_id, pipeline, scheduled_slot)` ensures idempotent retries and no double-publish | derived from risk analysis |

## Failure isolation design

- Pipeline A failure → Pipeline B falls back to last-known `StyleProfile`.
- Pipeline C failure → signals stale; pipelines run with last-known priors.
- Pipeline B failure mid-run → retry uses the same `run_id`; `IdempotencyGuard` prevents double-publish; partial R2 artifacts are reused where identical, else overwritten.
- Adapter failure → retried inside adapter up to 3x; pipeline records terminal failure; alert fires.
- Channel-level failure (e.g., auth revoked) → that channel marked `stale`; other channels unaffected.
- Budget cap breach → generative scenes auto-fall-back to asset-assembly; alert fires; publishing proceeds.

## Observability contract

Every pipeline run writes:
1. A `pipeline_runs` row at start (status `running`) and finish (`succeeded` / `failed` / `skipped`).
2. A `pipeline_stages` row per stage boundary (status + artifact refs + error if any).
3. `cost_ledger` entries for every paid API call.
4. A `run_summary` event pushed to Telegram on completion.

Stale-channel detection: Web UI query selects channels with no `succeeded` Pipeline B run within `2 × posting_schedule_gap`; surfaces on Channels overview.

## Security posture (Security Baseline extension)

- **Credentials**: GHA secrets only; per-channel keyed; rotation runbook documented at U1 construction.
- **Supabase**: RLS on all tables; Web UI uses user JWT; pipelines use service-role key injected via env.
- **R2**: Private bucket; presigned URLs (15-min TTL) for Web UI previews; pipelines access via long-lived access key scoped to the bucket.
- **Telegram**: Bot restricted to whitelisted `operator_chat_id`; unknown chat callbacks ignored.
- **OAuth tokens**: Refresh-token flow; refresh failures page operator; never logged in plaintext.
- **Input validation**: All adapter boundaries validate inputs; user-input (config editor) sanitized at Supabase write.

## PBT posture (Property-Based Testing extension, full)

Targeted property coverage (to be designed per-unit):
- `IdempotencyGuard.run_id_for` — deterministic, collision-free across realistic inputs.
- `CostLedger.month_spend` / `remaining_budget` — additive, non-negative, correct across month boundaries.
- `BudgetGovernor.preflight` — for any plan, either approved plan stays within cap or fallbacks are applied; never emits an over-cap approval.
- `PostingSchedulerGuard.is_slot_allowed` — warmup transition is monotonic in channel age.
- `StyleProfile` serialization — round-trip identity.
- `ApprovalGate` state transitions — only valid transitions accepted; terminal states stay terminal.
- Plan `plan_hash` — deterministic canonical serialization.

## Open design questions (deferred to per-unit Functional Design)

- Exact StyleFeatures schema (enumerate feature keys).
- TTS provider selection for Korean quality.
- Generative-video provider for v1 opt-in path.
- Trend-source roster for Korean shorts (2 default adapters).
- Heavy-render offload trigger threshold (precise minutes-of-projected-render).
