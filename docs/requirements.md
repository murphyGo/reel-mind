# Project Requirements: Reel-Mind

*Generated via interactive refinement on 2026-04-13*

## 1. Overview

### Problem Statement
Running a portfolio of monetized short-form video channels is labor-intensive: trend research, style-matching, scripting, editing, publishing, and metrics review must happen daily per channel. A solo operator cannot scale past a few accounts. Existing "AI video tools" automate one step but not the full loop, and none continuously adapt to shifting platform trends or manage multiple channels in parallel.

### Target Users
Solo operator (initially the builder) running a portfolio of faceless, single-subject short-form channels.

### Success Metrics
- **Primary**: ~$1,000/month net ad + affiliate revenue from the channel portfolio.
- **Operational**: Zero unhandled pipeline failures go undetected for >24h. System operates 24/7/365 without manual intervention (once per-channel approval mode is flipped off).
- **MVP milestone**: One YouTube Shorts channel (Korean-language) publishing approval-gated, asset-assembly-only videos end-to-end on a fixed KST posting schedule.

## 2. Functional Requirements

### Architecture Overview

The system is organized as **three independent pipelines** plus a **Web UI** and an **Approval/Alert Bot**. Pipelines communicate only through persisted artifacts (Supabase rows + R2 blobs); there is no in-memory coupling.

```
Pipeline A: Style Study       (per channel, slow cadence)
Pipeline B: Content Production (per channel, per posting slot)
Pipeline C: Measure & Learn   (per channel, slow cadence)

Web UI + Telegram Bot sit on top of the shared Supabase state.
```

### FR-001: Style Study Pipeline (Pipeline A)
- **Description**: Per-channel agent that mines top-performing short-form videos in the channel's subject, extracts editing-style features, and persists a versioned `StyleProfile`.
- **User Story**: As the operator, I want the system to continuously learn current short-form editing conventions for each channel so that produced videos match what is currently working on the platform.
- **Acceptance Criteria**:
  - [ ] Runs on a configurable cadence per channel (default: daily).
  - [ ] Produces a `StyleProfile(channel_id, version, created_at, features{length_distribution, cut_pacing, subtitle_style, bgm_genre, hook_patterns, cta_patterns, ...})`.
  - [ ] StyleProfile versions are immutable; history is retained.
  - [ ] Pipeline B pins a specific StyleProfile version per video for reproducibility.
  - [ ] Failure to produce a new profile leaves the previous one usable (graceful degradation).
- **Priority**: Must-have
- **Notes**: Claude Agent SDK drives the extraction step; raw scraped samples are stored in R2.

### FR-002: Trend Scout (in Pipeline B)
- **Description**: Per-channel subject-locked agent that mines viral content, memes, and trend signals from pluggable sources and outputs ranked topic candidates for the next video.
- **Acceptance Criteria**:
  - [ ] Accepts a channel's locked subject as a constraint.
  - [ ] Returns ranked `TrendCandidate` list with source provenance.
  - [ ] Skips the production slot gracefully if no candidates meet a quality threshold.
- **Priority**: Must-have
- **Notes**: Sources are adapter-pluggable (FR-009). MVP: 1–2 initial sources for Korean short-form.

### FR-003: Video Planning (in Pipeline B)
- **Description**: Agent produces a complete production plan from the chosen trend + pinned StyleProfile.
- **Acceptance Criteria**:
  - [ ] Output includes: script, storyboard with per-scene generation-mode tags (asset-assembly vs generative), continuity notes, BGM choice, caption style, thumbnail prompt, title, description, tags, estimated cost.
  - [ ] Plan references `style_profile_version` and `trend_id` for lineage.
  - [ ] Plan passes schema validation before moving to generation.
- **Priority**: Must-have

