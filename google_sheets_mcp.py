"""Google Sheets MCP server for reading and editing spreadsheets.

The server exposes tools for listing worksheets, reading ranges, writing
values, appending rows, and clearing data. Authentication uses a Google
service account provided via ``GOOGLE_SERVICE_ACCOUNT_JSON`` (file path or
JSON string).
"""

import json
import logging
import os
import sys
from typing import List, Sequence

from fastmcp import FastMCP
from google.oauth2.service_account import Credentials
import gspread

logger = logging.getLogger("GoogleSheetsMCP")

# Ensure UTF-8 encoding on Windows consoles
if sys.platform == "win32":
    sys.stderr.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

mcp = FastMCP("GoogleSheets")


def _load_service_account_info(raw: str) -> dict:
    """Load service account JSON from a path or raw JSON string."""
    if not raw:
        raise RuntimeError(
            "GOOGLE_SERVICE_ACCOUNT_JSON is required (path to JSON file or raw JSON string)"
        )

    if os.path.exists(raw):
        with open(raw, "r", encoding="utf-8") as f:
            return json.load(f)

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "GOOGLE_SERVICE_ACCOUNT_JSON must be a file path or valid JSON string"
        ) from exc


def _get_client() -> gspread.Client:
    raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    info = _load_service_account_info(raw)
    credentials = Credentials.from_service_account_info(info, scopes=SCOPES)
    return gspread.authorize(credentials)


def _get_worksheet(spreadsheet_id: str, worksheet_name: str) -> gspread.Worksheet:
    client = _get_client()
    spreadsheet = client.open_by_key(spreadsheet_id)
    return spreadsheet.worksheet(worksheet_name)


def _normalize_values(values: Sequence[Sequence[str]]) -> List[List[str]]:
    """Convert incoming sequences to a list-of-lists while preserving strings.

    This is helpful because some callers may pass tuples or other iterables.
    """
    return [list(row) for row in values]


@mcp.tool()
def list_worksheets(spreadsheet_id: str) -> dict:
    """List all worksheet titles for the given spreadsheet ID."""
    client = _get_client()
    spreadsheet = client.open_by_key(spreadsheet_id)
    titles = [ws.title for ws in spreadsheet.worksheets()]
    logger.info("Listed worksheets for %s: %s", spreadsheet_id, ", ".join(titles))
    return {"success": True, "worksheets": titles}


@mcp.tool()
def read_range(spreadsheet_id: str, worksheet_name: str, cell_range: str) -> dict:
    """Read values from a worksheet cell range (e.g., "A1:C10")."""
    worksheet = _get_worksheet(spreadsheet_id, worksheet_name)
    values = worksheet.get(cell_range)
    logger.info(
        "Read %d rows from %s!%s", len(values), worksheet_name, cell_range
    )
    return {"success": True, "values": values}


@mcp.tool()
def write_range(
    spreadsheet_id: str,
    worksheet_name: str,
    start_cell: str,
    values: Sequence[Sequence[str]],
) -> dict:
    """Overwrite a block of cells starting at ``start_cell`` with provided values."""
    worksheet = _get_worksheet(spreadsheet_id, worksheet_name)
    normalized = _normalize_values(values)
    worksheet.update(start_cell, normalized)
    logger.info(
        "Wrote %d rows to %s!%s", len(normalized), worksheet_name, start_cell
    )
    return {"success": True, "rows_written": len(normalized)}


@mcp.tool()
def append_rows(
    spreadsheet_id: str,
    worksheet_name: str,
    rows: Sequence[Sequence[str]],
    table_range: str | None = None,
) -> dict:
    """Append rows to the end of a worksheet.

    ``table_range`` is optional; when provided (e.g., "A1:C1"), it defines the
    columns to append to, matching Google Sheets API semantics.
    """
    worksheet = _get_worksheet(spreadsheet_id, worksheet_name)
    normalized = _normalize_values(rows)
    worksheet.append_rows(normalized, table_range=table_range)
    logger.info(
        "Appended %d rows to %s (table_range=%s)",
        len(normalized),
        worksheet_name,
        table_range,
    )
    return {"success": True, "rows_appended": len(normalized)}


@mcp.tool()
def clear_range(spreadsheet_id: str, worksheet_name: str, cell_range: str) -> dict:
    """Clear the contents of a range (e.g., "B2:D20")."""
    worksheet = _get_worksheet(spreadsheet_id, worksheet_name)
    worksheet.batch_clear([cell_range])
    logger.info("Cleared range %s!%s", worksheet_name, cell_range)
    return {"success": True, "cleared": cell_range}


if __name__ == "__main__":
    mcp.run(transport="stdio")
