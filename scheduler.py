"""Scheduler module for Lead Scraper Agent."""

import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import asyncio
from main import LeadScraperAgent


logger = logging.getLogger(__name__)


class LeadScraperScheduler:
    """Schedule periodic lead scraping."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize scheduler.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.scheduler = BackgroundScheduler()
    
    def start(self, config: dict) -> None:
        """Start the scheduler.
        
        Args:
            config: Scheduler configuration
        """
        scheduler_config = config.get("scheduler", {})
        
        if not scheduler_config.get("enabled", True):
            logger.info("Scheduler is disabled")
            return
        
        frequency = scheduler_config.get("frequency", "daily")
        time_str = scheduler_config.get("time", "09:00")
        timezone = scheduler_config.get("timezone", "UTC")
        
        # Parse time
        hour, minute = map(int, time_str.split(":"))
        
        # Create trigger based on frequency
        if frequency == "hourly":
            trigger = CronTrigger(minute=minute, timezone=timezone)
        elif frequency == "daily":
            trigger = CronTrigger(hour=hour, minute=minute, timezone=timezone)
        elif frequency == "weekly":
            trigger = CronTrigger(
                day_of_week="mon",
                hour=hour,
                minute=minute,
                timezone=timezone
            )
        elif frequency == "monthly":
            trigger = CronTrigger(
                day=1,
                hour=hour,
                minute=minute,
                timezone=timezone
            )
        else:
            raise ValueError(f"Unknown frequency: {frequency}")
        
        # Add job
        self.scheduler.add_job(
            self._run_scraper,
            trigger=trigger,
            name="lead_scraper",
            replace_existing=True
        )
        
        logger.info(
            f"Scheduler started: {frequency} at {time_str} {timezone}"
        )
        self.scheduler.start()
    
    def _run_scraper(self) -> None:
        """Run the lead scraper."""
        try:
            agent = LeadScraperAgent(self.config_path)
            asyncio.run(agent.run())
        except Exception as e:
            logger.error(f"Scheduled scraper failed: {e}", exc_info=True)
    
    def stop(self) -> None:
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")


if __name__ == "__main__":
    from utils.config_loader import ConfigLoader
    from utils.logger import setup_logger
    
    # Setup logging
    setup_logger("LeadScraperScheduler")
    
    # Load config
    config = ConfigLoader.load("config.yaml")
    
    # Start scheduler
    scheduler = LeadScraperScheduler()
    scheduler.start(config)
    
    # Keep running
    try:
        while True:
            pass
    except KeyboardInterrupt:
        scheduler.stop()
