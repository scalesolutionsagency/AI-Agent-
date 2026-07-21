"""Lead deduplication logic."""

import json
from pathlib import Path
from typing import Dict, Any, List, Set
from datetime import datetime
import hashlib


class LeadDeduplicator:
    """Deduplicate leads against a running history."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize deduplicator.
        
        Args:
            config: Deduplication configuration
        """
        self.config = config
        self.enabled = config.get("enabled", True)
        self.check_fields = config.get("check_fields", ["phone_number", "email", "website"])
        self.history_file = Path(config.get("history_file", "./data/leads_history.json"))
        self.keep_history = config.get("keep_history", True)
        self.history = self._load_history()
    
    def deduplicate(self, leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate leads based on check fields.
        
        Args:
            leads: List of leads to deduplicate
            
        Returns:
            Deduplicated leads
        """
        if not self.enabled:
            return leads
        
        unique_leads = []
        seen_hashes = set(self.history.get("lead_hashes", []))
        new_hashes = []
        
        for lead in leads:
            lead_hash = self._hash_lead(lead)
            
            if lead_hash not in seen_hashes:
                unique_leads.append(lead)
                seen_hashes.add(lead_hash)
                new_hashes.append(lead_hash)
        
        # Update history
        if self.keep_history:
            self.history["lead_hashes"].extend(new_hashes)
            self.history["last_updated"] = datetime.now().isoformat()
            self._save_history()
        
        return unique_leads
    
    def _hash_lead(self, lead: Dict[str, Any]) -> str:
        """Create hash of lead based on check fields.
        
        Args:
            lead: Lead to hash
            
        Returns:
            Hash string
        """
        values = []
        for field in self.check_fields:
            value = lead.get(field, "")
            if value:
                values.append(str(value).lower().strip())
        
        hash_str = "|".join(values)
        return hashlib.md5(hash_str.encode()).hexdigest()
    
    def _load_history(self) -> Dict[str, Any]:
        """Load history from file.
        
        Returns:
            History dictionary
        """
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {"lead_hashes": [], "last_updated": None}
        
        return {"lead_hashes": [], "last_updated": None}
    
    def _save_history(self) -> None:
        """Save history to file."""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
