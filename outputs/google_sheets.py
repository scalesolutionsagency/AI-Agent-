"""Google Sheets output handler."""

import os
import json
from typing import Dict, Any, List
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.api_core.exceptions import GoogleAPIError
from googleapiclient.discovery import build
from outputs.base import OutputHandler
from datetime import datetime


class GoogleSheetsOutputHandler(OutputHandler):
    """Write leads to Google Sheets."""
    
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Google Sheets handler.
        
        Args:
            config: Output configuration
        """
        super().__init__(config)
        self.sheet_id = os.getenv("GOOGLE_SHEET_ID")
        self.tab_name = os.getenv("GOOGLE_SHEET_TAB_NAME", "Leads")
        self.credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH")
        
        if not self.sheet_id:
            raise ValueError("GOOGLE_SHEET_ID environment variable not set")
        if not self.credentials_path:
            raise ValueError("GOOGLE_SHEETS_CREDENTIALS_PATH environment variable not set")
        
        self.service = self._init_service()
    
    def _init_service(self):
        """Initialize Google Sheets service.
        
        Returns:
            Sheets API service
        """
        credentials = Credentials.from_service_account_file(
            self.credentials_path,
            scopes=self.SCOPES
        )
        return build("sheets", "v4", credentials=credentials)
    
    async def write(self, leads: List[Dict[str, Any]]) -> None:
        """Write leads to Google Sheet.
        
        Args:
            leads: List of leads to write
        """
        if not leads:
            return
        
        try:
            # Get all field names
            fieldnames = set()
            for lead in leads:
                fieldnames.update(lead.keys())
            fieldnames = sorted(list(fieldnames))
            
            # Prepare data
            append_mode = self.config.get("google_sheets", {}).get("append_mode", True)
            
            if append_mode:
                # Append to existing sheet
                values = self._leads_to_rows(leads, fieldnames)
            else:
                # Clear and replace
                self.service.spreadsheets().values().clear(
                    spreadsheetId=self.sheet_id,
                    range=self.tab_name
                ).execute()
                
                # Add header and leads
                values = [fieldnames] + self._leads_to_rows(leads, fieldnames)
            
            # Update sheet
            range_name = f"{self.tab_name}!A1"
            body = {"values": values}
            
            if append_mode:
                self.service.spreadsheets().values().append(
                    spreadsheetId=self.sheet_id,
                    range=range_name,
                    valueInputOption="RAW",
                    body=body
                ).execute()
            else:
                self.service.spreadsheets().values().update(
                    spreadsheetId=self.sheet_id,
                    range=range_name,
                    valueInputOption="RAW",
                    body=body
                ).execute()
            
            # Auto-resize columns
            if self.config.get("google_sheets", {}).get("auto_resize_columns", True):
                self._auto_resize_columns(len(fieldnames))
        
        except GoogleAPIError as e:
            raise RuntimeError(f"Failed to write to Google Sheets: {e}")
    
    @staticmethod
    def _leads_to_rows(
        leads: List[Dict[str, Any]],
        fieldnames: List[str]
    ) -> List[List[str]]:
        """Convert leads to rows for sheet.
        
        Args:
            leads: Leads to convert
            fieldnames: Column names
            
        Returns:
            Rows for sheet
        """
        rows = []
        for lead in leads:
            row = [
                str(lead.get(field, "")) if lead.get(field) is not None else ""
                for field in fieldnames
            ]
            rows.append(row)
        return rows
    
    def _auto_resize_columns(self, num_columns: int) -> None:
        """Auto-resize sheet columns.
        
        Args:
            num_columns: Number of columns to resize
        """
        try:
            request = {
                "requests": [
                    {
                        "autoResizeDimensions": {
                            "dimensions": {
                                "sheetId": 0,
                                "dimension": "COLUMNS",
                                "startIndex": 0,
                                "endIndex": num_columns,
                            }
                        }
                    }
                ]
            }
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.sheet_id,
                body=request
            ).execute()
        except GoogleAPIError:
            # Non-critical, skip if fails
            pass
