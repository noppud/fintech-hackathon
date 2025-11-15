from __future__ import annotations


def normalize_spreadsheet_id(raw: str) -> str:
  """
  Normalize a spreadsheet identifier that may be a bare ID or a full URL.

  If the input is a URL with a gid parameter, returns the full URL to preserve
  the sheet context. Otherwise, extracts and returns just the spreadsheet ID.

  Examples:
    - "https://docs.google.com/spreadsheets/d/abc123/edit?gid=0" -> "https://docs.google.com/spreadsheets/d/abc123/edit?gid=0"
    - "https://docs.google.com/spreadsheets/d/abc123" -> "abc123"
    - "abc123" -> "abc123"
  """
  if not raw:
    return raw

  trimmed = raw.strip()
  import re

  # Check if URL contains a gid parameter - if so, return the full URL
  if "gid=" in trimmed and "/spreadsheets/d/" in trimmed:
    return trimmed

  # Otherwise, extract just the spreadsheet ID
  match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", trimmed)
  if match:
    return match.group(1)
  return trimmed


def column_to_letter(column: int) -> str:
  letter = ""
  while column > 0:
    remainder = (column - 1) % 26
    letter = chr(65 + remainder) + letter
    column = (column - 1) // 26
  return letter


