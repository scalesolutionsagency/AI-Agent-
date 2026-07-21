"""Base class for lead sources."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class LeadSource(ABC):
    """Abstract base class for lead sources."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize lead source.
        
        Args:
            config: Source-specific configuration
        """
        self.config = config
    
    @abstractmethod
    async def search(
        self,
        business_type: str,
        location: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Search for leads.
        
        Args:
            business_type: Type of business to search for
            location: Location to search in
            limit: Maximum number of results
            
        Returns:
            List of lead dictionaries with: business_name, phone_number, email, website, address
        """
        pass
