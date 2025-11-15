"""
# * Snapshot background colors for cells listed in an input JSON and store them in Supabase.
# * The input JSON must include a shared 'url' pointing to the target sheet/tab.
"""

import json
import os
import re
import sys
import uuid
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from dotenv import load_dotenv

# * Ensure project root is importable when run from tools directory
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.google_sheets import (
    DEFAULT_CREDENTIALS_PATH,
    GoogleSheetsFormulaValidator,
)

load_dotenv(PROJECT_ROOT / ".env")

Color = Dict[str, float]

WHITE: Color = {"red": 1.0, "green": 1.0, "blue": 1.0}

# * Environment configuration (must exist; fail fast if missing)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")
if not SUPABASE_URL:
    raise SystemExit("SUPABASE_URL must be defined in environment or .env file.")
if not SUPABASE_SERVICE_KEY:
    raise SystemExit("SUPABASE_SERVICE_KEY must be defined in environment or .env file.")


def _parse_args() -> Path:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python snapshot_input_colors.py /absolute/path/to/input.json")

    input_path = Path(sys.argv[1]).expanduser().resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"No input file found at {input_path}")
    return input_path


def _load_cell_ranges(input_path: Path) -> Tuple[List[str], str]:
    payload = json.loads(input_path.read_text())
    potential_errors = payload.get("potential_errors")
    if not isinstance(potential_errors, list) or not potential_errors:
        raise ValueError("Input JSON must contain a non-empty 'potential_errors' list.")

    ranges: List[str] = []
    sheet_url: Optional[str] = None
    for idx, entry in enumerate(potential_errors):
        if not isinstance(entry, dict):
            raise ValueError(f"Entry #{idx} is not an object.")
        cell_location = entry.get("cell_location")
        url = entry.get("url")
        if not isinstance(cell_location, str) or not cell_location.strip():
            raise ValueError(f"Entry #{idx} missing 'cell_location'.")
        if not isinstance(url, str) or not url.strip():
            raise ValueError(f"Entry #{idx} missing 'url'.")
        normalized_url = url.strip()
        if sheet_url is None:
            sheet_url = normalized_url
        elif normalized_url != sheet_url:
            raise ValueError("All entries in input JSON must share the same 'url'.")
        ranges.append(cell_location.strip().upper())
    if sheet_url is None:
        raise ValueError("Input JSON must specify a 'url' for each entry.")
    return ranges, sheet_url
def _parse_sheet_url(sheet_url: str) -> Tuple[str, Optional[int]]:
    if not isinstance(sheet_url, str) or not sheet_url.strip():
        raise ValueError("Sheet URL must be a non-empty string.")
    sheet_url = sheet_url.strip()
    url_id_match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", sheet_url)
    url_gid_match = re.search(r"[?&]gid=(\d+)", sheet_url)
    spreadsheet_id = url_id_match.group(1) if url_id_match else sheet_url
    gid = int(url_gid_match.group(1)) if url_gid_match else None
    return spreadsheet_id, gid


def _column_label(index: int) -> str:
    if index < 0:
        raise ValueError(f"Column index must be non-negative: {index}")
    label = ""
    while index >= 0:
        index, remainder = divmod(index, 26)
        label = chr(65 + remainder) + label
        index -= 1
    return label


def _cell_address(row_index: int, col_index: int) -> str:
    return f"{_column_label(col_index)}{row_index + 1}"


def _column_index(label: str) -> int:
    if not re.fullmatch(r"[A-Z]+", label):
        raise ValueError(f"Invalid column label '{label}'.")
    index = 0
    for char in label:
        index = index * 26 + (ord(char) - ord("A") + 1)
    return index - 1


def _parse_cell(cell: str) -> Tuple[int, int]:
    match = re.fullmatch(r"([A-Z]+)(\d+)", cell)
    if not match:
        raise ValueError(f"Invalid cell reference '{cell}'.")
    column_label, row_digits = match.groups()
    row = int(row_digits) - 1
    if row < 0:
        raise ValueError(f"Row index must be positive in '{cell}'.")
    column = _column_index(column_label)
    return row, column


def _range_bounds(range_ref: str) -> Tuple[int, int, int, int]:
    parts = range_ref.split(":")
    if len(parts) == 1:
        start = end = parts[0]
    elif len(parts) == 2:
        start, end = parts
    else:
        raise ValueError(f"Invalid range '{range_ref}'.")
    start_row, start_col = _parse_cell(start)
    end_row, end_col = _parse_cell(end)
    if end_row < start_row or end_col < start_col:
        raise ValueError(f"Range '{range_ref}' has inverted bounds.")
    return start_row, end_row, start_col, end_col


def _expand_range(range_ref: str) -> List[str]:
    start_row, end_row, start_col, end_col = _range_bounds(range_ref)
    cells: List[str] = []
    for row in range(start_row, end_row + 1):
        for col in range(start_col, end_col + 1):
            cells.append(_cell_address(row, col))
    return cells


def _normalize_color(cell_data: Optional[Dict[str, Any]]) -> Color:
    if not cell_data:
        return WHITE
    fmt = cell_data.get("userEnteredFormat")
    if not isinstance(fmt, dict):
        return WHITE
    color = fmt.get("backgroundColor")
    if not isinstance(color, dict):
        return WHITE
    red = float(color.get("red", 1.0) or 0.0)
    green = float(color.get("green", 1.0) or 0.0)
    blue = float(color.get("blue", 1.0) or 0.0)
    return {"red": red, "green": green, "blue": blue}


