"""Lead source using Apollo.io API."""

import os
import asyncio
from typing import Dict, Any, List
import aiohttp
from leads.base import LeadSource


class ApolloLeadSource(LeadSource):
    """Scrape leads using Apollo.io API."""
    
    BASE_URL = "https://api.apollo.io/v1"
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Apollo lead source.
        
        Args:
            config: Configuration containing Apollo API key
        """
        super().__init__(config)
        self.api_key = os.getenv("APOLLO_API_KEY")
        
        if not self.api_key:
            raise ValueError("APOLLO_API_KEY environment variable not set")
    
    async def search(
        self,
        business_type: str,
        location: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Search for leads using Apollo.io.
        
        Args:
            business_type: Type of business
            location: Location to search
            limit: Max results
            
        Returns:
            List of leads
        """
        try:
            async with aiohttp.ClientSession() as session:
                leads = await self._search_companies(session, business_type, location, limit)
                return self._format_leads(leads)
        except Exception as e:
            raise RuntimeError(f"Apollo.io search failed: {e}")
    
    async def _search_companies(
        self,
        session: aiohttp.ClientSession,
        business_type: str,
        location: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Search for companies on Apollo.io.
        
        Args:
            session: aiohttp session
            business_type: Business type
            location: Location
            limit: Max results
            
        Returns:
            Raw company data
        """
        url = f"{self.BASE_URL}/organizations/search"
        
        headers = {
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
        }
        
        payload = {
            "q_organization_industry": business_type,
            "organization_locations": [location],
            "per_page": min(limit, 100),
        }
        
        results = []
        page = 1
        
        while len(results) < limit:
            payload["page"] = page
            
            async with session.post(
                url,
                json=payload,
                headers=headers,
                params={"api_key": self.api_key}
            ) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"Apollo.io search failed: {resp.status}")
                
                data = await resp.json()
                organizations = data.get("organizations", [])
                
                if not organizations:
                    break
                
                results.extend(organizations)
                page += 1
                
                if len(organizations) < payload["per_page"]:
                    break
        
        return results[:limit]
    
    @staticmethod
    def _format_leads(raw_leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format Apollo.io results to standard format.
        
        Args:
            raw_leads: Raw Apollo.io results
            
        Returns:
            Standardized leads
        """
        formatted = []
        for lead in raw_leads:
            formatted.append({
                "business_name": lead.get("name"),
                "phone_number": lead.get("phone_number"),
                "email": lead.get("email"),
                "website": lead.get("website_url"),
                "address": lead.get("street_address"),
                "city": lead.get("city"),
                "state": lead.get("state"),
                "zip_code": lead.get("postal_code"),
                "source": "apollo",
            })
        return formatted
