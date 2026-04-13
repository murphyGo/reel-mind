# Component Methods

Key public methods for each non-trivial component. Signatures are pseudocode; exact types finalized in Functional Design per unit.

## ConfigLoader
- `load_channel_config(channel_id) -> ChannelConfig`
- `list_active_channels() -> list[str]`
- `validate(config) -> ValidationResult`

## SecretsProvider
- `get(channel_id, key) -> str` — resolves env var name; raises if missing
- `get_with_refresh(channel_id, key, refresh_fn) -> str` — for OAuth tokens

## SupabaseClient
- `insert(table, row, idempotency_key=None) -> Row`
- `query(table, filters, order_by, limit) -> list[Row]`
- `update(table, id, fields) -> Row`
- `subscribe(table, filters, callback)` — Realtime (Web UI only)

## R2Client
- `put(key, bytes, content_type) -> ObjectRef`
- `get(key) -> bytes`
- `presigned_url(key, ttl_seconds) -> str`

## Logger
- `bind(channel_id, pipeline, run_id, stage) -> Logger`
- `info/warn/error(msg, **fields)`

## CostLedger
- `record(channel_id, pipeline, run_id, provider, units, usd_cost, metadata) -> LedgerEntry`
- `month_spend(channel_id, provider, month) -> Decimal`
- `remaining_budget(channel_id, provider, cap_usd) -> Decimal`

## RunRecorder
- `start_run(channel_id, pipeline, trigger) -> run_id`
- `stage(run_id, name, status, artifacts, error?) -> StageRecord`
- `finish_run(run_id, status)`

## IdempotencyGuard
- `run_id_for(channel_id, pipeline, scheduled_slot) -> str` — deterministic hash
- `already_ran(run_id) -> bool`

## AdapterRegistry
- `resolve_source(channel_id) -> list[SourceAdapter]`
- `resolve_publish(channel_id, platform) -> PublishAdapter`
- `resolve_generative(channel_id) -> GenerativeVideoAdapter`
- `resolve_tts(channel_id) -> TTSAdapter`
- `resolve_stock(channel_id) -> StockMediaAdapter`

## SourceAdapter (interface)
- `fetch_trending(subject, language, now) -> list[TrendCandidate]`
- `adapter_name() -> str`

## GenerativeVideoAdapter (interface)
- `estimate_cost(scene_spec) -> Decimal` — pre-flight
- `generate(scene_spec, budget_remaining) -> GeneratedSceneRef`

## TTSAdapter (interface)
- `synthesize(text, voice, language) -> AudioRef`
- `estimate_cost(text) -> Decimal`

## StockMediaAdapter (interface)
- `search(query, media_type, license_filter) -> list[MediaRef]`

## PublishAdapter (interface)
- `upload(video_ref, metadata, ai_disclosure) -> PublishedRef`
- `fetch_metrics(platform_id, since) -> MetricsSnapshot`
- `refresh_token() -> None`

## StyleStudyOrchestrator
- `run(channel_id) -> StyleProfile`

## SampleCollector
- `collect_top_performers(channel_id, subject, sample_size) -> list[SampleRef]`

## StyleExtractor
- `extract(samples) -> StyleFeatures`

## StyleProfileRepository
- `save(channel_id, features) -> StyleProfile` — increments version, immutable
- `latest_for(channel_id) -> StyleProfile`
- `get(channel_id, version) -> StyleProfile`

## ContentProductionOrchestrator
- `run(channel_id, scheduled_slot) -> PublishedVideo | SkippedRun`

## TrendScout
- `pick(channel_id, subject) -> TrendCandidate | None`

## VideoPlanner
- `plan(trend, style_profile, channel_config) -> VideoPlan`

## BudgetGovernor
- `preflight(plan, channel_id) -> BudgetDecision(approved_plan, fallbacks_applied)`
- `reconcile(run_id) -> ReconciliationRecord`

## AssetAssemblyEngine
- `assemble(plan, scenes, audio, bgm) -> VideoRef`

## GenerativeSceneRouter
- `render_scenes(plan) -> list[GeneratedSceneRef]` — routes scenes tagged `generative`

## FfmpegComposer
- `compose(scenes, audio, captions, bgm, format) -> VideoRef`

## ApprovalGate
- `request_approval(channel_id, video_ref, plan) -> ApprovalDecision`
- `wait(approval_id, timeout, default) -> ApprovalOutcome`

## PostingSchedulerGuard
- `is_slot_allowed(channel_id, now) -> bool`
- `next_allowed_slot(channel_id, now) -> datetime`

## Publisher
- `publish(channel_id, video_ref, plan, approval_id) -> PublishedVideo`

## MeasureOrchestrator
- `run(channel_id) -> MeasurementResult`

## MetricsIngestor
- `ingest_pending(channel_id, since) -> list[MetricsSnapshot]`

## SignalUpdater
- `update_style_signals(channel_id) -> StyleSignalUpdate`
- `update_trend_signals(channel_id) -> TrendSignalUpdate`

## AlertPublisher
- `post_run_summary(run_id) -> None`
- `page(severity, message, channel_id?) -> None`

## ApprovalBot
- `send_request(approval_id) -> None`
- `handle_callback(update)` — writes operator response to Supabase

## Web UI (Next.js server components)
- Read paths: Supabase via typed client, RLS-scoped to the single operator
- Write paths: `approveApproval(id)`, `rejectApproval(id, reason)`, `requestEdit(id, notes)`, `updateChannelConfig(id, patch)`, `pauseChannel(id)`
