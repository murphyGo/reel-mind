# Units of Work

Units are construction-sized slices. Each unit goes through the per-unit construction loop (Functional Design → NFR Req → NFR Design → Infrastructure Design → Code Gen → Build & Test).

| ID | Name | Scope | MVP | Est. effort |
|----|------|-------|-----|-------------|
| U1 | Shared Foundation | Supabase schema + migrations; `ConfigLoader`, `SecretsProvider`, `SupabaseClient`, `R2Client`, `Logger`, `CostLedger`, `RunRecorder`, `IdempotencyGuard`; `config/defaults.yaml` | ✅ | L |
| U2 | Adapter Framework | `AdapterRegistry` + interface definitions for Source / GenerativeVideo / TTS / StockMedia / Publish; `RetryPolicy`; reference mocks for tests | ✅ | M |
| U3 | Pipeline A — Style Study | `StyleStudyOrchestrator`, `SampleCollector`, `StyleExtractor`, `StyleProfileRepository`; Claude Opus prompts; GHA workflow `pipeline-a.yml` | Post-MVP (v1) | M |
| U4 | Pipeline B — Content Production | `ContentProductionOrchestrator`, `TrendScout`, `VideoPlanner`, `BudgetGovernor`, `AssetAssemblyEngine`, `GenerativeSceneRouter`, `FfmpegComposer`, `ApprovalGate`, `PostingSchedulerGuard`, `Publisher`; YouTube Shorts publish adapter impl; one Korean TTS adapter impl; one stock-media adapter impl; one trend-source adapter impl; GHA workflow `pipeline-b.yml` | ✅ (critical path) | XL |
| U5 | Pipeline C — Measure & Learn | `MeasureOrchestrator`, `MetricsIngestor`, `SignalUpdater`; YouTube metrics fetch; GHA workflow `pipeline-c.yml` | Post-MVP (v1) | M |
| U6 | Telegram Bot | `AlertPublisher`, `ApprovalBot` with inline buttons; operator-chat whitelist; long-poll or webhook worker | ✅ | M |
| U7 | Web UI | Next.js 15 scaffold; Supabase Auth gate; `ChannelsOverview` + `ApprovalQueueView` for MVP; stub screens for `PipelineRunsTimeline`, `MetricsDashboardView`, `ConfigEditor`, `BudgetView` | ✅ (minimal MVP subset) | L |
| U8 | Orchestration | GHA workflow files (pipeline-a/b/c), cron definitions, matrix config driven by active channels, secrets-layout docs, repo conventions, CI for tests, Vercel deploy wiring | ✅ | M |

## Unit content split clarifications

- **U3 & U5 are marked post-MVP** — they ship in v1 (right after MVP walking skeleton). The MVP skeleton (U1+U2+U4+U6+U7+U8) can run with a **bootstrap StyleProfile** authored manually and no automated learning loop. This de-risks the approval-gated first publish.
- **U4 is the largest unit by far.** It may be internally phased during Functional Design (see U4 note below) but remains a single construction unit for plan tracking.
- **Generative video is opt-in within U4**, not a separate unit. A generative-video adapter impl is deferred to v1.5 (after the walking skeleton publishes its first asset-assembly video).

## U4 internal phasing (hint for Functional Design)

| Phase | Content |
|-------|---------|
| U4.a | Trend scout + planner + asset-assembly engine + budget governor + posting scheduler guard |
| U4.b | Approval gate + publisher (depends on U6 shape) |
| U4.c | Generative scene router (deferred; stub in MVP) |

Phasing is a planning hint — a single set of Functional Design / NFR / Code Gen artifacts still covers U4.

## Notes on MVP ship criteria

Walking skeleton is publishable when:
- U1, U2, U4 (through U4.b), U6, U7 (MVP subset), U8 are all construction-complete.
- One Korean-language asset-assembly video has been generated, approved via Telegram, and published to the operator's YouTube Shorts channel.
- Web UI shows the channel status + the just-approved video as published.
- Telegram alert fires on run completion.