### FR-004: Hybrid Video Generation (in Pipeline B)
- **Description**: Generates the video from the plan. Default asset-assembly; selected scenes routed to generative-video APIs.
- **Acceptance Criteria**:
  - [ ] Asset-assembly path: LLM script → TTS → stock footage/images → ffmpeg composition → captions → BGM.
  - [ ] Generative path: selected scenes rendered via pluggable generative-video adapter (Sora/Veo/Runway/Kling).
  - [ ] Respects per-channel monthly generative-video budget cap; degrades to asset-assembly when exceeded.
  - [ ] Final artifact uploaded to R2 with full metadata lineage.
- **Priority**: Must-have (asset-assembly MVP); generative routing is v1.
- **Notes**: MVP: Korean-language TTS + Korean subtitles.

### FR-005: Approval Gate (in Pipeline B)
- **Description**: Per-channel configurable gate between generation and publishing.
- **Acceptance Criteria**:
  - [ ] Modes: `required` (human must approve), `optional` (auto-approve after timeout), `off` (fully autonomous).
  - [ ] Approval requests delivered via Telegram bot AND visible in Web UI.
  - [ ] Operator can approve, reject with reason, or request edit (regenerate script/reroll scenes).
  - [ ] Default for new channels: `required`.
  - [ ] Mode flip per channel is a config change, not a code change.
- **Priority**: Must-have

### FR-006: Multi-Platform Publishing (in Pipeline B)
- **Description**: Uploads approved videos via pluggable platform adapters.
- **Acceptance Criteria**:
  - [ ] MVP: YouTube Shorts adapter only.
  - [ ] v2: Instagram Reels adapter; future: TikTok, others.
  - [ ] Adapter handles OAuth token storage/refresh, rate pacing, and AI-content disclosure flags.
  - [ ] Enforces per-channel posting schedule and warmup phase (FR-014).
  - [ ] Persists `PublishedVideo(channel_id, platform_id, published_at, style_profile_version, trend_id, video_artifact_ref, ...)`.
- **Priority**: Must-have (YT adapter); others are later.

### FR-007: Measure & Learn Pipeline (Pipeline C)
- **Description**: Pulls metrics for previously published videos and updates learning priors that feed Pipelines A and B.
- **Acceptance Criteria**:
  - [ ] Runs daily per channel.
  - [ ] Fetches followers, views, watch time, revenue, and per-video performance for videos published >24h ago and not yet fully measured.
  - [ ] Updates `StyleSignal` priors (which style features correlate with performance) consumed by Pipeline A.
  - [ ] Updates `TrendSignal` priors (which topics won) consumed by Pipeline B's trend scout.
  - [ ] Publishes snapshots to Web UI metrics dashboard.
- **Priority**: Must-have

### FR-008: Multi-Channel Orchestration
- **Description**: N independent pipeline sets run concurrently, one per channel, each with its own config, schedule, and state.
- **Acceptance Criteria**:
  - [ ] Channels are data rows, not code (adding a channel = inserting a config row + provisioning secrets).
  - [ ] Failure or cost-cap breach in one channel does not affect others.
  - [ ] MVP: 1 channel (`youtube-kr-1`). Design must support N without refactor.
- **Priority**: Must-have

### FR-009: Pluggable Adapter System
- **Description**: Sources (trend, stock), generative-video providers, and publishing platforms are implemented as adapters conforming to versioned interfaces.
- **Acceptance Criteria**:
  - [ ] Adding a new adapter does not require changes to pipeline core logic.
  - [ ] Adapter selection per channel is config-driven.
- **Priority**: Must-have

### FR-010: Web Dashboard
- **Description**: Single-user web UI for observability, approval actions, and configuration.
- **Acceptance Criteria**:
  - [ ] Screens: Channels overview, Pipeline runs timeline (A/B/C), Approval queue (with video preview), Metrics, Style profile viewer + version history, Trend candidates, Config editor, Cost/budget per channel.
  - [ ] Single-user auth (Supabase Auth).
  - [ ] Real-time updates for approval queue and pipeline run status (Supabase Realtime).
  - [ ] MVP scope: Channels overview + Approval queue must ship with the walking skeleton.
