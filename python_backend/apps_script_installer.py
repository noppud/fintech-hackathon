"""
Apps Script Installer

Programmatically installs the Mangler AI Copilot extension to Google Sheets
using the Apps Script API.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from google.oauth2 import service_account
from google.oauth2.credentials import Credentials as UserCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class AppsScriptInstaller:
    """
    Installs Apps Script extensions to Google Sheets using the Apps Script API.
    """

    def __init__(
        self,
        credentials_path: Optional[str] = None,
        user_credentials: Optional[UserCredentials] = None,
    ) -> None:
        """
        Initialize the Apps Script installer with service account credentials.

        Args:
            credentials_path: Path to service account JSON file. If None, uses env vars.
            user_credentials: Optional OAuth credentials for an authenticated Google user.
        """
        scopes = [
            "https://www.googleapis.com/auth/script.projects",
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/spreadsheets",
        ]

        if user_credentials is not None:
            # Assume the provided credentials already have the correct scopes granted.
            self._script = build("script", "v1", credentials=user_credentials, cache_discovery=False)
            self._drive = build("drive", "v3", credentials=user_credentials, cache_discovery=False)
            return

        # Try environment variable first (for Railway/hosted environments)
        if credentials_path is None:
            env_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
            if env_json:
                try:
                    info = json.loads(env_json)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        "GOOGLE_SERVICE_ACCOUNT_JSON is set but does not contain valid JSON."
                    ) from exc

                creds = service_account.Credentials.from_service_account_info(
                    info, scopes=scopes
                )
                self._script = build("script", "v1", credentials=creds, cache_discovery=False)
                self._drive = build("drive", "v3", credentials=creds, cache_discovery=False)
                return

        # Fall back to file-based credentials
        if credentials_path is None:
            backend_root = Path(__file__).resolve().parent
            env_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")

            candidate_paths = []
            if env_path:
                candidate_paths.append(Path(env_path))
            candidate_paths.append(backend_root / "service-account.json")

            resolved_path = None
            for candidate in candidate_paths:
                if candidate and candidate.is_file():
                    resolved_path = candidate
                    break

            if not resolved_path:
                raise FileNotFoundError(
                    "Could not find Google service account key JSON. "
                    "Set GOOGLE_SERVICE_ACCOUNT_FILE or GOOGLE_SERVICE_ACCOUNT_JSON."
                )

            credentials_path = str(resolved_path)

        creds = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=scopes
        )

        self._script = build("script", "v1", credentials=creds, cache_discovery=False)
        self._drive = build("drive", "v3", credentials=creds, cache_discovery=False)

    def install_extension(
        self,
        spreadsheet_id: str,
        code_gs_content: str,
        sidebar_html_content: str,
    ) -> Dict[str, Any]:
        """
        Install the Mangler AI Copilot extension to a Google Sheet.

        Args:
            spreadsheet_id: The ID of the spreadsheet (from URL)
            code_gs_content: Content of Code.gs file
            sidebar_html_content: Content of Sidebar.html file

        Returns:
            Dict with installation status and script project ID

        Raises:
            HttpError: If installation fails
        """
        try:
            # Step 1: Create a container-bound script project
            logger.info(f"Creating Apps Script project for spreadsheet {spreadsheet_id}")

            create_request = {
                "title": "Mangler AI Copilot",
                "parentId": spreadsheet_id,
            }

            project = self._script.projects().create(body=create_request).execute()
            script_id = project.get("scriptId")

            logger.info(f"Created script project with ID: {script_id}")

            # Step 2: Prepare the script files
            files = [
                {
                    "name": "appsscript",
                    "type": "JSON",
                    "source": json.dumps({
                        "timeZone": "America/New_York",
                        "dependencies": {},
                        "exceptionLogging": "STACKDRIVER",
                        "runtimeVersion": "V8",
                    }),
                },
                {
                    "name": "Code",
                    "type": "SERVER_JS",
                    "source": code_gs_content,
                },
                {
                    "name": "Sidebar",
                    "type": "HTML",
                    "source": sidebar_html_content,
                },
            ]

            # Step 3: Update the project content with our files
            logger.info(f"Updating script content for project {script_id}")

            content_request = {"files": files}

            updated_content = (
                self._script.projects()
                .updateContent(scriptId=script_id, body=content_request)
                .execute()
            )

            logger.info(f"Successfully installed extension to spreadsheet {spreadsheet_id}")

            return {
                "success": True,
                "scriptId": script_id,
                "spreadsheetId": spreadsheet_id,
                "message": "Extension installed successfully",
                "filesUpdated": len(updated_content.get("files", [])),
            }

        except HttpError as error:
            logger.error(f"Failed to install extension: {error}")
            error_details = error.error_details if hasattr(error, "error_details") else str(error)

            return {
                "success": False,
                "error": str(error),
                "errorDetails": error_details,
                "message": f"Installation failed: {error}",
            }

    def check_sheet_access(self, spreadsheet_id: str) -> Dict[str, Any]:
        """
        Check if the service account has access to the spreadsheet.

        Args:
            spreadsheet_id: The ID of the spreadsheet

        Returns:
            Dict with access status and spreadsheet metadata
        """
        try:
            # Try to get the spreadsheet metadata from Drive API
            file_metadata = (
                self._drive.files()
                .get(fileId=spreadsheet_id, fields="id,name,permissions,owners")
                .execute()
            )

            return {
                "hasAccess": True,
                "spreadsheetId": spreadsheet_id,
                "name": file_metadata.get("name", "Unknown"),
                "owners": file_metadata.get("owners", []),
            }

        except HttpError as error:
            logger.warning(f"No access to spreadsheet {spreadsheet_id}: {error}")

            return {
                "hasAccess": False,
                "spreadsheetId": spreadsheet_id,
                "error": str(error),
                "message": "Service account does not have access to this spreadsheet",
            }

    def get_service_account_email(self) -> str:
        """
        Get the email address of the service account.

        Returns:
            Service account email address
        """
        # Try to extract from credentials
        env_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        if env_json:
            try:
                info = json.loads(env_json)
                return info.get("client_email", "Unknown")
            except:
                pass

        # Try from file
        env_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
        if env_path and Path(env_path).exists():
            with open(env_path) as f:
                info = json.load(f)
                return info.get("client_email", "Unknown")

        backend_root = Path(__file__).resolve().parent
        service_account_path = backend_root / "service-account.json"
        if service_account_path.exists():
            with open(service_account_path) as f:
                info = json.load(f)
                return info.get("client_email", "Unknown")

        return "Unknown service account"