def _fetch_colors_for_range(
    validator: GoogleSheetsFormulaValidator,
    spreadsheet_id: str,
    sheet_title: str,
    range_ref: str,
) -> Dict[str, Color]:
    sheet_range = f"'{sheet_title}'!{range_ref}"
    response = validator.service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        ranges=[sheet_range],
        includeGridData=True,
        fields="sheets(data(rowData(values(userEnteredFormat.backgroundColor)))),sheets(properties(sheetId,title))",
    ).execute()

    start_row, end_row, start_col, end_col = _range_bounds(range_ref)
    colors: Dict[str, Color] = {}

    sheets_data = response.get("sheets", [])
    if not sheets_data:
        return colors

    data_blocks = sheets_data[0].get("data", [])
    if not data_blocks:
        return colors

    row_data = data_blocks[0].get("rowData", [])
    for row_offset, row_entry in enumerate(row_data):
        values = row_entry.get("values", [])
        for col_offset, cell_entry in enumerate(values):
            row_index = start_row + row_offset
            col_index = start_col + col_offset
            cell_label = _cell_address(row_index, col_index)
            colors[cell_label] = _normalize_color(cell_entry)

    return colors


def _iter_cells(ranges: Iterable[str]) -> Iterable[str]:
    seen = set()
    for range_ref in ranges:
        for cell in _expand_range(range_ref):
            if cell not in seen:
                seen.add(cell)
                yield cell


def _post_to_supabase(rows: List[Dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("No rows to persist to Supabase.")

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/cell_color_snapshots"
    request = urllib.request.Request(
        url,
        method="POST",
        data=json.dumps(rows).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "Prefer": "resolution=merge-duplicates",
        },
    )

    try:
        with urllib.request.urlopen(request) as response:
            if response.status not in (200, 201, 204):
                raise RuntimeError(f"Unexpected Supabase status: {response.status}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Supabase insert failed: {exc.status} {body}") from exc


def save_snapshot_rows(rows: List[Dict[str, Any]]) -> None:
    """Persist pre-built snapshot rows to Supabase."""
    _post_to_supabase(rows)


def snapshot_ranges_to_supabase(ranges: List[str], sheet_url: str) -> Dict[str, Any]:
    """# * Snapshot the provided ranges and persist them to Supabase."""
    if not ranges:
        raise ValueError("No ranges provided for snapshot.")

    normalized_ranges = []
    seen = set()
    for range_ref in ranges:
        if not isinstance(range_ref, str):
            raise ValueError("Range references must be strings.")
        trimmed = range_ref.strip().upper()
        if not trimmed:
            continue
        if trimmed not in seen:
            seen.add(trimmed)
            normalized_ranges.append(trimmed)

    if not normalized_ranges:
        raise ValueError("No valid ranges provided for snapshot.")

    spreadsheet_id, gid = _parse_sheet_url(sheet_url)

    validator = GoogleSheetsFormulaValidator(DEFAULT_CREDENTIALS_PATH)
    spreadsheet = validator.fetch_spreadsheet(spreadsheet_id)
    sheets = spreadsheet.get("sheets", [])
    if not sheets:
        raise ValueError("No sheets available in spreadsheet.")

    sheet = None
    if gid is None:
        sheet = sheets[0]
    else:
        for candidate in sheets:
            if candidate["properties"].get("sheetId") == gid:
                sheet = candidate
                break
    if sheet is None:
        raise ValueError(f"No sheet found with gid={gid}.")

    sheet_props = sheet["properties"]
    sheet_title = sheet_props["title"]

    rows_to_insert: List[Dict[str, Any]] = []
    snapshot_ids: Dict[str, str] = {}

    for range_ref in normalized_ranges:
        snapshot_batch_id = uuid.uuid5(
            uuid.NAMESPACE_URL,
            f"{spreadsheet_id}:{gid}:{range_ref}",
        )
        snapshot_ids[range_ref] = str(snapshot_batch_id)
        colors_by_cell = _fetch_colors_for_range(validator, spreadsheet_id, sheet_title, range_ref)
        for cell in _expand_range(range_ref):
            color = colors_by_cell.get(cell, WHITE)
            rows_to_insert.append(
                {
                    "snapshot_batch_id": str(snapshot_batch_id),
                    "spreadsheet_id": spreadsheet_id,
                    "gid": gid,
                    "cell": cell,
                    "red": float(color["red"]),
                    "green": float(color["green"]),
                    "blue": float(color["blue"]),
                    "sheet_url": sheet_url,
                }
            )

    _post_to_supabase(rows_to_insert)

    total_cells = len(rows_to_insert)
    total_batches = len(normalized_ranges)
    first_snapshot_batch_id = snapshot_ids.get(normalized_ranges[0]) if normalized_ranges else None

    return {
        "status": "success",
        "message": f"Stored {total_cells} cell color snapshot(s) across {total_batches} batch id(s).",
        "count": total_cells,
        "range_snapshot_ids": snapshot_ids,
        "first_snapshot_batch_id": first_snapshot_batch_id,
    }


def main() -> None:
    input_path = _parse_args()
    ranges, sheet_url = _load_cell_ranges(input_path)
    result = snapshot_ranges_to_supabase(ranges, sheet_url)
    print(result["message"])
    if result["first_snapshot_batch_id"]:
        print(f"Snapshot batch ID: {result['first_snapshot_batch_id']}")


if __name__ == "__main__":
    main()


