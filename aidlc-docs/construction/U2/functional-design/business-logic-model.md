# U2 Adapter Framework — Business Logic Model

**Unit**: U2 Adapter Framework
**Stage**: Functional Design
**Created**: 2026-05-10

This document defines the adapter framework workflows and algorithms. It is provider-neutral; concrete SDK behavior belongs to downstream provider implementations.

---

## 1. Registry Startup Validation

### Inputs

- U1 `ChannelConfig.adapters`
- Built-in adapter specs registered by code
- Optional test-only mock specs

### Algorithm

```text
validate_channel_adapters(channel_config):
  for source_name in channel_config.adapters.source:
    assert registry contains (source, source_name)

  assert registry contains (tts, channel_config.adapters.tts)
  assert registry contains (stock_media, channel_config.adapters.stock)

  for platform, publish_name in channel_config.adapters.publish:
    assert registry contains (publish, publish_name)

  if channel_config.generative_video_enabled:
    assert channel_config.adapters.generative_video is not null
    assert registry contains (generative_video, channel_config.adapters.generative_video)
```

Missing adapters fail at startup/bootstrap with `AdapterNotFound`. The pipeline should fail before spending external API calls.

---

## 2. Adapter Registration

```text
register(spec):
  key = (spec.kind, spec.name)
  if key already exists:
    raise DuplicateAdapter
  registry[key] = spec
```

Registration is in-process and deterministic. U2 does not require dynamic plugin loading from the network or filesystem for MVP.

---

## 3. Adapter Resolution

### Single adapter kinds

```text
resolve(kind, name, context):
  spec = registry[(kind, name)] or raise AdapterNotFound
  validate_required_secrets(spec, context)
  return spec.factory(context.with_settings(adapter_settings))
```

Single adapter kinds:

- `tts`
- `stock_media`
- `generative_video`
- `publish`

### Source adapter list

```text
resolve_sources(channel_config, context):
  return [
    resolve(source, source_name, context)
    for source_name in channel_config.adapters.source
  ]
```

Source adapters preserve config order. Ranking/merging candidates is pipeline logic in U4, not registry logic.

---

## 4. Adapter Context Construction

```text
build_context(channel_config, runtime, adapter_settings):
  return AdapterContext(
    channel_config = channel_config,
    secrets = runtime.secrets,
    cost_ledger = runtime.cost_ledger,
    logger = runtime.logger.bind(channel_id=channel_config.channel_id),
    settings = adapter_settings,
  )
```

Adapters receive dependencies explicitly. They do not import singleton clients or read secret-shaped environment variables.

---

## 5. Paid Adapter Call Wrapper

Paid adapter operations use a common wrapper:

```text
call_paid_adapter(operation, estimate_or_actual_cost, run_context, invoke):
  result = retry_policy.run(operation, invoke)
  if result contains actual cost:
    cost_ledger.record(
      channel_id,
      pipeline,
      run_id,
      provider,
      bucket,
      units,
      unit_kind,
      usd_cost,
      metadata,
    )
  return result
```

Rules:

- Cost is recorded inside adapter wrappers, not by pipeline core.
- If the provider call succeeds but ledger recording fails, U1 raises and the run fails.
- Free adapters may omit cost records.
- Estimated costs are returned before paid calls where relevant, especially generative video.

---

## 6. Retry and Error Classification

U2 adapter retry is a thin domain wrapper around U1 `RetryExecutor`.

```text
adapter_retry(operation, provider_call):
  classify provider SDK exceptions as:
    RetryableAdapterError
    TerminalAdapterError
  call U1 RetryExecutor with adapter policy
```

Classification examples:

| Provider condition | Classification |
|-------------------|----------------|
| Network timeout | Retryable |
| HTTP 429 with retry-after | Retryable with retry-after |
| HTTP 5xx | Retryable |
| HTTP 401/403 | Terminal |
| Invalid prompt/config | Terminal |
| Unsupported media/license | Terminal |

Provider-specific exceptions subclass U1 `RetryableError` or `TerminalError` so pipelines can handle them consistently.

---

## 7. Interface Workflows

### SourceAdapter

```text
fetch_trending(subject, language, now):
  validate subject and language
  fetch provider results
  normalize to TrendCandidate[]
  filter out candidates that violate subject lock
  return candidates
```

### GenerativeVideoAdapter

```text
estimate_cost(scene_spec):
  validate scene duration/aspect ratio
  return CostEstimate

generate(scene_spec):
  run paid call wrapper
  upload resulting clip to R2 through downstream pipeline/U1
  return VideoClipRef
```

### TTSAdapter

```text
synthesize(text, voice, language):
  validate language and text length
  run paid call wrapper
  return AudioRef
```

### StockMediaAdapter

```text
search(query, media_type):
  validate query and media type
  call provider
  normalize license/attribution
  return MediaRef[]
```

### PublishAdapter

```text
upload(video_ref, metadata):
  validate metadata and AI disclosure flag
  refresh token if needed through U1 SecretsProvider flow
  call provider upload
  return PublishedRef

fetch_metrics(published_ref):
  call provider metrics endpoint
  normalize to MetricsSnapshot
```

---

## 8. Reference Mock Behavior

Mock adapters support three deterministic modes:

- `success`
- `retryable_error`
- `terminal_error`

Mock IDs are derived from stable input hashes so tests can assert exact outputs.

```text
mock_source.fetch_trending("food", "ko", now)
  -> [TrendCandidate(candidate_id="mock-source-<hash>", ...)]
```

Mocks must never call external services, read real secrets, or write cost records unless explicitly configured for ledger-wrapper tests.