- **Priority**: Must-have (MVP subset); full dashboard is Should-have.

### FR-011: Telegram Alert/Approval Bot
- **Description**: Push-side companion to the Web UI.
- **Acceptance Criteria**:
  - [ ] Pipeline run summary (✅/❌ per stage) posted to an operator channel.
  - [ ] Approval requests pushed with inline approve/reject/edit buttons; links back to Web UI for deep review.
  - [ ] Unhandled exceptions and "no trends found / upload failed / budget exceeded" events page the operator.
- **Priority**: Must-have

### FR-012: Per-Channel Configuration
- **Description**: All per-channel behavior is config-driven, not hardcoded.
- **Acceptance Criteria**:
  - [ ] Fields: subject, platform, language (default `ko`), posting_schedule (cron-ish, default KST), approval_mode, style_profile_cadence, generative_video_budget_cap, warmup_phase, active/paused.
  - [ ] Editable via Web UI Config screen.
  - [ ] Config changes are audited (who/when/what).
- **Priority**: Must-have

### FR-013: Budget Governance
- **Description**: Hard cost ceilings per channel per month; kill-switch when exceeded.
- **Acceptance Criteria**:
  - [ ] MVP cap: generative-video spend **$20/channel/month** (hard ceiling).
  - [ ] Running spend visible in Web UI.
  - [ ] Exceeding the cap: generative scenes fall back to asset-assembly automatically; operator is notified.
  - [ ] Additional caps (LLM, TTS) tracked but not enforced in MVP.
- **Priority**: Must-have

### FR-014: Account Warmup & Posting Cadence
- **Description**: Enforces realistic posting rhythm to avoid anti-spam flags.
- **Acceptance Criteria**:
  - [ ] New channels begin in `warmup_phase` (default 14 days: 1 video/day) before transitioning to normal cadence (default 3 videos/day).
  - [ ] Publisher adapter is the enforcement point.
  - [ ] Cadence and warmup duration are per-channel config (FR-012).
- **Priority**: Must-have

## 3. Non-Functional Requirements

### NFR-001: Availability
- System operates 24/7/365 unattended once per-channel approval mode is flipped off.
- Pipeline runs scheduled via GitHub Actions cron; single missed run must not cascade.

### NFR-002: Security
- All external credentials stored as GitHub Actions encrypted secrets, keyed per channel (e.g., `YT_REFRESH_TOKEN_CHANNEL_1`). Never in Supabase, never in repo.
- OAuth tokens refreshed automatically; refresh failures page the operator.
- Supabase Row Level Security restricts Web UI access to the single authenticated operator.
- R2 artifacts accessed via time-limited presigned URLs only.
- **Security Baseline extension enabled** — all extension rules enforced as blocking constraints.

### NFR-003: Observability
- Every pipeline run writes a structured summary (stage-by-stage status) to Supabase.
- Failures and kill-switch events produce Telegram pages within 5 minutes.
- Web UI surfaces stale-channel detection (no successful Pipeline B run in N configured hours).

### NFR-004: Cost Governance
- Per-channel generative-video budget cap hard-enforced (FR-013).
- All external API calls attributed to `(channel_id, pipeline, run_id)` for accounting.
- Portfolio-level cost projection must support solvency vs. the $1,000/mo net revenue target.

### NFR-005: Reproducibility
- Every published video traceable to: `trend_id`, `style_profile_version`, `plan_hash`, prompt versions, model versions, artifact refs.
- StyleProfile versions are immutable.

### NFR-006: Extensibility
- New source, generative-video, and publishing adapters addable without pipeline-core changes (FR-009).
- New channels addable via config + secrets provisioning only.

### NFR-007: Platform ToS Compliance
- YouTube/Instagram AI-disclosure flags set at upload time where required.
- Rate limits and warmup schedules respected (FR-014).
- Copyright-safe asset sources only (licensed stock libraries, royalty-free BGM); track licenses per asset.

