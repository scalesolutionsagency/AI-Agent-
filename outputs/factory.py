"""Factory for creating output handlers."""

from typing import Dict, Any, List
from outputs.base import OutputHandler
from outputs.csv_output import CSVOutputHandler
from outputs.json_output import JSONOutputHandler
from outputs.google_sheets import GoogleSheetsOutputHandler
from outputs.notion_output import NotionOutputHandler


class OutputFactory:
    """Factory for creating output handler instances."""
    
    @staticmethod
    def create_local_outputs(
        format_type: str,
        config: Dict[str, Any]
    ) -> List[OutputHandler]:
        """Create local file output handlers (CSV/JSON).
        
        Args:
            format_type: Output format (csv, json, both)
            config: Output configuration
            
        Returns:
            List of output handlers
        """
        handlers = []
        
        if format_type in ["csv", "both"]:
            handlers.append(CSVOutputHandler(config))
        
        if format_type in ["json", "both"]:
            handlers.append(JSONOutputHandler(config))
        
        return handlers
    
    @staticmethod
    def create_google_sheets_output(config: Dict[str, Any]) -> OutputHandler:
        """Create Google Sheets output handler.
        
        Args:
            config: Output configuration
            
        Returns:
            Google Sheets output handler
        """
        return GoogleSheetsOutputHandler(config)
    
    @staticmethod
    def create_notion_output(config: Dict[str, Any]) -> OutputHandler:
        """Create Notion output handler.
        
        Args:
            config: Output configuration
            
        Returns:
            Notion output handler
        """
        return NotionOutputHandler(config)
