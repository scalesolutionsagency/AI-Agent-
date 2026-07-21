"""Notion output handler."""

import os
from typing import Dict, Any, List
from notion_client import Client
from outputs.base import OutputHandler


class NotionOutputHandler(OutputHandler):
    """Write leads to Notion database."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Notion handler.
        
        Args:
            config: Output configuration
        """
        super().__init__(config)
        self.api_token = os.getenv("NOTION_API_TOKEN")
        self.database_id = os.getenv("NOTION_DATABASE_ID")
        
        if not self.api_token:
            raise ValueError("NOTION_API_TOKEN environment variable not set")
        if not self.database_id:
            raise ValueError("NOTION_DATABASE_ID environment variable not set")
        
        self.client = Client(auth=self.api_token)
    
    async def write(self, leads: List[Dict[str, Any]]) -> None:
        """Write leads to Notion database.
        
        Args:
            leads: List of leads to write
        """
        if not leads:
            return
        
        try:
            for lead in leads:
                self._create_page(lead)
        except Exception as e:
            raise RuntimeError(f"Failed to write to Notion: {e}")
    
    def _create_page(self, lead: Dict[str, Any]) -> None:
        """Create a page in Notion for a lead.
        
        Args:
            lead: Lead data
        """
        properties = self._lead_to_notion_properties(lead)
        
        self.client.pages.create(
            parent={"database_id": self.database_id},
            properties=properties
        )
    
    @staticmethod
    def _lead_to_notion_properties(lead: Dict[str, Any]) -> Dict[str, Any]:
        """Convert lead to Notion page properties.
        
        Args:
            lead: Lead data
            
        Returns:
            Notion page properties
        """
        properties = {}
        
        # Map common fields to Notion properties
        field_mapping = {
            "business_name": "Title",
            "phone_number": "Phone",
            "email": "Email",
            "website": "Website",
            "address": "Address",
            "city": "City",
            "state": "State",
            "zip_code": "Zip",
            "source": "Source",
        }
        
        for field, property_name in field_mapping.items():
            value = lead.get(field)
            if value:
                if property_name == "Title":
                    properties[property_name] = {
                        "title": [{"text": {"content": str(value)}}]
                    }
                else:
                    properties[property_name] = {
                        "rich_text": [{"text": {"content": str(value)}}]
                    }
        
        return properties