### NFR-008: Testing
- **Property-based testing extension enabled (full)** — PBT rules enforced as blocking constraints across pipeline logic, adapters, serialization, and state transitions.
- Integration tests exercise each adapter against sandbox/mocked platform APIs.

### NFR-009: Runtime Constraints
- GitHub Actions 6h single-job limit respected. Long renders offloaded to a callable worker (Modal or Runpod) if a render is projected to exceed the budget.
- Pipelines are idempotent and resumable where feasible (e.g., re-running a failed Pipeline B run does not double-publish).

## 4. Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Language | Python 3.12 | Strongest ecosystem for LLMs, video tooling (ffmpeg, moviepy), platform SDKs |
| Orchestrator | Claude Agent SDK (Python) | Each pipeline stage driven by Claude as an agent, matches "automated iteration by Claude" |
| State / Metadata DB | Supabase (Postgres) | Free tier, reachable from GHA, built-in Auth + Realtime for Web UI |
| Artifact Storage | Cloudflare R2 | S3-compatible, no egress fees, cheap for video blobs |
| Runtime (pipelines) | GitHub Actions matrix jobs (cron) | One job per channel per pipeline; zero infra to manage |
| Heavy-render offload | Modal or Runpod (deferred) | Only invoked if GHA 6h limit is threatened |
| Approval/Alert UX | Telegram bot | Mobile-first, push-native, complements Web UI |
| Web Dashboard | Next.js 15 (App Router) on Vercel | Solo-op friendly, zero infra; shares Supabase with pipelines |
| Dashboard Auth | Supabase Auth (magic-link or GitHub OAuth) | Same vendor as DB; RLS integration |
| UI styling | Tailwind + shadcn/ui | Fast build, professional finish |
| Video assembly | ffmpeg + moviepy | Industry-standard, scriptable |
| Generative video | Pluggable (Sora / Veo / Runway / Kling) | Adapter layer, per-channel selection |
| TTS | Pluggable (Korean-quality providers) | MVP requires high-quality Korean TTS |
| MVP platform | YouTube Shorts | Single adapter to prove the loop |
| Timezone | Asia/Seoul (KST) | Operator and initial audience in Korea |
| Initial language | Korean (`ko`) | MVP channel targets Korean audience |
| Secrets | GitHub Actions encrypted secrets, per-channel keyed | Secure, native to runtime |

## 5. Constraints & Assumptions

### Constraints
- Solo operator; low/no ongoing infra ops appetite.
- Monthly budget discipline: ~$20/channel/mo generative video cap; overall system must be solvent at ~$1K/mo net target.
- Must respect platform ToS (YouTube/Instagram automation and AI-content policies).

### Assumptions
- Operator has YouTube account(s) and can provision OAuth refresh tokens.
- Operator has API access to Claude, chosen TTS provider, chosen generative-video provider(s), and chosen stock-media libraries.
- Supabase free tier sufficient for MVP; R2 spend negligible at MVP scale.

## 6. Out of Scope (v1)

- Live-action / face-on-camera content.
- Real-time collaboration or multi-user SaaS.
- Paid promotion / ad-campaign automation.
- Long-form video (>3 min).
- Instagram Reels, TikTok, Shorts-on-Facebook (v2+).
- Generative-video as default path (stays opt-in per scene within budget).
- Languages other than Korean (v2+).

## 7. Open Questions

- Preferred Korean TTS provider (ElevenLabs Korean vs. Naver Clova vs. Typecast vs. Google)? Deferred to construction.
- Preferred generative-video provider for v1 opt-in path? Deferred to construction.
- Affiliate strategy — channel-subject-driven or generic networks (Amazon Associates-equivalent)? Deferred, decided per-channel at launch.
- Trend-source adapter roster for Korean short-form (YouTube trending API? Google Trends KR? Naver DataLab? manual curation list?) — shortlist needed during adapter design.
