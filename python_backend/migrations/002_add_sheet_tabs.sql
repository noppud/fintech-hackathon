-- Migration: add sheet_tabs table and link conversation_messages to it

create table if not exists public.sheet_tabs (
  id uuid primary key default gen_random_uuid(),
  spreadsheet_id text not null,
  spreadsheet_url text not null,
  sheet_title text not null,
  created_at timestamptz not null default now(),
  unique (spreadsheet_id, sheet_title)
);

alter table public.conversation_messages
  add column if not exists sheet_tab_id uuid;

alter table public.conversation_messages
  add constraint if not exists conversation_messages_sheet_tab_id_fkey
  foreign key (sheet_tab_id) references public.sheet_tabs (id) on delete set null;

create index if not exists conversation_messages_sheet_tab_id_idx
  on public.conversation_messages (sheet_tab_id);

