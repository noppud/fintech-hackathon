#!/usr/bin/env python3
"""
Test script for the /tools/update_cells endpoint.

This demonstrates how to use the cell update API to fix issues in Google Sheets.
"""

import json
import requests
from typing import List, Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"  # Adjust if your API runs on a different port
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/16Mh8TsyBjUgFFpl4bJuJYtH1niXGOKnGO0USxsfxaTk/edit"  # Optional: will use env default if not provided


def update_cells(
    updates: List[Dict[str, Any]],
    spreadsheet_id: str = None,
    sheet_title: str = "Sheet1",
    create_snapshot: bool = True,
) -> Dict[str, Any]:
    """
    Update cells in a Google Spreadsheet.

    Args:
        updates: List of cell updates, each with:
            - cell_location: A1 notation (e.g., "A1" or "B2:C5")
            - value: New value (string, number, boolean, or None)
            - is_formula: Optional, set to True if value is a formula
        spreadsheet_id: Optional spreadsheet URL or ID
        sheet_title: Sheet name (defaults to "Sheet1")
        create_snapshot: Whether to create undo snapshot

    Returns:
        Response dict with status, message, count, and snapshot_batch_id
    """
    url = f"{API_BASE_URL}/tools/update_cells"
    payload = {
        "updates": updates,
        "sheet_title": sheet_title,
        "create_snapshot": create_snapshot,
    }

    if spreadsheet_id:
        payload["spreadsheet_id"] = spreadsheet_id

    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()


def restore_cells(snapshot_batch_id: str, cell_locations: List[str] = None) -> Dict[str, Any]:
    """
    Restore cells from a snapshot.

    Args:
        snapshot_batch_id: Snapshot ID from update_cells response
        cell_locations: Optional list of specific cells to restore

    Returns:
        Response dict with status, message, and count
    """
    url = f"{API_BASE_URL}/tools/restore_cells"
    payload = {"snapshot_batch_id": snapshot_batch_id}

    if cell_locations:
        payload["cell_locations"] = cell_locations

    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()


def example_fix_broken_reference():
    """Example: Fix a broken reference error in cell A7."""
    print("\n=== Example 1: Fix Broken Reference ===")

    # Issue from the detection results:
    # Cell A7 contains '#ERROR: REF' which indicates a broken cell reference

    updates = [
        {
            "cell_location": "A7",
            "value": None,  # Clear the broken formula
        }
    ]

    result = update_cells(updates)
    print(f"✓ {result['message']}")
    print(f"  Snapshot ID: {result.get('snapshot_batch_id')}")

    return result.get("snapshot_batch_id")


def example_fix_phone_number():
    """Example: Fix incomplete phone number in cell O2."""
    print("\n=== Example 2: Fix Incomplete Phone Number ===")

    # Issue: The phone number in row 2 ('+358501968') appears incomplete

    updates = [
        {
            "cell_location": "O2",
            "value": "+358501968123",  # Complete phone number
        }
    ]

    result = update_cells(updates)
    print(f"✓ {result['message']}")

    return result.get("snapshot_batch_id")


def example_fix_column_headers():
    """Example: Fix inconsistent column naming."""
    print("\n=== Example 3: Fix Column Headers (Batch Update) ===")

    # Issue: Generic column labels (14, B, D, F, etc.) should have descriptive names

    updates = [
        {"cell_location": "B1", "value": "Yritys"},
        {"cell_location": "D1", "value": "Y-tunnus"},
        {"cell_location": "F1", "value": "Osoite"},
        {"cell_location": "G1", "value": "Postinumero"},
        {"cell_location": "H1", "value": "Kaupunki"},
        {"cell_location": "I1", "value": "Maa"},
    ]

    result = update_cells(updates)
    print(f"✓ {result['message']}")
    print(f"  Updated {result['count']} column headers")

    return result.get("snapshot_batch_id")


def example_fix_date_formatting():
    """Example: Fix date format with formula."""
    print("\n=== Example 4: Fix Date Formatting with Formula ===")

    # Issue: Row 9 contains Excel serial numbers instead of proper dates

    updates = [
        {
            "cell_location": "C9",
            "value": "=TEXT(45964.84996082176, \"DD.MM.YYYY\")",
            "is_formula": True,
        }
    ]

    result = update_cells(updates)
    print(f"✓ {result['message']}")

    return result.get("snapshot_batch_id")


def example_batch_update_range():
    """Example: Update a range of cells with the same value."""
    print("\n=== Example 5: Batch Update Range ===")

    # Clear empty rows or fill with placeholder

    updates = [
        {
            "cell_location": "A3:Z6",  # Clear empty rows
            "value": None,
        }
    ]

    result = update_cells(updates)
    print(f"✓ {result['message']}")

    return result.get("snapshot_batch_id")


def example_undo_changes(snapshot_batch_id: str):
    """Example: Restore cells to original values."""
    print("\n=== Example 6: Undo Changes ===")

    if not snapshot_batch_id:
        print("⚠ No snapshot ID provided, skipping undo example")
        return

    result = restore_cells(snapshot_batch_id)
    print(f"✓ {result['message']}")


def example_ai_tool_calling_format():
    """
    Example: Format that an AI assistant would use when calling the update_cells tool.

    This shows how the endpoint integrates with AI tool-calling systems.
    """
    print("\n=== Example 7: AI Tool-Calling Format ===")

    # AI detects issues and generates fix proposals
    tool_call = {
        "tool_name": "update_cells",
        "parameters": {
            "updates": [
                {
                    "cell_location": "A7",
                    "value": "",
                    "is_formula": False,
                },
                {
                    "cell_location": "O2",
                    "value": "+358501968123",
                    "is_formula": False,
                },
            ],
            "sheet_title": "Sheet1",
            "create_snapshot": True,
        },
    }

    print("AI would call the endpoint with:")
    print(json.dumps(tool_call, indent=2))

    # Make actual API call
    result = update_cells(**tool_call["parameters"])
    print(f"\n✓ {result['message']}")

    return result


def main():
    """Run all examples."""
    print("=" * 60)
    print("Cell Update API Test Suite")
    print("=" * 60)

    try:
        # Run examples
        snapshot1 = example_fix_broken_reference()
        snapshot2 = example_fix_phone_number()
        snapshot3 = example_fix_column_headers()
        snapshot4 = example_fix_date_formatting()
        snapshot5 = example_batch_update_range()

        # Demonstrate undo
        example_undo_changes(snapshot5)

        # AI integration example
        example_ai_tool_calling_format()

        print("\n" + "=" * 60)
        print("✓ All tests completed successfully!")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server.")
        print(f"   Make sure the API is running at {API_BASE_URL}")
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ API Error: {e}")
        print(f"   Response: {e.response.text}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
