# Components

Components are grouped by **layer**. The first five layers are Python (pipelines + shared). The Web UI layer is TypeScript/Next.js. The Orchestration layer is YAML (GHA).

## Layer 1 — Shared Foundation (U1)

| Component | Responsibility |
|-----------|---------------|
| `ConfigLoader` | Loads `config/defaults.yaml` (repo) and per-channel rows from `channels` table; merges into a validated `ChannelConfig` object |
| `SecretsProvider` | Resolves per-channel secret names (e.g. `YT_REFRESH_TOKEN_CHANNEL_<id>`) from environment (populated by GHA secrets); never reads from DB |
| `SupabaseClient` | Thin wrapper over `supabase-py`; enforces schema-validated writes; RLS-aware |
| `R2Client` | S3-compatible client for artifact upload/download/presigned URLs |
| `Logger` | Structured JSON logger with binding for `(channel_id, pipeline, run_id, stage)` context |
| `CostLedger` | Records every paid API call with `(channel_id, pipeline, run_id, provider, units, usd_cost)`; queries monthly spend per channel per provider |
| `RunRecorder` | Creates `pipeline_runs` row at stage boundaries, records stage status and artifacts |
| `IdempotencyGuard` | Generates deterministic `run_id` from `(channel_id, pipeline, scheduled_slot)`; prevents double-publish on retry |

## Layer 2 — Adapter Framework (U2)

| Component | Responsibility |
|-----------|---------------|
| `AdapterRegistry` | Resolves adapter by `(kind, name)` from config; initializes with channel-scoped secrets |
| `SourceAdapter` (interface) | `fetch_trending(subject, language, now) -> list[TrendCandidate]` — implemented by YouTube Trending, Google Trends KR, Naver DataLab, etc. |
| `GenerativeVideoAdapter` (interface) | `estimate_cost(scene_spec)`, `generate(scene_spec) -> VideoClipRef` — implemented by Sora, Veo, Runway, Kling adapters |
| `TTSAdapter` (interface) | `synthesize(text, voice, language) -> AudioRef` — Korean-quality providers |
| `StockMediaAdapter` (interface) | `search(query, media_type) -> list[MediaRef]` — Pexels, Pixabay, etc. |
| `PublishAdapter` (interface) | `upload(video_ref, metadata) -> PublishedRef`, `refresh_token()`, `disclose_ai_content(flag)` — YouTube Shorts MVP; IG/TikTok later |
| `RetryPolicy` | Applied by every adapter: exp backoff, jitter, max 3 attempts, terminal error classification |

## Layer 3 — Pipeline A: Style Study (U3)

| Component | Responsibility |
|-----------|---------------|
| `StyleStudyOrchestrator` | Claude Agent SDK session driving the full pipeline A run |
| `SampleCollector` | Uses `SourceAdapter` to pull top-performing shorts matching the channel's subject; stores samples in R2 |
| `StyleExtractor` | Claude-powered feature extraction → `StyleProfile.features` (length distribution, cut pacing, subtitle style, BGM genre, hook patterns, CTA patterns) |
| `StyleProfileRepository` | Persists versioned `StyleProfile` rows; enforces immutability; exposes `latest_for(channel_id)` |

## Layer 4 — Pipeline B: Content Production (U4)

| Component | Responsibility |
|-----------|---------------|
| `ContentProductionOrchestrator` | Claude Agent SDK session driving the full pipeline B run |
| `TrendScout` | Calls configured `SourceAdapter`s; ranks candidates; filters by subject lock; returns `TrendCandidate` |
| `VideoPlanner` | Claude-powered plan synthesis; pins `style_profile_version`; tags each scene `asset_assembly` or `generative` |
| `BudgetGovernor` | Pre-flight: sums planned generative-scene cost vs. remaining monthly cap; downgrades scenes if needed. Post-call: reconciles actuals via `CostLedger` |
| `AssetAssemblyEngine` | TTS + stock media + ffmpeg composition + captions + BGM |
| `GenerativeSceneRouter` | Routes tagged scenes to the configured `GenerativeVideoAdapter`; merges output into assembly |
| `FfmpegComposer` | Mechanical video assembly; shared by asset and generative paths |
| `ApprovalGate` | Creates `approval_requests` row; waits per channel's `approval_mode` (required / optional+timeout / off); routes to `ApprovalBot` for push |
| `PostingSchedulerGuard` | Enforces per-channel `posting_schedule` + `warmup_phase`; blocks publish outside allowed slots |
| `Publisher` | Invokes `PublishAdapter`; records `PublishedVideo`; triggers `AlertPublisher` on success/failure |

## Layer 5 — Pipeline C: Measure & Learn (U5)

| Component | Responsibility |
|-----------|---------------|
| `MeasureOrchestrator` | Claude Agent SDK session for pipeline C run |
| `MetricsIngestor` | Pulls per-video and per-channel metrics via platform APIs; writes `MetricsSnapshot` rows |
| `SignalUpdater` | Computes `StyleSignal` and `TrendSignal` priors from recent snapshots; Claude-assisted interpretation |

## Layer 6 — Telegram Bot (U6)

| Component | Responsibility |
|-----------|---------------|
| `AlertPublisher` | Posts structured stage summaries and exception alerts to operator's Telegram |
| `ApprovalBot` | Sends approval requests with inline buttons (approve/reject/edit); writes operator response back to Supabase |

## Layer 7 — Web UI (U7, Next.js)

| Component | Responsibility |
|-----------|---------------|
| `AuthGate` | Supabase Auth magic-link / GitHub OAuth wrapper |
| `ChannelsOverview` | Per-channel status card (healthy/stale/failing, last publish, next slot, pending approvals, monthly spend) |
| `ApprovalQueueView` | Lists pending approvals; video preview via R2 presigned URL; approve/reject/edit action buttons |
| `PipelineRunsTimeline` | Realtime-updating timeline of A/B/C runs per channel |
| `MetricsDashboardView` | Charts for followers, views, revenue; portfolio and per-channel views |
| `StyleProfileViewer` | Current profile + version history per channel |
| `TrendCandidatesView` | What scout found, what was picked |
| `ConfigEditor` | Form for per-channel config fields (FR-012) |
| `BudgetView` | Monthly spend vs. cap per channel per provider |

## Layer 8 — Orchestration (U8)

| Component | Responsibility |
|-----------|---------------|
| `pipeline-a.yml` | GHA workflow; cron; matrix over active channels |
| `pipeline-b.yml` | GHA workflow; cron fans out per posting slot via matrix |
| `pipeline-c.yml` | GHA workflow; daily cron; matrix over active channels |
| `SecretsLayout` | Documented naming convention: `{KIND}_{PROVIDER}_CHANNEL_{id}` (e.g. `YT_REFRESH_TOKEN_CHANNEL_1`) |
| `HeavyRenderDispatcher` | Invoked by `FfmpegComposer` when projected render exceeds GHA budget; offloads to Modal/Runpod (deferred; stub in MVP) |
