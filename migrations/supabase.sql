-- Ads engine — Supabase tables (prefix ads_).
-- Run in the Supabase SQL Editor, or: psql "$DIRECT_URL" -f migrations/supabase.sql

create table if not exists ads_ledger (
  id         bigserial primary key,
  date       text not null,
  platform   text not null,
  status     text not null default 'queued',
  angle      text not null default '',
  sub        text not null default '',
  chars      int  not null default 0,
  path       text not null default '',
  url        text not null default '',
  text       text not null default '',
  created_at timestamptz not null default now()
);

create index if not exists ads_ledger_platform_status_idx
  on ads_ledger (platform, status);

create table if not exists ads_crm (
  id          bigserial primary key,
  date        text not null,
  platform    text not null,
  from_handle text not null default '',
  note        text not null default '',
  url         text not null default '',
  created_at  timestamptz not null default now()
);

-- REST access (secret key -> service_role). Required when tables are created
-- outside the Supabase dashboard (e.g. via psql with the postgres role).
grant select, insert, update, delete on ads_ledger, ads_crm to service_role;
grant usage, select on sequence ads_ledger_id_seq, ads_crm_id_seq to service_role;
