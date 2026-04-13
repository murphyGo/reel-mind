# Technical Environment: Reel-Mind

## Technology Stack

### Pipelines (A / B / C)
- **Language**: Python 3.12
- **Orchestrator**: Claude Agent SDK (Python)
- **Video assembly**: ffmpeg, moviepy
- **Generative video**: pluggable adapters (Sora / Veo / Runway / Kling)
- **TTS**: pluggable (Korean-quality providers)

### Backend / State
- **Database**: Supabase (Postgres) — rows for channels, configs, runs, plans, approvals, metrics, style profiles, trend candidates, budgets
- **Artifact storage**: Cloudflare R2 — scraped samples, generated audio/images/video
- **Auth**: Supabase Auth (single operator; RLS)
- **Realtime**: Supabase Realtime — live approval queue + run status in Web UI

### Web UI
- **Framework**: Next.js 15 (App Router)
- **Hosting**: Vercel
- **Styling**: Tailwind CSS + shadcn/ui

### Approval / Alerts
- **Bot**: Telegram (python-telegram-bot or aiogram)

### Runtime / Deployment
- **Pipeline execution**: GitHub Actions (cron-scheduled, matrix jobs per channel per pipeline)
- **Secrets**: GitHub Actions encrypted secrets, per-channel keyed
- **Heavy-render offload (deferred)**: Modal or Runpod — invoked only when a render threatens the GHA 6h single-job limit

## Development Environment
- Python 3.12 with `uv` or `pip-tools` for dependency management
- Node.js 20+ for the Next.js dashboard
- `ffmpeg` installed locally and in GHA runners
- Supabase CLI for local DB migrations
- `.env` for local dev credentials; prod credentials in GHA secrets

## Deployment Targets
- **Pipelines**: GitHub Actions workflows, one per (channel × pipeline) via matrix; cron-triggered
- **Web UI**: Vercel (Next.js)
- **DB + Auth + Realtime**: Supabase (managed)
- **Artifacts**: Cloudflare R2 (managed)
- **Optional heavy-render**: Modal or Runpod (only when needed)

## Existing Systems
None — greenfield project.

## Technical Constraints
- GitHub Actions 6h per-job limit → long renders must offload.
- Platform ToS (YouTube, later Instagram) around automation and AI-content disclosure.
- Per-channel monthly generative-video budget cap: **$20 (MVP)**.
- Portfolio-level revenue target: ~$1,000/month net.
- Per-channel credential isolation: tokens never in Supabase or repo.
- Timezone: Asia/Seoul (KST) for MVP scheduling.
- Language: Korean (`ko`) for MVP content.
