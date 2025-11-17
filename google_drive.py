"""Google Drive MCP server providing Sheets and Docs editing tools."""
import json
import logging
import os
import sys
from functools import lru_cache
from typing import List, Optional

from fastmcp import FastMCP
from google.oauth2 import service_account
from googleapiclient.discovery import build

logger = logging.getLogger("GoogleDriveMCP")

if sys.platform == "win32":
    sys.stderr.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/documents",
]

mcp = FastMCP("GoogleDrive")


def _load_credentials():
    """Load Google service account credentials from env."""
    json_blob = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    json_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE")

    if json_blob:
        info = json.loads(json_blob)
        return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    if json_path and os.path.exists(json_path):
        return service_account.Credentials.from_service_account_file(json_path, scopes=SCOPES)

    raise RuntimeError(
        "Set GOOGLE_SERVICE_ACCOUNT_JSON or GOOGLE_SERVICE_ACCOUNT_FILE for Google API access."
    )


@lru_cache(maxsize=1)
def _sheets_service():
    return build("sheets", "v4", credentials=_load_credentials())


@lru_cache(maxsize=1)
def _docs_service():
    return build("docs", "v1", credentials=_load_credentials())


@mcp.tool()
def update_sheet_values(
    spreadsheet_id: str,
    range_name: str,
    values: List[List[str]],
    value_input_option: str = "RAW",
) -> dict:
    """Overwrite the given cell range in a Google Sheet with the provided values."""
    service = _sheets_service()
    body = {"values": values}
    result = (
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption=value_input_option,
            body=body,
        )
        .execute()
    )
    logger.info("Updated sheet %s range %s", spreadsheet_id, range_name)
    return {
        "success": True,
        "updatedRange": result.get("updatedRange"),
        "updatedRows": result.get("updatedRows"),
        "updatedColumns": result.get("updatedColumns"),
    }


@mcp.tool()
def append_sheet_rows(
    spreadsheet_id: str,
    range_name: str,
    values: List[List[str]],
    value_input_option: str = "RAW",
) -> dict:
    """Append rows to a Google Sheet in the specified range."""
    service = _sheets_service()
    body = {"values": values}
    result = (
        service.spreadsheets()
        .values()
        .append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption=value_input_option,
            insertDataOption="INSERT_ROWS",
            body=body,
        )
        .execute()
    )
    updates = result.get("updates", {})
    logger.info("Appended %s rows to sheet %s", updates.get("updatedRows"), spreadsheet_id)
    return {
        "success": True,
        "tableRange": updates.get("tableRange"),
        "updatedRange": updates.get("updatedRange"),
        "updatedRows": updates.get("updatedRows"),
    }


def _document_end_index(service, document_id: str) -> int:
    doc = service.documents().get(documentId=document_id).execute()
    content = doc.get("body", {}).get("content", [])
    if not content:
        return 1
    return content[-1].get("endIndex", 1)


def _document_length(service, document_id: str) -> int:
    """Return the end index for the full document body."""
    return _document_end_index(service, document_id)


@mcp.tool()
def append_document_text(document_id: str, text: str, location_index: Optional[int] = None) -> dict:
    """Insert text into a Google Doc at the provided location or at the end if omitted."""
    service = _docs_service()

    def _resolve_insert_index() -> int:
        doc_end = _document_end_index(service, document_id)
        max_insert_index = 1 if doc_end <= 1 else doc_end - 1
        if location_index is None:
            return max_insert_index
        if location_index < 1:
            raise ValueError("location_index must be >= 1.")
        if location_index > max_insert_index:
            raise ValueError(
                f"location_index {location_index} exceeds document end {max_insert_index}. "
                "Use a smaller index or omit the location to append at the end."
            )
        return location_index

    target_index = _resolve_insert_index()
    requests = [
        {
            "insertText": {
                "location": {"index": target_index},
                "text": text,
            }
        }
    ]
    response = (
        service.documents()
        .batchUpdate(documentId=document_id, body={"requests": requests})
        .execute()
    )
    logger.info("Inserted text into document %s at index %s", document_id, target_index)
    return {"success": True, "replies": response.get("replies", [])}


@mcp.tool()
def replace_document_text(document_id: str, find_text: str, replace_text: str, match_case: bool = False) -> dict:
    """Find and replace all occurrences of text within a Google Doc."""
    service = _docs_service()
    requests = [
        {
            "replaceAllText": {
                "containsText": {
                    "text": find_text,
                    "matchCase": match_case,
                },
                "replaceText": replace_text,
            }
        }
    ]
    response = (
        service.documents()
        .batchUpdate(documentId=document_id, body={"requests": requests})
        .execute()
    )
    logger.info(
        "Replaced text in document %s (match_case=%s) for pattern '%s'",
        document_id,
        match_case,
        find_text,
    )
    return {"success": True, "replies": response.get("replies", [])}


@mcp.tool()
def set_document_text(document_id: str, text: str) -> dict:
    """Replace the full body of a Google Doc with the provided text."""
    service = _docs_service()
    end_index = _document_length(service, document_id)
    requests = []
    if end_index > 1:
        requests.append({"deleteContentRange": {"range": {"startIndex": 1, "endIndex": end_index}}})
    requests.append({"insertText": {"location": {"index": 1}, "text": text}})

    response = (
        service.documents()
        .batchUpdate(documentId=document_id, body={"requests": requests})
        .execute()
    )
    logger.info("Replaced all content in document %s", document_id)
    return {"success": True, "replies": response.get("replies", [])}


if __name__ == "__main__":
    mcp.run(transport="stdio")
