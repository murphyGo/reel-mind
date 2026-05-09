# U2 Adapter Framework — Domain Entities

**Unit**: U2 Adapter Framework
**Stage**: Functional Design
**Created**: 2026-05-10

This document defines the technology-agnostic domain entities for adapter resolution and adapter contracts. Concrete provider SDK details are out of scope for U2.

---

## Entity Catalog

| Entity | Purpose | Owner |
|--------|---------|-------|
| `AdapterKind` | Names the supported adapter categories | U2 |
| `AdapterName` | Stable configured adapter identifier | U2 |
| `AdapterSpec` | Registry metadata for one adapter implementation | U2 |
| `AdapterContext` | Per-channel dependency bundle passed to adapters | U2 + U1 |
| `AdapterRegistry` | Resolves configured adapters by kind/name | U2 |
| `TrendCandidate` | Source-adapter output consumed by Pipeline B | U2/U4 |
| `SceneSpec` | Generative-video estimate/generate input | U2/U4 |
| `CostEstimate` | Provider-neutral estimated cost | U2 |
| `VideoClipRef` | Generated clip artifact reference | U2/U4 |
| `AudioRef` | TTS output artifact reference | U2/U4 |
| `MediaRef` | Stock-media search output | U2/U4 |
| `PublishMetadata` | Publish request metadata | U2/U4 |
| `PublishedRef` | Publish result reference | U2/U4/U5 |
| `MetricsSnapshot` | Platform metrics returned by publisher | U2/U5 |
| `AdapterFailureMode` | Mock adapter failure configuration | U2 tests |

---

## 1. `AdapterKind`

Enum:

- `source`
- `generative_video`
- `tts`
- `stock_media`
- `publish`

Rules:
- `source` may resolve an ordered list.
- Every other kind resolves exactly one adapter for a channel config.

---

## 2. `AdapterName`

Stable config-facing adapter identifier.

Examples:

- `youtube_trends`
- `naver_datalab`
- `sora`
- `korean_tts`
- `pexels`
- `youtube_shorts`
- `mock_source`

Validation:
- Lowercase slug: `^[a-z0-9][a-z0-9_-]{0,63}$`.
- Names are stable config contracts; renames require config migration.

---

## 3. `AdapterSpec`

Registry metadata for a concrete adapter.

| Field | Type | Notes |
|-------|------|-------|
| `kind` | `AdapterKind` | Category |
| `name` | `AdapterName` | Config identifier |
| `factory` | callable | Builds adapter from `AdapterContext` |
| `requires_secrets` | list[str] | Logical secret keys |
| `paid` | bool | Whether adapter calls may create `cost_ledger` rows |
| `capabilities` | set[str] | Optional feature flags, e.g. `ko_tts`, `youtube_upload` |

---

## 4. `AdapterContext`

Per-channel dependency bundle.

| Field | Source |
|-------|--------|
| `channel_config` | U1 `ChannelConfig` |
| `secrets` | U1 `SecretsProvider` |
| `cost_ledger` | U1 `CostLedger` |
| `logger` | U1 bound logger |
| `settings` | Provider-specific config object |

Adapters do not read global process state for secrets or config.

---

## 5. `AdapterRegistry`

In-memory registry that maps `(kind, name)` to `AdapterSpec`.

Responsibilities:
- Register adapter specs at startup.
- Validate channel config adapter references at bootstrap.
- Resolve one adapter by `(kind, name)`.
- Resolve ordered source adapters from `ChannelConfig.adapters.source`.
- Initialize adapters with `AdapterContext`.

Failure:
- Missing configured adapter raises `AdapterNotFound`, a terminal adapter error.
- Missing required secret is surfaced from U1 `SecretError`.

---

## 6. Source Adapter Entities

### `TrendCandidate`

| Field | Type | Notes |
|-------|------|-------|
| `candidate_id` | str | Stable per source result |
| `subject` | str | Must respect channel subject lock |
| `title` | str | Human-readable |
| `summary` | str | Why it may work |
| `source_name` | AdapterName | Adapter provenance |
| `source_url` | str | Optional source link |
| `score` | float | 0..1 normalized rank score |
| `observed_at` | datetime | UTC |
| `metadata` | dict | Source-specific details |

---

## 7. Generative Video Entities

### `SceneSpec`

Provider-neutral scene request:

- `scene_id`
- `prompt`
- `duration_seconds`
- `aspect_ratio`
- `style_notes`
- `safety_tags`

### `CostEstimate`

- `provider`
- `bucket`
- `units`
- `unit_kind`
- `usd_cost`
- `metadata`

### `VideoClipRef`

- U1 `ArtifactRef`
- `provider`
- `scene_id`
- `cost_entry_id`

---

## 8. TTS and Stock Media Entities

### `AudioRef`

- U1 `ArtifactRef`
- `provider`
- `voice`
- `language`
- `duration_seconds`
- `cost_entry_id`

### `MediaRef`

- `media_id`
- `provider`
- `media_type`
- `preview_url`
- `license`
- `attribution`
- `source_url`
- `metadata`

---

## 9. Publish and Metrics Entities

### `PublishMetadata`

- `title`
- `description`
- `tags`
- `scheduled_slot`
- `ai_disclosure`
- `visibility`

### `PublishedRef`

- `platform`
- `platform_video_id`
- `published_url`
- `published_at`
- `metadata`

### `MetricsSnapshot`

- `platform`
- `platform_video_id`
- `captured_at`
- `views`
- `likes`
- `comments`
- `watch_time_seconds`
- `revenue_usd`
- `metadata`

---

## 10. Mock Adapter Entities

`AdapterFailureMode` configures deterministic mock behavior:

- `success`
- `retryable_error`
- `terminal_error`

Reference mocks return stable IDs and predictable payloads so pipelines can test orchestration without real provider calls.
