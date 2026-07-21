#!/usr/bin/env python3
"""CLI interface for digital clock."""

import click
import time
import os
import sys
from typing import List
import yaml
from pathlib import Path
from tabulate import tabulate
from colorama import Fore, Style, init

from clock.time_manager import TimeManager
from clock.formatter import TimeFormatter

# Initialize colorama
init(autoreset=True)


class DigitalClockCLI:
    """CLI for digital clock."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize CLI.
        
        Args:
            config_path: Path to config file
        """
        self.config = self._load_config(config_path)
        self.time_manager = TimeManager()
        self.formatter = TimeFormatter()
    
    @staticmethod
    def _load_config(config_path: str) -> dict:
        """Load configuration.
        
        Args:
            config_path: Path to config file
            
        Returns:
            Configuration dictionary
        """
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def display_clocks(self, zones: List[str], format_24: bool = True, show_seconds: bool = True):
        """Display clocks for multiple time zones.
        
        Args:
            zones: List of time zones
            format_24: Use 24-hour format
            show_seconds: Show seconds
        """
        update_interval = self.config.get("cli", {}).get("update_interval", 1)
        clear_screen = self.config.get("cli", {}).get("clear_screen", True)
        
        try:
            while True:
                if clear_screen:
                    os.system('clear' if os.name == 'posix' else 'cls')
                
                print(f"{Fore.CYAN}{Style.BRIGHT}{'═' * 80}")
                print(f"{Fore.CYAN}{Style.BRIGHT}Digital Clock - Multi-Timezone Display")
                print(f"{Fore.CYAN}{Style.BRIGHT}{'═' * 80}{Style.RESET_ALL}\n")
                
                # Get time in all zones
                times = self.time_manager.get_time_in_zones(zones)
                
                # Format for display
                table_data = []
                for time_data in times:
                    formatted = self.formatter.format_full_info(
                        time_data,
                        format_24=format_24,
                        show_seconds=show_seconds
                    )
                    
                    if "error" not in formatted:
                        table_data.append([
                            f"{Fore.GREEN}{formatted['timezone']}{Style.RESET_ALL}",
                            f"{Fore.YELLOW}{Style.BRIGHT}{formatted['time']}{Style.RESET_ALL}",
                            formatted['date'],
                            formatted['day'],
                            formatted['offset'],
                            formatted['dst']
                        ])
                    else:
                        table_data.append([
                            f"{Fore.RED}{formatted['timezone']}{Style.RESET_ALL}",
                            f"{Fore.RED}{formatted['error']}{Style.RESET_ALL}",
                            "-", "-", "-", "-"
                        ])
                
                # Display table
                headers = ["Timezone", "Time", "Date", "Day", "UTC Offset", "DST"]
                print(tabulate(
                    table_data,
                    headers=headers,
                    tablefmt="fancy_grid",
                    disable_numparse=True
                ))
                
                print(f"\n{Fore.CYAN}Press Ctrl+C to exit{Style.RESET_ALL}")
                time.sleep(update_interval)
        
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Clock stopped.{Style.RESET_ALL}")
            sys.exit(0)
    
    def list_timezones(self):
        """List all available time zones."""
        zones = self.time_manager.get_available_zones()
        print(f"{Fore.CYAN}Available Time Zones ({len(zones)} total):{Style.RESET_ALL}\n")
        
        # Display in columns
        for i in range(0, len(zones), 3):
            row = zones[i:i+3]
            print("  ".join(f"{zone:30}" for zone in row))


@click.command()
@click.option(
    '--zones',
    multiple=True,
    default=None,
    help='Time zones to display (e.g. "US/Eastern" "Europe/London")'
)
@click.option(
    '--format',
    type=click.Choice(['12', '24'], case_sensitive=False),
    default='24',
    help='Time format (12 or 24 hour)'
)
@click.option(
    '--no-seconds',
    is_flag=True,
    help='Hide seconds in display'
)
@click.option(
    '--list',
    'list_zones',
    is_flag=True,
    help='List all available time zones'
)
def main(zones: tuple, format: str, no_seconds: bool, list_zones: bool):
    """Digital Clock - Display time in multiple time zones."""
    
    cli = DigitalClockCLI()
    
    if list_zones:
        cli.list_timezones()
        return
    
    # Use provided zones or defaults from config
    if zones:
        zones_list = list(zones)
    else:
        zones_list = cli.config.get("time_zones", [
            "UTC",
            "US/Eastern",
            "US/Pacific",
            "Europe/London",
            "Europe/Paris",
            "Asia/Tokyo",
            "Asia/Shanghai",
            "Australia/Sydney"
        ])
    
    # Validate zones
    valid_zones = []
    for zone in zones_list:
        if cli.time_manager.validate_timezone(zone):
            valid_zones.append(zone)
        else:
            click.echo(f"{Fore.RED}Warning: Invalid timezone '{zone}' - skipping{Style.RESET_ALL}")
    
    if not valid_zones:
        click.echo(f"{Fore.RED}Error: No valid time zones specified{Style.RESET_ALL}")
        sys.exit(1)
    
    format_24 = format == '24'
    show_seconds = not no_seconds
    
    cli.display_clocks(valid_zones, format_24=format_24, show_seconds=show_seconds)


if __name__ == '__main__':
    main()
