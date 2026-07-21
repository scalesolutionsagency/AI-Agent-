"""JSON output handler."""

import json
from pathlib import Path
from typing import Dict, Any, List
from outputs.base import OutputHandler
from datetime import datetime


class JSONOutputHandler(OutputHandler):
    """Write leads to JSON file."""
    
    async def write(self, leads: List[Dict[str, Any]]) -> None:
        """Write leads to JSON file.
        
        Args:
            leads: List of leads to write
        """
        if not leads:
            return
        
        output_dir = Path(self.config.get("output_dir", "./output"))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = output_dir / f"leads_{timestamp}.json"
        
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "total_leads": len(leads),
            "leads": leads,
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
