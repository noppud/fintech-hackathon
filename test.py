"""
Google Sheets Formula Validator
Analyzes Google Sheets documents for formula logic errors.
* Extracts all formulas from a sheet
* Detects common formula issues
"""

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as UserCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# * Load environment variables from .env
load_dotenv()

Color = Dict[str, float]

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
TOKEN_PATH = Path(__file__).resolve().parent / "token.json"

# * Default configuration (loaded from .env, no fallbacks)
DEFAULT_SPREADSHEET_URL = os.environ["SPREADSHEET_URL"]
DEFAULT_CREDENTIALS_PATH = os.environ["CREDENTIALS_PATH"]
OAUTH_PORT = int(os.getenv("OAUTH_PORT") or os.environ["OAUTH_PORT"])
FORMULA_CELL_COLOR: Color = {
    "red": float(os.environ["FORMULA_CELL_RED"]),
    "green": float(os.environ["FORMULA_CELL_GREEN"]),
    "blue": float(os.environ["FORMULA_CELL_BLUE"]),
}
INTEGER_CELL_COLOR: Color = {
    "red": float(os.environ["INTEGER_CELL_RED"]),
    "green": float(os.environ["INTEGER_CELL_GREEN"]),
    "blue": float(os.environ["INTEGER_CELL_BLUE"]),
}


@dataclass
class FormulaIssue:
    """# * Represents a detected formula issue"""

    cell: str
    formula: str
    severity: str  # "error", "warning", "info"
    message: str


class GoogleSheetsFormulaValidator:
    """# * Minimal validator for Google Sheets formulas"""

    def __init__(self, credentials_path: str):
        self.service = self._authenticate(credentials_path)

    def _authenticate(self, credentials_path: str):
        """# * Authenticate with Google Sheets via OAuth"""
        creds = None

        if TOKEN_PATH.exists():
            creds = UserCredentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=OAUTH_PORT)

            TOKEN_PATH.write_text(creds.to_json())

        return build("sheets", "v4", credentials=creds)

    def fetch_spreadsheet(self, spreadsheet_id: str) -> Dict[str, Any]:
        """# * Return spreadsheet metadata"""
        return self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()

    def get_formulas(self, spreadsheet_id: str, sheet_name: str) -> Dict[str, str]:
        """# * Return every formula found in the target sheet"""
        result = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"'{sheet_name}'",
            valueRenderOption="FORMULA",
            majorDimension="ROWS",
        ).execute()

        values = result.get("values", [])
        formulas: Dict[str, str] = {}

        for row_idx, row in enumerate(values, start=1):
            for col_idx, value in enumerate(row, start=1):
                if isinstance(value, str) and value.startswith("="):
                    formulas[self._cell_address(row_idx, col_idx)] = value

        return formulas

    def analyze_formulas(self, formulas: Dict[str, str]) -> List[FormulaIssue]:
        """# * Run simple validations on each formula"""
        issues: List[FormulaIssue] = []

        for cell, formula in formulas.items():
            issues.extend(self._analyze_formula(cell, formula))

        return issues

    def apply_highlighting(self, spreadsheet_id: str, sheet_id: int, sheet_name: str) -> None:
        """# * Highlight formulas (green) and integer literals (orange)"""
        formulas_view = self._get_values(spreadsheet_id, sheet_name, "FORMULA")
        raw_view = self._get_values(spreadsheet_id, sheet_name, "UNFORMATTED_VALUE")

        max_rows = max(len(formulas_view), len(raw_view))
        max_cols = 0
        for row in formulas_view:
            max_cols = max(max_cols, len(row))
        for row in raw_view:
            max_cols = max(max_cols, len(row))

        if max_rows == 0 or max_cols == 0:
            return

        requests: List[Dict[str, Any]] = []

        for row_index in range(max_rows):
            formula_row = formulas_view[row_index] if row_index < len(formulas_view) else []
            raw_row = raw_view[row_index] if row_index < len(raw_view) else []

            col = 0
            while col < max_cols:
                formula_value = formula_row[col] if col < len(formula_row) else None
                if isinstance(formula_value, str) and formula_value.startswith("="):
                    start_col = col
                    while col < max_cols:
                        value = formula_row[col] if col < len(formula_row) else None
                        if not (isinstance(value, str) and value.startswith("=")):
                            break
                        col += 1
                    requests.append(
                        self._build_repeat_cell(sheet_id, row_index, start_col, col, FORMULA_CELL_COLOR)
                    )
                    continue

                raw_value = raw_row[col] if col < len(raw_row) else None
                if self._is_integer(raw_value):
                    start_col = col
                    while col < max_cols:
                        inner_value = raw_row[col] if col < len(raw_row) else None
                        if not self._is_integer(inner_value):
                            break
                        col += 1
                    requests.append(
                        self._build_repeat_cell(sheet_id, row_index, start_col, col, INTEGER_CELL_COLOR)
                    )
                    continue

                col += 1

        if requests:
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body={"requests": requests},
            ).execute()

    def report_issues(self, issues: List[FormulaIssue]) -> str:
        """# * Produce a grouped summary"""
        if not issues:
            return "No issues found!"

        report_lines = [f"Found {len(issues)} potential issues:", "=" * 60, ""]
        by_severity: Dict[str, List[FormulaIssue]] = {"error": [], "warning": [], "info": []}

        for issue in issues:
            by_severity.setdefault(issue.severity, []).append(issue)

        for severity in ["error", "warning", "info"]:
            group = by_severity.get(severity, [])
            if not group:
                continue
            report_lines.append(f"{severity.upper()} ({len(group)}):")
            report_lines.append("-" * 40)
            for item in group:
                report_lines.append(f"{item.cell}: {item.message}")
                report_lines.append(f"  Formula: {item.formula}")
            report_lines.append("")

        return "\n".join(report_lines).strip()

    def _analyze_formula(self, cell: str, formula: str) -> List[FormulaIssue]:
        issues: List[FormulaIssue] = []

        stripped = re.sub(r'"[^"]*"', '""', formula)
        open_count = stripped.count("(")
        close_count = stripped.count(")")
        if open_count != close_count:
            issues.append(
                FormulaIssue(
                    cell=cell,
                    formula=formula,
                    severity="error",
                    message=f"Unmatched parentheses (open={open_count}, close={close_count})",
                )
            )

        if re.search(r'/\s*(0|"0")', formula):
            issues.append(
                FormulaIssue(
                    cell=cell,
                    formula=formula,
                    severity="warning",
                    message="Formula divides by a zero literal.",
                )
            )

        if re.search(r'\bIF\s*\(\s*[^,]+,\s*\)', formula.upper()):
            issues.append(
                FormulaIssue(
                    cell=cell,
                    formula=formula,
                    severity="error",
                    message="IF statement missing value_if_true/value_if_false.",
                )
            )

        return issues

    def _get_values(self, spreadsheet_id: str, sheet_name: str, render_option: str) -> List[List[Any]]:
        result = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"'{sheet_name}'",
            valueRenderOption=render_option,
            majorDimension="ROWS",
        ).execute()
        return result.get("values", [])

    @staticmethod
    def _build_repeat_cell(sheet_id: int, row_index: int, start_col: int, end_col: int, color: Color) -> Dict[str, Any]:
        return {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": row_index,
                    "endRowIndex": row_index + 1,
                    "startColumnIndex": start_col,
                    "endColumnIndex": end_col,
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": color,
                    }
                },
                "fields": "userEnteredFormat.backgroundColor",
            }
        }

    @staticmethod
    def _is_integer(value: Any) -> bool:
        if isinstance(value, bool):
            return False
        if isinstance(value, int):
            return True
        if isinstance(value, float):
            return value.is_integer()
        if isinstance(value, str):
            return bool(re.fullmatch(r"-?\d+", value.strip()))
        return False

    @staticmethod
    def _cell_address(row: int, col: int) -> str:
        label = ""
        while col > 0:
            col -= 1
            label = chr(65 + col % 26) + label
            col //= 26
        return f"{label}{row}"


