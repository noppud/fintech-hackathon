"""
Reset all cell background colors and notes on the configured Google Sheet.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# * Ensure project root is importable when run from helper directory
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# * Ensure python_backend package is importable for tools.*
PYTHON_BACKEND_DIR = PROJECT_ROOT / "python_backend"
if str(PYTHON_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_BACKEND_DIR))

# * Load environment variables from the project root so DEFAULT_SPREADSHEET_URL resolves.
load_dotenv(PROJECT_ROOT / ".env")

from tools.google_sheets import (
    DEFAULT_CREDENTIALS_PATH,
    DEFAULT_SPREADSHEET_URL,
    GoogleSheetsFormulaValidator,
)


def _resolve_sheet(spreadsheet: dict, gid: Optional[int]) -> dict:
    sheets = spreadsheet.get("sheets", [])
    if not sheets:
        raise ValueError("No sheets found in spreadsheet.")

    if gid is None:
        return sheets[0]

    for sheet in sheets:
        if sheet["properties"].get("sheetId") == gid:
            return sheet

    raise ValueError(f"No sheet found with gid={gid}.")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reset all cell background colors and notes on the target Google Sheet.",
    )
    parser.add_argument(
        "--sheet-url",
        dest="sheet_url",
        help="Explicit sheet URL to override SPREADSHEET_URL env.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    spreadsheet_url = args.sheet_url or DEFAULT_SPREADSHEET_URL

    if not spreadsheet_url:
        raise ValueError("SPREADSHEET_URL is empty; set it in .env or pass --sheet-url.")
    credentials_path = DEFAULT_CREDENTIALS_PATH

    url_id_match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", spreadsheet_url)
    url_gid_match = re.search(r"[?&]gid=(\d+)", spreadsheet_url)
    spreadsheet_id = url_id_match.group(1) if url_id_match else spreadsheet_url
    gid = int(url_gid_match.group(1)) if url_gid_match else None

    validator = GoogleSheetsFormulaValidator(credentials_path)
    spreadsheet = validator.fetch_spreadsheet(spreadsheet_id)

    sheet = _resolve_sheet(spreadsheet, gid)
    props = sheet["properties"]
    grid = props.get("gridProperties") or {}
    row_count = grid.get("rowCount")
    column_count = grid.get("columnCount")

    if row_count is None or column_count is None:
        raise ValueError("Sheet grid dimensions unavailable; cannot reset colors.")

    if row_count == 0 or column_count == 0:
        print("Sheet has no cells; nothing to reset.")
        return

    request = {
        "repeatCell": {
            "range": {
                "sheetId": props["sheetId"],
                "startRowIndex": 0,
                "endRowIndex": row_count,
                "startColumnIndex": 0,
                "endColumnIndex": column_count,
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {"red": 1, "green": 1, "blue": 1},
                },
                "note": None,
            },
            "fields": "userEnteredFormat.backgroundColor,note",
        }
    }

    validator.service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={"requests": [request]},
    ).execute()

    print(f"Cleared background colors and notes on '{props['title']}'.")


if __name__ == "__main__":
    main()

