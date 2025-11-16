from __future__ import annotations

import re
from typing import Optional, Dict


def parse_spreadsheet_url(raw: str) -> Dict[str, Optional[str]]:
  """
  Parse a spreadsheet identifier (URL or bare ID) into its components.

  Returns a dictionary with:
    - spreadsheet_id: The bare spreadsheet ID (always extracted)
    - gid: The sheet gid if present in URL, None otherwise
    - url: The original input (for reference)

  Examples:
    - "https://docs.google.com/spreadsheets/d/abc123/edit?gid=456"
      -> {"spreadsheet_id": "abc123", "gid": "456", "url": "https://..."}
    - "https://docs.google.com/spreadsheets/d/abc123"
      -> {"spreadsheet_id": "abc123", "gid": None, "url": "https://..."}
    - "abc123"
      -> {"spreadsheet_id": "abc123", "gid": None, "url": "abc123"}
  """
  if not raw:
    return {"spreadsheet_id": raw, "gid": None, "url": raw}

  trimmed = raw.strip()

  # Extract spreadsheet ID from URL or use as-is
  id_match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", trimmed)
  spreadsheet_id = id_match.group(1) if id_match else trimmed

  # Extract gid if present in URL
  gid_match = re.search(r"[?&]gid=(\d+)", trimmed)
  gid = gid_match.group(1) if gid_match else None

  return {
    "spreadsheet_id": spreadsheet_id,
    "gid": gid,
    "url": trimmed
  }


def normalize_spreadsheet_id(raw: str) -> str:
  """
  Extract and return ONLY the bare spreadsheet ID from a URL or ID string.

  This function ALWAYS returns just the spreadsheet ID, never a full URL.
  Use this when calling Google Sheets API methods that expect a spreadsheet ID.

  Examples:
    - "https://docs.google.com/spreadsheets/d/abc123/edit?gid=0" -> "abc123"
    - "https://docs.google.com/spreadsheets/d/abc123" -> "abc123"
    - "abc123" -> "abc123"
  """
  return parse_spreadsheet_url(raw)["spreadsheet_id"]


def column_to_letter(column: int) -> str:
  letter = ""
  while column > 0:
    remainder = (column - 1) % 26
    letter = chr(65 + remainder) + letter
    column = (column - 1) // 26
  return letter


