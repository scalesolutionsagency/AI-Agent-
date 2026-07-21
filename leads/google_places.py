"""Lead source using Google Places API."""

import os
import asyncio
from typing import Dict, Any, List
import aiohttp
from leads.base import LeadSource


class GooglePlacesSource(LeadSource):
    """Scrape leads using Google Places API."""
    
    BASE_URL = "https://maps.googleapis.com/maps/api"
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Google Places lead source.
        
        Args:
            config: Configuration containing Google Places API key
        """
        super().__init__(config)
        self.api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        
        if not self.api_key:
            raise ValueError("GOOGLE_PLACES_API_KEY environment variable not set")
    
    async def search(
        self,
        business_type: str,
        location: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Search for leads using Google Places.
        
        Args:
            business_type: Type of business
            location: Location to search
            limit: Max results
            
        Returns:
            List of leads
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Note: This is a simplified implementation
                # Google Places API requires geocoding first, then search
                leads = await self._search_places(session, business_type, location, limit)
                return self._format_leads(leads)
        except Exception as e:
            raise RuntimeError(f"Google Places search failed: {e}")
    
    async def _search_places(
        self,
        session: aiohttp.ClientSession,
        business_type: str,
        location: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Search for places on Google Places API.
        
        Args:
            session: aiohttp session
            business_type: Business type (used as search query)
            location: Location
            limit: Max results
            
        Returns:
            Raw place data
        """
        # First, geocode the location
        geocode_url = f"{self.BASE_URL}/geocode/json"
        geocode_params = {
            "address": location,
            "key": self.api_key,
        }
        
        async with session.get(geocode_url, params=geocode_params) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Geocoding failed: {resp.status}")
            
            geo_data = await resp.json()
            if not geo_data.get("results"):
                return []
            
            location_data = geo_data["results"][0]["geometry"]["location"]
            lat, lng = location_data["lat"], location_data["lng"]
        
        # Search nearby places
        nearby_url = f"{self.BASE_URL}/place/nearbysearch/json"
        search_params = {
            "location": f"{lat},{lng}",
            "radius": self.config.get("google_places", {}).get("radius", 50000),
            "keyword": business_type,
            "key": self.api_key,
        }
        
        results = []
        
        async with session.get(nearby_url, params=search_params) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Place search failed: {resp.status}")
            
            data = await resp.json()
            results.extend(data.get("results", []))
            
            # Handle pagination
            while data.get("next_page_token") and len(results) < limit:
                await asyncio.sleep(2)  # API requires delay between requests
                search_params["pagetoken"] = data["next_page_token"]
                
                async with session.get(nearby_url, params=search_params) as page_resp:
                    if page_resp.status != 200:
                        break
                    
                    data = await page_resp.json()
                    results.extend(data.get("results", []))
        
        return results[:limit]
    
    async def _get_place_details(
        self,
        session: aiohttp.ClientSession,
        place_id: str
    ) -> Dict[str, Any]:
        """Get detailed place information.
        
        Args:
            session: aiohttp session
            place_id: Place ID
            
        Returns:
            Place details
        """
        url = f"{self.BASE_URL}/place/details/json"
        params = {
            "place_id": place_id,
            "fields": "name,formatted_phone_number,website,formatted_address,opening_hours",
            "key": self.api_key,
        }
        
        async with session.get(url, params=params) as resp:
            if resp.status != 200:
                return {}
            
            data = await resp.json()
            return data.get("result", {})
    
    @staticmethod
    def _format_leads(raw_leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format Google Places results to standard format.
        
        Args:
            raw_leads: Raw Google Places results
            
        Returns:
            Standardized leads
        """
        formatted = []
        for lead in raw_leads:
            formatted.append({
                "business_name": lead.get("name"),
                "phone_number": lead.get("formatted_phone_number"),
                "email": None,  # Google Places doesn't provide email
                "website": lead.get("website"),
                "address": lead.get("vicinity") or lead.get("formatted_address"),
                "city": None,
                "state": None,
                "zip_code": None,
                "source": "google_places",
            })
        return formatted
