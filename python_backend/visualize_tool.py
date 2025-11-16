"""
Formula visualization tool - color-code formulas vs hardcoded values.

Moved from tools/ to python_backend/ to eliminate deployment path issues.
"""

import re
import uuid
from typing import Any, Dict, List, Optional, Tuple

from .logging_config import get_logger

logger = get_logger(__name__)

Color = Dict[str, float]

# Visualization colors
FORMULA_COLOR: Color = {"red": 0.75, "green": 0.92, "blue": 0.75}  # light green
VALUE_COLOR: Color = {"red": 0.98, "green": 0.8, "blue": 0.5}      # light orange


def _cell_to_indices(cell: str) -> Tuple[int, int]:
    """Convert cell reference like 'A1' to (row_index, col_index)."""
    match = re.fullmatch(r"([A-Z]+)(\d+)", cell.strip().upper())
    if not match:
        raise ValueError(f"Invalid cell reference '{cell}'.")
    col_letters, row_digits = match.groups()
    row_index = int(row_digits) - 1
    if row_index < 0:
        raise ValueError(f"Row index must be positive in '{cell}'.")
    col_index = 0
    for char in col_letters:
        col_index = col_index * 26 + (ord(char) - ord("A") + 1)
    col_index -= 1
    return row_index, col_index


def _column_label(index: int) -> str:
    """Convert column index to letter (0=A, 25=Z, 26=AA, etc)."""
    if index < 0:
        raise ValueError(f"Column index must be non-negative: {index}")
    label = ""
    while index >= 0:
        index, remainder = divmod(index, 26)
        label = chr(65 + remainder) + label
        index -= 1
    return label


def _cell_address(row_index: int, col_index: int) -> str:
    """Convert row/col indices to A1 notation."""
    return f"{_column_label(col_index)}{row_index + 1}"


def _build_color_request(sheet_id: int, row: int, col: int, color: Color) -> Dict[str, Any]:
    """Build a repeatCell request for Google Sheets API."""
    return {
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": row,
                "endRowIndex": row + 1,
                "startColumnIndex": col,
                "endColumnIndex": col + 1,
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": color,
                },
            },
            "fields": "userEnteredFormat.backgroundColor",
        }
    }


def _normalize_color(cell_data: Dict[str, Any]) -> Color:
    """Extract background color from cell data."""
    fmt = cell_data.get("userEnteredFormat") or cell_data.get("effectiveFormat") or {}
    color = fmt.get("backgroundColor") or {}
    return {
        "red": float(color.get("red", 1.0) or 0.0),
        "green": float(color.get("green", 1.0) or 0.0),
        "blue": float(color.get("blue", 1.0) or 0.0),
    }


def visualize_formulas(
    validator: Any,
    spreadsheet_id: str,
    sheet_title: str,
    sheet_id: int,
    gid: Optional[int],
    supabase_insert_fn: callable,
) -> Dict[str, Any]:
    """
    Color-code cells to distinguish formulas (green) from hard-coded values (orange).

    Args:
        validator: GoogleSheetsFormulaValidator instance with .service attribute
        spreadsheet_id: The bare spreadsheet ID
        sheet_title: The sheet name
        sheet_id: The sheet ID for API requests
        gid: The gid for snapshots (optional)
        supabase_insert_fn: Function to insert snapshot rows

    Returns:
        Dict with status, message, count, and snapshot_batch_id
    """
    logger.info(f"Visualizing formulas on sheet '{sheet_title}' (id={spreadsheet_id})")

    # Fetch cell data with formulas
    quoted_title = sheet_title.replace("'", "''")
    try:
        response = validator.service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            includeGridData=True,
            ranges=[f"'{quoted_title}'"],
            fields="sheets(data(startRow,startColumn,rowData(values(userEnteredValue,userEnteredFormat,effectiveFormat))),properties(sheetId,title))",
        ).execute()
    except Exception as exc:
        logger.error(f"Failed to fetch sheet data: {exc}", exc_info=True)
        raise

    sheets_data = response.get("sheets", [])
    if not sheets_data:
        return {
            "status": "no_cells",
            "message": f"No data found on sheet '{sheet_title}'.",
            "count": 0,
            "snapshot_batch_id": None,
        }

    # Collect cells with formulas or numeric constants
    targets = []
    data_blocks = sheets_data[0].get("data", [])

    for block in data_blocks:
        start_row = block.get("startRow", 0)
        start_col = block.get("startColumn", 0)
        for row_offset, row_entry in enumerate(block.get("rowData", [])):
            values = row_entry.get("values", [])
            for col_offset, cell_entry in enumerate(values):
                user_value = cell_entry.get("userEnteredValue") or {}
                has_formula = "formulaValue" in user_value
                has_numeric_constant = "numberValue" in user_value and not has_formula

                if not has_formula and not has_numeric_constant:
                    continue

                row_index = start_row + row_offset
                col_index = start_col + col_offset
                cell_label = _cell_address(row_index, col_index)

                targets.append({
                    "cell": cell_label,
                    "row": row_index,
                    "col": col_index,
                    "has_formula": has_formula,
                    "has_numeric_constant": has_numeric_constant,
                    "original_color": _normalize_color(cell_entry),
                })

    if not targets:
        return {
            "status": "no_cells",
            "message": f"No formulas or hard-coded numeric values detected on '{sheet_title}'.",
            "count": 0,
            "snapshot_batch_id": None,
        }

    logger.info(f"Found {len(targets)} cells to visualize ({sum(1 for t in targets if t['has_formula'])} formulas, {sum(1 for t in targets if t['has_numeric_constant'])} values)")

    # Create snapshot
    snapshot_batch_id = str(uuid.uuid4())
    snapshot_rows = [
        {
            "snapshot_batch_id": snapshot_batch_id,
            "spreadsheet_id": spreadsheet_id,
            "gid": gid,
            "cell": target["cell"],
            "red": float(target["original_color"]["red"]),
            "green": float(target["original_color"]["green"]),
            "blue": float(target["original_color"]["blue"]),
        }
        for target in targets
    ]

    try:
        supabase_insert_fn(snapshot_rows)
        logger.info(f"Created snapshot {snapshot_batch_id} with {len(snapshot_rows)} cells")
    except Exception as exc:
        logger.error(f"Failed to create snapshot: {exc}", exc_info=True)
        raise

    # Apply colors
    batch_requests = []
    for target in targets:
        color = FORMULA_COLOR if target["has_formula"] else VALUE_COLOR
        batch_requests.append(
            _build_color_request(sheet_id, target["row"], target["col"], color)
        )

    try:
        validator.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": batch_requests},
        ).execute()
        logger.info(f"Applied colors to {len(batch_requests)} cells")
    except Exception as exc:
        logger.error(f"Failed to apply colors: {exc}", exc_info=True)
        raise

    formula_count = sum(1 for t in targets if t["has_formula"])
    value_count = sum(1 for t in targets if t["has_numeric_constant"])

    return {
        "status": "success",
        "message": (
            f"Colored {len(targets)} cell(s) on '{sheet_title}' "
            f"({formula_count} formulas → green, {value_count} values → orange)."
        ),
        "count": len(targets),
        "snapshot_batch_id": snapshot_batch_id,
    }
