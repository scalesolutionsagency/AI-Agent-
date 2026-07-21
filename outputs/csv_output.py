"""CSV output handler."""

import csv
from pathlib import Path
from typing import Dict, Any, List
from outputs.base import OutputHandler
from datetime import datetime


class CSVOutputHandler(OutputHandler):
    """Write leads to CSV file."""
    
    async def write(self, leads: List[Dict[str, Any]]) -> None:
        """Write leads to CSV file.
        
        Args:
            leads: List of leads to write
        """
        if not leads:
            return
        
        output_dir = Path(self.config.get("output_dir", "./output"))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = output_dir / f"leads_{timestamp}.csv"
        
        # Get all possible fields from leads
        fieldnames = set()
        for lead in leads:
            fieldnames.update(lead.keys())
        
        # Sort for consistent ordering
        fieldnames = sorted(list(fieldnames))
        
        # Write CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(leads)
