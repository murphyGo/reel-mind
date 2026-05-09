-- U1 Shared Foundation schema.
-- Source: aidlc-docs/construction/U1/infrastructure-design/infrastructure-design.md

create extension if not exists pgcrypto;

create table if not exists public.channels (
  id text primary key,
  display_name text not null,
  active boolean not null default true,
  config jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint channels_id_slug_check check (id ~ '^[a-z0-9][a-z0-9-]{0,31}$'),
  constraint channels_config_object_check check (jsonb_typeof(config) = 'object')
);

create index if not exists channels_active_idx on public.channels (id) where active = true;

create table if not exists public.pipeline_runs (
  run_id text primary key,
  channel_id text not null references public.channels(id),
  pipeline text not null,
  scheduled_slot text,
  trigger text not null,
  state text not null,
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  outcome text,
  force_retry_of text references public.pipeline_runs(run_id),
  config_version_hash text,
  constraint pipeline_runs_pipeline_check check (pipeline in ('A', 'B', 'C')),
  constraint pipeline_runs_trigger_check check (trigger in ('cron', 'manual', 'retry')),
  constraint pipeline_runs_state_check check (
    state in ('started', 'succeeded', 'failed', 'skipped', 'canceled')
  ),
  constraint pipeline_runs_finished_at_check check (
    state = 'started' or finished_at is not null
  )
);

create unique index if not exists pipeline_runs_scheduled_unique_idx
  on public.pipeline_runs (channel_id, pipeline, scheduled_slot)
  where scheduled_slot is not null and force_retry_of is null;

create index if not exists pipeline_runs_timeline_idx
  on public.pipeline_runs (channel_id, pipeline, started_at desc);

create table if not exists public.stage_records (
  id bigint generated always as identity primary key,
  run_id text not null references public.pipeline_runs(run_id),
  stage_name text not null,
  sequence integer not null,
  status text not null,
  attempt integer not null default 1,
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  artifacts jsonb not null default '[]'::jsonb,
  error jsonb,
  constraint stage_records_sequence_check check (sequence >= 1),
  constraint stage_records_attempt_check check (attempt >= 1),
  constraint stage_records_status_check check (status in ('ok', 'error', 'skipped', 'retrying')),
  constraint stage_records_artifacts_array_check check (jsonb_typeof(artifacts) = 'array'),
  constraint stage_records_run_sequence_unique unique (run_id, sequence)
);

create index if not exists stage_records_run_sequence_idx
  on public.stage_records (run_id, sequence);

create table if not exists public.cost_ledger (
  entry_id text primary key,
  timestamp timestamptz not null default now(),
  month_bucket date generated always as (
    date_trunc('month', timestamp at time zone 'UTC')::date
  ) stored,
  channel_id text not null,
  pipeline text not null,
  run_id text not null,
  provider text not null,
  bucket text not null,
  units numeric(18, 6) not null,
  unit_kind text not null,
  usd_cost numeric(12, 6) not null,
  metadata jsonb not null default '{}'::jsonb,
  constraint cost_ledger_channel_slug_check check (channel_id ~ '^[a-z0-9][a-z0-9-]{0,31}$'),
  constraint cost_ledger_pipeline_check check (pipeline in ('A', 'B', 'C', 'bot', 'ops')),
  constraint cost_ledger_bucket_check check (
    bucket in ('generative_video', 'tts', 'stock_media', 'claude', 'other')
  ),
  constraint cost_ledger_units_check check (units >= 0),
  constraint cost_ledger_usd_cost_check check (usd_cost >= 0),
  constraint cost_ledger_metadata_object_check check (jsonb_typeof(metadata) = 'object')
);

create index if not exists cost_ledger_month_sum_idx
  on public.cost_ledger (channel_id, month_bucket);

create index if not exists cost_ledger_audit_idx
  on public.cost_ledger (channel_id, timestamp desc);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists channels_set_updated_at on public.channels;
create trigger channels_set_updated_at
before update on public.channels
for each row execute function public.set_updated_at();

create or replace function public.reject_stage_after_terminal_run()
returns trigger
language plpgsql
as $$
declare
  parent_state text;
begin
  select state into parent_state
  from public.pipeline_runs
  where run_id = new.run_id;

  if parent_state in ('succeeded', 'failed', 'skipped', 'canceled') then
    raise exception 'cannot insert stage record after terminal run %', new.run_id;
  end if;

  return new;
end;
$$;

drop trigger if exists stage_records_reject_after_terminal on public.stage_records;
create trigger stage_records_reject_after_terminal
before insert on public.stage_records
for each row execute function public.reject_stage_after_terminal_run();

alter table public.channels enable row level security;
alter table public.pipeline_runs enable row level security;
alter table public.stage_records enable row level security;
alter table public.cost_ledger enable row level security;

-- U7 defines authenticated Web UI policies. Server-side pipeline/bot/ops access
-- uses Supabase service-role credentials and bypasses RLS by design.
