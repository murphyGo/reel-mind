# Reel-Mind

A 24/7 autonomous AI pipeline that researches short-form video trends, scripts and produces videos, publishes them across a portfolio of single-subject channels, and iterates on performance — all orchestrated by Claude with configurable human approval.

## Overview

Running a portfolio of monetized short-form video channels is labor-intensive: trend research, style-matching, scripting, editing, publishing, and metrics review must happen daily per channel. Reel-Mind automates the full loop for a solo operator, adapts continuously to platform trends, and runs N channels in parallel.

## Features

- **Style Study pipeline** — continuously learns current editing conventions for each channel's subject
- **Content Production pipeline** — trend scout → plan → hybrid video generation → optional approval → publish
- **Measure & Learn pipeline** — ingests metrics and feeds the loop
- **Multi-channel orchestration** — N channels, isolated failures, per-channel config
- **Pluggable adapters** — sources, TTS, stock media, generative video, publishing platforms
- **Web dashboard** (Next.js + Supabase) for observability and approvals
- **Telegram bot** for push alerts and mobile approval
- **Per-channel budget governance** with hard generative-video caps

## Tech Stack

| Component | Technology |
|-----------|------------|
| Pipelines | Python 3.12, Claude Agent SDK, ffmpeg, moviepy |
| State / Metadata | Supabase (Postgres + Auth + Realtime) |
| Artifacts | Cloudflare R2 |
| Web UI | Next.js 15, Tailwind, shadcn/ui (Vercel) |
| Approval / Alerts | Telegram bot |
| Runtime | GitHub Actions (cron + matrix per channel) |
| Models | Claude Opus 4.6 (creative), Claude Haiku 4.5 (mechanical) |

## Getting Started

### Prerequisites

- Python 3.12 with `uv` or `pip-tools`
- Node.js 20+
- `ffmpeg` installed locally
- Accounts/API keys: Anthropic, Supabase, Cloudflare R2, YouTube Data API, Telegram Bot, chosen TTS + stock-media providers

### Installation

```bash
git clone <repo-url>
cd reel-mind

# Project structure is generated via /scaffold after init.
```

## Development

This project is built with **AI-DLC** methodology and **Claude Code** skills.

```bash
claude
/dev-reel-mind
```

`/dev-reel-mind` reads `aidlc-docs/aidlc-state.md` and walks you through construction one unit and one stage at a time.

### Development Workflow

1. `/dev-reel-mind` — get the next AIDLC construction step
2. Implement following `docs/requirements.md` and the unit's design artifacts
3. `/code-review git` — review before committing
4. Track debt with `/tech-debt`

### Key Documents

| Document | Description |
|----------|-------------|
| `aidlc-docs/aidlc-state.md` | AIDLC state and progress |
| `aidlc-docs/inception/application-design/` | Components, methods, services, dependencies |
| `docs/requirements.md` | Full FR/NFR requirements |
| `docs/DESIGN.md` | Architecture summary |
| `CLAUDE.md` | Context for Claude Code sessions |

## License

MIT (to be confirmed)
