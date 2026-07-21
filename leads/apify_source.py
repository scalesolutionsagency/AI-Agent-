"""Lead source using Apify Google Maps scraper."""

import os
import asyncio
from typing import Dict, Any, List
import aiohttp
from leads.base import LeadSource


class ApifyLeadSource(LeadSource):
    """Scrape leads using Apify's Google Maps scraper."""
    
    BASE_URL = "https://api.apify.com/v2/acts/{actor_id}/runs"
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Apify lead source.
        
        Args:
            config: Configuration containing Apify API token and actor ID
        """
        super().__init__(config)
        self.api_token = os.getenv("APIFY_API_TOKEN")
        self.actor_id = config.get("apify", {}).get(
            "actor_id",
            "apify/google-maps-scraper"
        )
        
        if not self.api_token:
            raise ValueError("APIFY_API_TOKEN environment variable not set")
    
    async def search(
        self,
        business_type: str,
        location: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Search for leads using Apify.
        
        Args:
            business_type: Type of business
            location: Location to search
            limit: Max results
            
        Returns:
            List of leads
        """
        query = f"{business_type} in {location}"
        
        payload = {
            "startUrls": [{"url": "https://www.google.com/maps"}],
            "searchStringsArray": [query],
            "maxPostsPerSearch": limit,
            "language": "en",
            "includeWebsites": True,
            "includePhoneNumbers": True,
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # Start run
                run_id = await self._start_run(session, payload)
                
                # Wait for completion and get results
                leads = await self._get_results(session, run_id)
                
                return self._format_leads(leads)
        except Exception as e:
            raise RuntimeError(f"Apify search failed: {e}")
    
    async def _start_run(
        self,
        session: aiohttp.ClientSession,
        payload: Dict[str, Any]
    ) -> str:
        """Start an Apify actor run.
        
        Args:
            session: aiohttp session
            payload: Actor input
            
        Returns:
            Run ID
        """
        url = self.BASE_URL.format(actor_id=self.actor_id)
        
        async with session.post(
            url,
            json=payload,
            auth=aiohttp.BasicAuth("user", self.api_token)
        ) as resp:
            if resp.status != 201:
                raise RuntimeError(f"Failed to start Apify run: {resp.status}")
            data = await resp.json()
            return data["data"]["id"]
    
    async def _get_results(
        self,
        session: aiohttp.ClientSession,
        run_id: str
    ) -> List[Dict[str, Any]]:
        """Get results from a completed run.
        
        Args:
            session: aiohttp session
            run_id: Run ID
            
        Returns:
            List of results
        """
        url = f"https://api.apify.com/v2/acts/{self.actor_id}/runs/{run_id}/dataset/items"
        max_retries = 60
        retry_count = 0
        
        while retry_count < max_retries:
            async with session.get(
                url,
                auth=aiohttp.BasicAuth("user", self.api_token)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data if isinstance(data, list) else []
                elif resp.status == 202:
                    # Still running
                    await asyncio.sleep(5)
                    retry_count += 1
                else:
                    raise RuntimeError(f"Failed to get results: {resp.status}")
        
        raise RuntimeError("Apify run timeout")
    
    @staticmethod
    def _format_leads(raw_leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format Apify results to standard lead format.
        
        Args:
            raw_leads: Raw Apify results
            
        Returns:
            Standardized leads
        """
        formatted = []
        for lead in raw_leads:
            formatted.append({
                "business_name": lead.get("title") or lead.get("name"),
                "phone_number": lead.get("phoneNumber"),
                "email": lead.get("email"),
                "website": lead.get("website") or lead.get("url"),
                "address": lead.get("address"),
                "city": lead.get("city"),
                "state": lead.get("state"),
                "zip_code": lead.get("zipCode") or lead.get("postalCode"),
                "source": "apify",
            })
        return formatted
