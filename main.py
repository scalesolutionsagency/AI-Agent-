#!/usr/bin/env python3
"""
Lead Scraper Agent - Main Entry Point

This module orchestrates the entire lead scraping workflow:
1. Loads configuration
2. Initializes the lead source
3. Executes searches
4. Deduplicates results
5. Cleans data
6. Pushes to output destinations
7. Logs results and errors
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from utils.config_loader import ConfigLoader
from utils.logger import setup_logger
from utils.data_cleaner import DataCleaner
from deduplication.deduplicator import LeadDeduplicator
from leads.factory import LeadSourceFactory
from outputs.factory import OutputFactory


class LeadScraperAgent:
    """Main agent coordinating the lead scraping workflow."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the lead scraper agent.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = ConfigLoader.load(config_path)
        self.logger = setup_logger(
            name="LeadScraperAgent",
            log_level=self.config.get("logging", {}).get("level", "INFO"),
            log_dir=self.config.get("logging", {}).get("file_path", "./logs")
        )
        
        self.logger.info("Lead Scraper Agent initialized")
        self.data_cleaner = DataCleaner(self.config.get("data_cleaning", {}))
        self.deduplicator = LeadDeduplicator(self.config.get("deduplication", {}))
        self.lead_source = None
        self.outputs = []
        
    def initialize_lead_source(self) -> None:
        """Initialize the configured lead source."""
        try:
            provider = self.config.get("lead_source", {}).get("provider", "apify")
            self.lead_source = LeadSourceFactory.create(
                provider,
                self.config.get("lead_source", {})
            )
            self.logger.info(f"Lead source '{provider}' initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize lead source: {e}")
            raise
    
    def initialize_outputs(self) -> None:
        """Initialize configured output handlers."""
        try:
            output_config = self.config.get("output", {})
            output_format = output_config.get("format", "json")
            
            if output_format in ["csv", "json", "both"]:
                self.outputs.extend(
                    OutputFactory.create_local_outputs(
                        output_format,
                        output_config
                    )
                )
            
            if output_config.get("google_sheets", {}).get("enabled"):
                self.outputs.append(
                    OutputFactory.create_google_sheets_output(output_config)
                )
            
            if output_config.get("notion", {}).get("enabled"):
                self.outputs.append(
                    OutputFactory.create_notion_output(output_config)
                )
            
            self.logger.info(f"Initialized {len(self.outputs)} output handler(s)")
        except Exception as e:
            self.logger.error(f"Failed to initialize outputs: {e}")
            raise
    
    async def scrape_leads(self) -> List[Dict[str, Any]]:
        """Execute lead scraping for all configured queries.
        
        Returns:
            List of deduplicated and cleaned leads
        """
        all_leads = []
        search_queries = self.config.get("search_queries", [])
        
        if not search_queries:
            self.logger.warning("No search queries configured")
            return all_leads
        
        for query in search_queries:
            try:
                self.logger.info(f"Scraping: {query['business_type']} in {query['location']}")
                leads = await self.lead_source.search(
                    business_type=query["business_type"],
                    location=query["location"],
                    limit=query.get("limit", 100)
                )
                self.logger.info(f"Found {len(leads)} leads")
                all_leads.extend(leads)
            except Exception as e:
                self.logger.error(f"Error scraping query {query}: {e}")
                if not self.config.get("error_handling", {}).get("continue_on_error", True):
                    raise
        
        return all_leads
    
    def process_leads(self, raw_leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process raw leads: clean and deduplicate.
        
        Args:
            raw_leads: Raw leads from scraper
            
        Returns:
            Processed and deduplicated leads
        """
        # Clean data
        self.logger.info(f"Cleaning {len(raw_leads)} leads...")
        cleaned_leads = [self.data_cleaner.clean(lead) for lead in raw_leads]
        
        # Deduplicate
        self.logger.info("Deduplicating leads...")
        processed_leads = self.deduplicator.deduplicate(cleaned_leads)
        
        self.logger.info(
            f"Processed leads: {len(cleaned_leads)} cleaned, "
            f"{len(processed_leads)} after deduplication"
        )
        
        return processed_leads
    
    async def push_leads(self, leads: List[Dict[str, Any]]) -> None:
        """Push processed leads to configured outputs.
        
        Args:
            leads: Processed leads to push
        """
        if not leads:
            self.logger.info("No leads to push")
            return
        
        for output in self.outputs:
            try:
                self.logger.info(f"Pushing {len(leads)} leads to {output.__class__.__name__}...")
                await output.write(leads)
                self.logger.info(f"Successfully pushed to {output.__class__.__name__}")
            except Exception as e:
                self.logger.error(
                    f"Failed to push leads to {output.__class__.__name__}: {e}"
                )
                if not self.config.get("error_handling", {}).get("continue_on_error", True):
                    raise
    
    async def run(self) -> None:
        """Execute the complete lead scraping workflow."""
        try:
            start_time = datetime.now()
            self.logger.info("=" * 60)
            self.logger.info(f"Lead Scraper Agent started at {start_time}")
            self.logger.info("=" * 60)
            
            # Initialize
            self.initialize_lead_source()
            self.initialize_outputs()
            
            # Scrape
            raw_leads = await self.scrape_leads()
            
            # Process
            processed_leads = self.process_leads(raw_leads)
            
            # Push
            await self.push_leads(processed_leads)
            
            # Log completion
            elapsed = datetime.now() - start_time
            self.logger.info("=" * 60)
            self.logger.info(
                f"Lead Scraper Agent completed successfully in {elapsed.total_seconds():.2f}s"
            )
            self.logger.info(f"Total leads processed: {len(processed_leads)}")
            self.logger.info("=" * 60)
            
        except Exception as e:
            self.logger.critical(f"Agent failed: {e}", exc_info=True)
            sys.exit(1)


async def main():
    """Entry point for the application."""
    agent = LeadScraperAgent()
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
