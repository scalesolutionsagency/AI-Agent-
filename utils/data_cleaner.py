"""Data cleaning and normalization utilities."""

import re
from typing import Dict, Any, Optional
from email_validator import validate_email, EmailNotValidError
import phonenumbers


class DataCleaner:
    """Clean and normalize lead data."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize cleaner with configuration.
        
        Args:
            config: Data cleaning configuration
        """
        self.config = config
    
    def clean(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize a single lead.
        
        Args:
            lead: Raw lead data
            
        Returns:
            Cleaned lead data
        """
        cleaned = lead.copy()
        
        # Trim whitespace
        if self.config.get("trim_whitespace", True):
            cleaned = self._trim_whitespace(cleaned)
        
        # Normalize phone
        if self.config.get("normalize_phone", True):
            cleaned = self._normalize_phone(cleaned)
        
        # Validate email
        if self.config.get("validate_email", True):
            cleaned = self._validate_email(cleaned)
        
        # Remove empty fields
        if self.config.get("remove_empty_fields", True):
            cleaned = self._remove_empty_fields(cleaned)
        
        return cleaned
    
    @staticmethod
    def _trim_whitespace(lead: Dict[str, Any]) -> Dict[str, Any]:
        """Trim whitespace from string values."""
        for key, value in lead.items():
            if isinstance(value, str):
                lead[key] = value.strip()
        return lead
    
    @staticmethod
    def _normalize_phone(lead: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize phone numbers to standard format."""
        if "phone_number" in lead and lead["phone_number"]:
            try:
                parsed = phonenumbers.parse(lead["phone_number"], "US")
                lead["phone_number"] = phonenumbers.format_number(
                    parsed,
                    phonenumbers.PhoneNumberFormat.E164
                )
            except phonenumbers.NumberParseException:
                # Keep original if parsing fails
                pass
        return lead
    
    @staticmethod
    def _validate_email(lead: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize email addresses."""
        if "email" in lead and lead["email"]:
            try:
                valid = validate_email(lead["email"])
                lead["email"] = valid.email
            except EmailNotValidError:
                # Remove invalid email
                lead["email"] = None
        return lead
    
    @staticmethod
    def _remove_empty_fields(lead: Dict[str, Any]) -> Dict[str, Any]:
        """Remove None and empty string values."""
        return {
            k: v for k, v in lead.items()
            if v is not None and v != ""
        }
