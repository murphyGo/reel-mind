# Design Document: Reel-Mind

*Generated on 2026-04-13*
*Source of truth: `aidlc-docs/inception/application-design/`*

## Overview

Reel-Mind is an autonomous short-form video content factory. It decomposes the lifecycle into three independently-scheduled Python pipelines — **A: Style Study**, **B: Content Production**, **C: Measure & Learn** — each driven by a single long-running Claude Agent SDK session per run. Pipelines communicate only through persisted artifacts: **Supabase** rows and **Cloudflare R2** blobs. A **Next.js Web UI** (Vercel) and a **Telegram bot** sit on top of the shared state for observability, approval, and configuration.

## Architecture

### High-Level Design

```
+-------------------+       +-------------------+       +-------------------+
|   Pipeline A      |       |   Pipeline B      |       |   Pipeline C      |
|   Style Study     |       |   Production      |       |   Measure + Learn |
+---------+---------+       +---------+---------+       +---------+---------+
          |                           |                           |
          v                           v                           v
+------------------------------------------------------------------------+
|                         Shared Foundation (U1)                         |
|      Supabase (rows)    +    R2 (artifacts)    +    CostLedger         |
+------------------------------------------------------------------------+
          ^                           ^                           ^
          |                           |                           |
+------------------------------------------------------------------------+
|                       Adapter Framework (U2)                           |
|  Source  |  TTS  |  StockMedia  |  GenerativeVideo  |  Publish         |
+------------------------------------------------------------------------+

    +-------------------+       +-------------------+
    |  Telegram Bot     |       |   Web UI          |
    |  (U6)             |       |   Next.js (U7)    |
    +-------------------+       +-------------------+
```

### Components (summary)

| Layer | Key Components | Unit |
|-------|---------------|------|
| Shared Foundation | ConfigLoader, SecretsProvider, SupabaseClient, R2Client, Logger, CostLedger, RunRecorder, IdempotencyGuard | U1 |
| Adapter Framework | AdapterRegistry, SourceAdapter, GenerativeVideoAdapter, TTSAdapter, StockMediaAdapter, PublishAdapter, RetryPolicy | U2 |
| Pipeline A | StyleStudyOrchestrator, SampleCollector, StyleExtractor, StyleProfileRepository | U3 |
| Pipeline B | ContentProductionOrchestrator, TrendScout, VideoPlanner, BudgetGovernor, AssetAssemblyEngine, GenerativeSceneRouter, FfmpegComposer, ApprovalGate, PostingSchedulerGuard, Publisher | U4 |
| Pipeline C | MeasureOrchestrator, MetricsIngestor, SignalUpdater | U5 |
| Telegram Bot | AlertPublisher, ApprovalBot | U6 |
| Web UI | AuthGate, ChannelsOverview, ApprovalQueueView, PipelineRunsTimeline, MetricsDashboardView, StyleProfileViewer, TrendCandidatesView, ConfigEditor, BudgetView | U7 |
| Orchestration | pipeline-a/b/c.yml, SecretsLayout, HeavyRenderDispatcher (stub) | U8 |

Full component list: `aidlc-docs/inception/application-design/components.md`.

## Technical Decisions (AD-01..AD-10)

| ID | Decision | Rationale |
|----|----------|-----------|
| AD-01 | GHA workflow-per-pipeline × matrix-over-channels | Minimal files; scales with channels via config |
| AD-02 | One Claude Agent SDK session per pipeline run | Context continuity across stages |
| AD-03 | Pipelines write-only to Supabase; Web UI reads + writes; no HTTP middle tier | Single shared state store, zero cross-layer coupling |
| AD-04 | Approval state: pending → approved / rejected / edit_requested / timed_out | Handles edit-and-retry without a new pipeline concept |
| AD-05 | Pre-flight cost estimate + post-call reconciliation; fallback to asset-assembly on projected overage | Avoids surprise overruns; preserves publishing |
| AD-06 | Retries live inside adapters (exp backoff + jitter + max 3) | Keeps pipelines clean |
| AD-07 | R2 permanent retention | Cheap; enables cross-posting and re-upload |
| AD-08 | Per-channel config in Supabase; global defaults in `config/defaults.yaml`; secrets only in GHA | Operator-editable behavior + least-privilege credentials |
| AD-09 | Opus 4.6 for creative stages, Haiku 4.5 for mechanical | Cost/quality balance |
| AD-10 | `run_id = hash(channel_id, pipeline, scheduled_slot)` | Idempotent retries; no double-publish |

## Data Model (sketch)

See `aidlc-docs/inception/application-design/application-design.md` §"Core data entities" for the 12-entity list. Finalized schema lands in U1 Functional Design / Infrastructure Design.

## API Design

No public HTTP API. Internal contracts:
- Adapters conform to `AdapterRegistry` interfaces.
- Pipeline ↔ Pipeline communication is via Supabase rows (schema-validated).
- Web UI uses Supabase client SDK with RLS; no custom backend.

## Non-Functional Considerations

### Performance
- Per-run latency tolerates seconds to minutes; pipelines are batch.
- GHA 6h per-job ceiling respected; heavy renders offload to Modal/Runpod when projected to exceed.

### Security (Security Baseline — blocking)
- Per-channel-keyed GHA secrets; never in DB or repo.
- Supabase RLS on all tables; service-role key used only by pipelines.
- R2 private bucket; presigned URLs (15-min TTL) for Web UI previews.
- Telegram bot restricted to whitelisted `operator_chat_id`.
- OAuth refresh flow; refresh failures page operator.

### Observability
- Every run writes `pipeline_runs` + per-stage `pipeline_stages` rows.
- `cost_ledger` entries for every paid call.
- Telegram alerts on failure and kill-switch events within 5 minutes.
- Web UI surfaces stale-channel detection (no successful B run within `2 × schedule_gap`).

### Scalability
- Multi-channel via GHA matrix; no code change to add a channel.
- Pipelines are stateless between runs; state is Supabase + R2.

### Reproducibility (PBT — blocking)
- Deterministic `run_id` + immutable `StyleProfile` versions + `plan_hash` per video plan.
- Property tests target `IdempotencyGuard`, `CostLedger`, `BudgetGovernor`, `ApprovalGate` state transitions, plan/profile serializers.

---

*Update this document as architectural decisions evolve. The AIDLC artifacts under `aidlc-docs/inception/application-design/` remain the source of truth.*
