-- Migration: create conversation_messages table for storing chat history
-- This migration is intended to be applied to your Supabase project's Postgres database.

create table if not exists public.conversation_messages (
  id uuid primary key default gen_random_uuid(),
  session_id text not null,
  message_id text not null,
  role text not null,
  content text not null,
  metadata jsonb,
  created_at timestamptz not null default now()
);

create unique index if not exists conversation_messages_message_id_idx
  on public.conversation_messages (message_id);

create index if not exists conversation_messages_session_id_created_at_idx
  on public.conversation_messages (session_id, created_at);

