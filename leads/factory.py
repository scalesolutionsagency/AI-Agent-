"""Factory for creating lead source instances."""

from typing import Dict, Any
from leads.base import LeadSource
from leads.apify_source import ApifyLeadSource
from leads.apollo_source import ApolloLeadSource
from leads.google_places import GooglePlacesSource


class LeadSourceFactory:
    """Factory for instantiating lead sources."""
    
    _sources = {
        "apify": ApifyLeadSource,
        "apollo": ApolloLeadSource,
        "google_places": GooglePlacesSource,
    }
    
    @classmethod
    def create(cls, provider: str, config: Dict[str, Any]) -> LeadSource:
        """Create a lead source instance.
        
        Args:
            provider: Name of the provider (apify, apollo, google_places)
            config: Source configuration
            
        Returns:
            Configured lead source instance
            
        Raises:
            ValueError: If provider is not supported
        """
        if provider not in cls._sources:
            raise ValueError(
                f"Unknown lead source: {provider}. "
                f"Supported: {list(cls._sources.keys())}"
            )
        
        source_class = cls._sources[provider]
        return source_class(config)
    
    @classmethod
    def register(cls, name: str, source_class: type) -> None:
        """Register a new lead source.
        
        Args:
            name: Provider name
            source_class: LeadSource subclass
        """
        cls._sources[name] = source_class
