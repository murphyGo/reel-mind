# Reel-Mind

## One-Liner
A 24/7 autonomous AI pipeline that researches short-form video trends, scripts and produces videos, publishes them across a portfolio of single-subject channels on YouTube/Instagram/etc., and iterates on performance — all orchestrated by Claude with configurable human approval.

## The Problem
Running a portfolio of monetized short-form video channels is labor-intensive: trend research, style-matching, scripting, editing, publishing, and metrics review have to happen daily per channel. A solo operator can't scale past a few accounts. Existing "AI video tools" automate one step (e.g. script → video) but not the full loop, and none continuously adapt to shifting platform trends or manage multiple channels in parallel.

## Target User
Solo operator (initially the builder) running a portfolio of faceless, single-subject short-form channels with a ~$1,000/month ad + affiliate revenue target.

## Core Features

1. **Trend Scout** — Per-channel subject-locked agent mines viral content, memes, and trend signals from pluggable sources; outputs ranked topic candidates.
2. **Style Profiler** — Agent continuously learns current short-form editing conventions (length, cut pacing, subtitle style, BGM genre, hook patterns, CTA style) for the target platform/niche.
3. **Video Planner** — Produces full plan: script, storyboard, continuity notes, BGM choice, captions, thumbnail, title, description, tags.
4. **Hybrid Video Generator** — Asset-assembly by default (LLM script → TTS → stock footage + captions + BGM); routes specific scenes to generative video APIs (Sora/Veo/Runway/Kling) when the plan calls for it.
5. **Approval Gate** — Per-channel toggle between "human approves via Telegram" and "fully autonomous." Approval includes preview, edit notes, or reject.
6. **Multi-Platform Publisher** — Uploads to YouTube / Instagram Reels / (future: TikTok, Shorts variants). Publishing adapter layer is pluggable.
7. **Multi-Channel Orchestration** — N independent pipelines run concurrently (youtube1, youtube2, instagram1, ...), each with its own subject, style profile, schedule, and config.
8. **Metrics & Earnings Tracker** — Pulls followers, views, watch time, revenue per channel; feeds back into trend/style decisions over time.
9. **Pluggable Sources & Platforms** — Every source (trend feeds, stock libraries, video gen APIs) and publishing platform is an adapter; new ones can be added without touching the pipeline core.

## Out of Scope (v1)
- Live-action / face-on-camera content
- Real-time collaboration or multi-user SaaS
- Full ad campaign / paid promotion automation
- Long-form video (>3 min)

## Tech Preferences

- **Language**: Python 3.12
- **Orchestrator**: Claude Agent SDK (Python) — Claude drives each pipeline stage as an agent
- **State/Metadata**: Supabase (Postgres)
- **Artifact Storage**: Cloudflare R2
- **Runtime**: GitHub Actions (cron + matrix jobs per channel); offload long renders to Modal/Runpod if the 6h Actions limit is hit
- **Approval UX**: Telegram bot
- **Video**: Hybrid — asset-assembly (ffmpeg/moviepy + TTS + stock libraries) with generative-video APIs (Sora/Veo/Runway/Kling) for selected scenes

## Non-Functional Requirements
- **Availability**: 24/7/365 unattended operation
- **Concurrency**: N independent channel pipelines in parallel
- **Configurability**: Per-channel config (subject, platform, schedule, approval mode, style seeds, budget cap)
- **Cost target**: Must clear ~$1,000/month net at modest channel count
- **Extensibility**: Sources and publishing platforms as adapters

## Notes
- Platform ToS risk (YouTube/IG policies on automation & AI-disclosed content) must be handled at the publishing-adapter layer — e.g. AI-content disclosure flags, rate pacing, account-warmup policy.
- Cost governance per channel (budget cap + generative-video quota) is a first-class concern given the $1K/mo target.
- Approval gate default: **ON** for new channels; flipped to autonomous per-channel after operator gains confidence.
