from __future__ import annotations

import os
from typing import Optional

from supabase import Client, create_client

from .llm import _load_env_from_local_files


_supabase_client: Optional[Client] = None


def get_supabase_client() -> Optional[Client]:
  """
  Lazily create and cache a Supabase client, if configured.

  Configuration is read from environment variables, which are loaded from
  local .env-style files using the same mechanism as the LLM client.
  """
  global _supabase_client

  if _supabase_client is not None:
    return _supabase_client

  # Ensure env vars are populated from local config files if present
  _load_env_from_local_files()

  url = os.getenv("SUPABASE_URL")
  key = (
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    or os.getenv("SUPABASE_SERVICE_KEY")
    or os.getenv("SUPABASE_ANON_KEY")
  )

  if not url or not key:
    return None

  try:
    _supabase_client = create_client(url, key)
  except Exception:
    # If Supabase is misconfigured, fall back to no-op mode.
    _supabase_client = None

  return _supabase_client

