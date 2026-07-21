"""Base class for output handlers."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class OutputHandler(ABC):
    """Abstract base class for output handlers."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize output handler.
        
        Args:
            config: Output configuration
        """
        self.config = config
    
    @abstractmethod
    async def write(self, leads: List[Dict[str, Any]]) -> None:
        """Write leads to destination.
        
        Args:
            leads: List of leads to write
        """
        pass