def main():
    """# * No-arg entrypoint using hardcoded defaults"""
    spreadsheet_url = DEFAULT_SPREADSHEET_URL
    credentials_path = DEFAULT_CREDENTIALS_PATH

    url_id_match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", spreadsheet_url)
    url_gid_match = re.search(r"[?&]gid=(\d+)", spreadsheet_url)
    spreadsheet_id = url_id_match.group(1) if url_id_match else spreadsheet_url
    gid = int(url_gid_match.group(1)) if url_gid_match else None

    validator = GoogleSheetsFormulaValidator(credentials_path)

    spreadsheet = validator.fetch_spreadsheet(spreadsheet_id)
    sheets = spreadsheet.get("sheets", [])
    if not sheets:
        raise ValueError("No sheets found in spreadsheet.")

    if gid is not None:
        matching = next((sheet for sheet in sheets if sheet["properties"].get("sheetId") == gid), None)
        if matching is None:
            raise ValueError(f"No sheet found with gid={gid}.")
        sheet_properties = matching["properties"]
    else:
        sheet_properties = sheets[0]["properties"]

    sheet_name = sheet_properties["title"]
    sheet_id = sheet_properties["sheetId"]

    formulas = validator.get_formulas(spreadsheet_id, sheet_name)
    issues = validator.analyze_formulas(formulas)

    print()
    print(validator.report_issues(issues))
    print()
    print("Applying highlighting for formulas and integers...")
    validator.apply_highlighting(spreadsheet_id, sheet_id, sheet_name)


if __name__ == "__main__":
    main()

