from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from .google_sheets import DEFAULT_SPREADSHEET_URL
from .function_to_color_things import apply_colors_to_sheet
from .snapshot_input_colors import snapshot_ranges_to_supabase
from .visulize_formulas import visualize_formulas
from .restore_input_colors import restore_snapshot_batch

Color = Dict[str, float]


def apply_colors_tool(requests: List[Dict[str, Any]]) -> Dict[str, Any]:
    """# * Snapshot existing colors and apply new colors via tools package."""
    if not requests:
        raise ValueError("No color requests provided.")

    sheet_url: Optional[str] = None

    normalized_ranges: List[str] = []
    entries: List[Dict[str, Any]] = []

    for idx, req in enumerate(requests):
        cell_location = req.get("cell_location")
        message = req.get("message")
        color = req.get("color")
        url = req.get("url")

        if not isinstance(cell_location, str) or not cell_location.strip():
            raise ValueError(f"Request #{idx} missing 'cell_location'.")
        if not isinstance(message, str):
            raise ValueError(f"Request #{idx} missing 'message'.")
        if not isinstance(color, str):
            raise ValueError(f"Request #{idx} missing 'color'.")
        if not isinstance(url, str) or not url.strip():
            raise ValueError(f"Request #{idx} missing 'url'.")

        normalized_url = url.strip()
        if sheet_url is None:
            sheet_url = normalized_url
        elif normalized_url != sheet_url:
            raise ValueError("All color requests must target the same 'url'.")

        normalized_cell = cell_location.strip().upper()
        normalized_ranges.append(normalized_cell)
        entries.append(
            {
                "cell_location": normalized_cell,
                "message": message.strip(),
                "color": _hex_color_to_rgb(color.strip()),
            }
        )

    if sheet_url is None:
        sheet_url = DEFAULT_SPREADSHEET_URL
    if not sheet_url:
        raise ValueError("Sheet URL must be provided via request payload.")

    snapshot_result = snapshot_ranges_to_supabase(normalized_ranges, sheet_url)
    apply_result = apply_colors_to_sheet(entries, sheet_url)
    apply_result["snapshot_batch_id"] = snapshot_result.get("first_snapshot_batch_id")
    return apply_result


def visualize_formulas_tool() -> Dict[str, Any]:
    """# * Run the visualize formulas tool for the configured sheet."""
    result = visualize_formulas(DEFAULT_SPREADSHEET_URL)
    # * Ensure consistent keys for clients expecting snapshot field
    if "snapshot_batch_id" not in result:
        result["snapshot_batch_id"] = None
    return result


def restore_colors_tool(
    snapshot_batch_id: str,
    cell_locations: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """# * Restore colors from a snapshot batch using tools package logic."""
    normalized_ranges = None
    if cell_locations:
        normalized_ranges = []
        for idx, range_ref in enumerate(cell_locations):
            if not isinstance(range_ref, str) or not range_ref.strip():
                raise ValueError(f"Range #{idx} is invalid.")
            normalized_ranges.append(range_ref.strip().upper())

    return restore_snapshot_batch(
        snapshot_batch_id=snapshot_batch_id,
        sheet_url=DEFAULT_SPREADSHEET_URL,
        expected_ranges=normalized_ranges,
    )


def _hex_color_to_rgb(value: str) -> Color:
    """# * Convert hex color to RGB dictionary."""
    match = re.fullmatch(r"#?([0-9A-Fa-f]{6})", value)
    if not match:
        raise ValueError(f"Invalid hex color '{value}'.")
    hex_value = match.group(1)
    red = int(hex_value[0:2], 16) / 255.0
    green = int(hex_value[2:4], 16) / 255.0
    blue = int(hex_value[4:6], 16) / 255.0
    return {"red": red, "green": green, "blue": blue}

