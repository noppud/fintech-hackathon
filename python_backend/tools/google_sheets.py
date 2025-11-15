"""
# * Google Sheets API helper shared by all tools.
"""

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google.oauth2.credentials import Credentials as UserCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv

# * Configuration
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

DEFAULT_CREDENTIALS_PATH = PROJECT_ROOT / "client_secret_138285220800-9425b585vgk9rcglfc8fpejomgr7ar4l.apps.googleusercontent.com.json"
DEFAULT_SPREADSHEET_URL = os.environ.get("SPREADSHEET_URL", "")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

Color = Dict[str, float]


@dataclass
class FormulaIssue:
    """Structured representation of a formula issue."""

    cell: str
    severity: str
    message: str


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


def _normalize_color(cell_data: Optional[Dict[str, Any]]) -> Color:
    """Normalize background color to RGB dict."""
    default = {"red": 1.0, "green": 1.0, "blue": 1.0}
    if not cell_data:
        return default
    fmt = cell_data.get("userEnteredFormat")
    if not isinstance(fmt, dict):
        return default
    color = fmt.get("backgroundColor")
    if not isinstance(color, dict):
        return default
    red = float(color.get("red", 1.0) or 0.0)
    green = float(color.get("green", 1.0) or 0.0)
    blue = float(color.get("blue", 1.0) or 0.0)
    return {"red": red, "green": green, "blue": blue}


@dataclass
class SheetCellState:
    """State for a single cell on the sheet."""

    cell: str
    has_formula: bool
    has_numeric_constant: bool
    color: Color
    formula: Optional[str] = None


class GoogleSheetsFormulaValidator:
    """Helper class to interact with Google Sheets API."""

    def __init__(self, credentials_path: Path):
        self.credentials_path = Path(credentials_path)
        self.service = self._build_service()

    def _build_service(self):
        """Build Google Sheets API service from credentials."""
        if not self.credentials_path.exists():
            raise FileNotFoundError(f"Credentials not found at {self.credentials_path}")

        credentials = None
        token_path = PROJECT_ROOT / "token.json"

        # * Try cached token first (OAuth2)
        if token_path.exists():
            credentials = UserCredentials.from_authorized_user_file(token_path, SCOPES)
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())

        # * Try service account
        if not credentials:
            try:
                credentials = ServiceAccountCredentials.from_service_account_file(
                    self.credentials_path,
                    scopes=SCOPES,
                )
            except (ValueError, KeyError):
                # * Fall back to OAuth2 with server
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path,
                    scopes=SCOPES,
                )
                credentials = flow.run_local_server(port=8080)
                # * Cache the credentials
                if token_path:
                    token_path.write_text(credentials.to_json())

        return build("sheets", "v4", credentials=credentials)

    def fetch_spreadsheet(self, spreadsheet_id: str) -> Dict[str, Any]:
        """Fetch full spreadsheet metadata."""
        response = self.service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
        ).execute()
        return response

    def get_formulas(self, spreadsheet_id: str, sheet_title: str) -> List[Dict[str, Any]]:
        """Fetch all formula cells (with grid data) for a sheet."""
        sheet_range = f"'{sheet_title}'"
        response = self.service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            ranges=[sheet_range],
            includeGridData=True,
            fields="sheets(data(startRow,startColumn,rowData(values(effectiveValue,formattedValue,userEnteredValue,note)))),sheets(properties(sheetId,title))",
        ).execute()

        sheets = response.get("sheets", [])
        if not sheets:
            return []

        formulas: List[Dict[str, Any]] = []
        data_blocks = sheets[0].get("data", [])
        for block in data_blocks:
            start_row = block.get("startRow", 0)
            start_col = block.get("startColumn", 0)
            row_data = block.get("rowData", [])
            for row_offset, row_entry in enumerate(row_data):
                values = row_entry.get("values", [])
                for col_offset, cell_entry in enumerate(values):
                    if not isinstance(cell_entry, dict):
                        continue
                    user_value = cell_entry.get("userEnteredValue")
                    if not isinstance(user_value, dict):
                        continue
                    formula = user_value.get("formulaValue")
                    if not formula:
                        continue
                    row_index = start_row + row_offset
                    col_index = start_col + col_offset
                    formulas.append(
                        {
                            "cell": _cell_address(row_index, col_index),
                            "formattedValue": cell_entry.get("formattedValue"),
                            "effectiveValue": cell_entry.get("effectiveValue"),
                            "note": cell_entry.get("note") or "",
                        }
                    )
        return formulas

    def analyze_formulas(self, formulas: List[Dict[str, Any]]) -> List[FormulaIssue]:
        """Identify issues for formula cells."""
        issues: List[FormulaIssue] = []
        for entry in formulas:
            cell = entry.get("cell")
            if not isinstance(cell, str):
                continue
            effective_value = entry.get("effectiveValue")
            error_value: Optional[Dict[str, Any]] = None
            if isinstance(effective_value, dict):
                error_value = effective_value.get("errorValue")

            formatted_value = entry.get("formattedValue")

            if error_value:
                message = (
                    error_value.get("message")
                    or formatted_value
                    or error_value.get("type")
                    or "Formula error"
                )
                issues.append(FormulaIssue(cell=cell, severity="error", message=message))
                continue

            if isinstance(formatted_value, str) and formatted_value.startswith("#"):
                message = formatted_value
                issues.append(FormulaIssue(cell=cell, severity="warning", message=message))

        return issues

    def get_sheet_cells(self, spreadsheet_id: str, sheet_title: str) -> List[SheetCellState]:
        """Fetch all non-empty cells with their current state."""
        sheet_range = f"'{sheet_title}'"
        response = self.service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            ranges=[sheet_range],
            includeGridData=True,
            fields="sheets(data(startRow,startColumn,rowData(values(userEnteredValue,userEnteredFormat.backgroundColor)))),sheets(properties(sheetId,title))",
        ).execute()

        sheets = response.get("sheets", [])
        if not sheets:
            return []

        cells: List[SheetCellState] = []
        data_blocks = sheets[0].get("data", [])
        for block in data_blocks:
            start_row = block.get("startRow", 0)
            start_col = block.get("startColumn", 0)
            row_data = block.get("rowData", [])
            for row_offset, row_entry in enumerate(row_data):
                values = row_entry.get("values", [])
                for col_offset, cell_entry in enumerate(values):
                    if not isinstance(cell_entry, dict):
                        continue
                    user_value = cell_entry.get("userEnteredValue")
                    if not isinstance(user_value, dict):
                        continue
                    formula_value = user_value.get("formulaValue")
                    has_formula = bool(formula_value)
                    has_numeric_constant = False
                    if not has_formula:
                        has_numeric_constant = "numberValue" in user_value
                    if not has_formula and not has_numeric_constant:
                        continue
                    row_index = start_row + row_offset
                    col_index = start_col + col_offset
                    cell_label = _cell_address(row_index, col_index)
                    cells.append(
                        SheetCellState(
                            cell=cell_label,
                            has_formula=has_formula,
                            has_numeric_constant=has_numeric_constant,
                            color=_normalize_color(cell_entry),
                            formula=formula_value,
                        )
                    )
        return cells

