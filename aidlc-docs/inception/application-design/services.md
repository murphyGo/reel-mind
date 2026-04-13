# External Services

## Core Infrastructure

| Service | Role | Auth | Notes |
|---------|------|------|-------|
| Supabase | Postgres + Auth + Realtime | Service-role key (pipelines) / Anon + user JWT (Web UI) | Free tier sufficient for MVP |
| Cloudflare R2 | Artifact blob storage | S3-compatible access keys | Long-term retention (FR-010, NFR-005) |
| GitHub Actions | Pipeline runtime | Native | 6h single-job limit; cron triggers |
| Vercel | Web UI hosting | Git-linked | Next.js App Router |

## AI / Model Providers

| Service | Role | Model | Notes |
|---------|------|-------|-------|
| Anthropic API | Orchestration + planning + extraction | Claude Opus 4.6 (creative), Claude Haiku 4.5 (mechanical) | Prompt caching enabled throughout |

## Content Generation (pluggable)

| Category | v1 Candidates | Selection point |
|----------|---------------|-----------------|
| TTS (Korean) | ElevenLabs KR, Naver Clova, Typecast, Google TTS | Per-channel config |
| Stock media | Pexels, Pixabay | Per-channel config |
| Generative video | Sora, Veo, Runway, Kling | Per-channel config; budget-capped |
| Royalty-free BGM | YouTube Audio Library, Pixabay Music | Per-channel config |

## Source Discovery (pluggable)

| Category | v1 Candidates (Korean shorts) | Notes |
|----------|------------------------------|-------|
| Trending feeds | YouTube Data API (regionCode=KR), Google Trends KR, Naver DataLab | At least 2 enabled for redundancy |
| Style samples | YouTube search via Data API | Reused in Pipeline A |

## Publishing (pluggable)

| Platform | Adapter | MVP |
|----------|---------|-----|
| YouTube Shorts | YouTube Data API (OAuth2 refresh token flow) | ✅ |
| Instagram Reels | Instagram Graph API or instagrapi | v2 |
| TikTok | TikTok Content Posting API | v3 |

## Operator Channels

| Service | Role | Auth |
|---------|------|------|
| Telegram Bot API | Alerts + approvals | Bot token (GHA secret) |

## Heavy Render Offload (deferred; MVP ships stub)

| Service | Role |
|---------|------|
| Modal _or_ Runpod | Long-running render jobs that would exceed GHA 6h limit |

## Secrets Layout (SecretsLayout)

Naming: `{KIND}_{PROVIDER}_CHANNEL_{id}` for per-channel; `{KIND}_{PROVIDER}` for shared.

Examples:
- `YT_REFRESH_TOKEN_CHANNEL_1`
- `YT_CLIENT_ID`, `YT_CLIENT_SECRET` (shared)
- `TELEGRAM_BOT_TOKEN` (shared, one operator)
- `TELEGRAM_OPERATOR_CHAT_ID` (shared)
- `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` (shared; service role used only by pipelines)
- `R2_ACCOUNT_ID`, `R2_ACCESS_KEY`, `R2_SECRET_KEY`, `R2_BUCKET` (shared)
- `ANTHROPIC_API_KEY` (shared)
- `TTS_ELEVENLABS_API_KEY_CHANNEL_1` (if channel-specific), or `TTS_ELEVENLABS_API_KEY` (shared)

Rotation runbook and least-privilege scoping enforced by Security Baseline extension (NFR-002).
