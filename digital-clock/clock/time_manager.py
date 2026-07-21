"""Time zone and datetime management."""

import pytz
from datetime import datetime
from typing import Dict, List, Any


class TimeManager:
    """Manage time in multiple time zones."""
    
    def __init__(self):
        """Initialize time manager."""
        self.timezones = pytz.all_timezones
    
    def get_time_in_zones(self, zones: List[str]) -> List[Dict[str, Any]]:
        """Get current time in specified time zones.
        
        Args:
            zones: List of time zone names
            
        Returns:
            List of time data for each zone
        """
        results = []
        utc_time = datetime.now(pytz.UTC)
        
        for zone in zones:
            try:
                tz = pytz.timezone(zone)
                local_time = utc_time.astimezone(tz)
                
                results.append({
                    "timezone": zone,
                    "datetime": local_time,
                    "hour": local_time.hour,
                    "minute": local_time.minute,
                    "second": local_time.second,
                    "date": local_time.strftime("%Y-%m-%d"),
                    "day_of_week": local_time.strftime("%A"),
                    "utc_offset": self._format_offset(local_time),
                    "is_dst": bool(local_time.dst()),
                })
            except pytz.exceptions.UnknownTimeZoneError:
                results.append({
                    "timezone": zone,
                    "error": f"Unknown timezone: {zone}"
                })
        
        return results
    
    def format_time_12hour(self, hour: int, minute: int) -> tuple:
        """Convert 24-hour to 12-hour format.
        
        Args:
            hour: Hour in 24-hour format
            minute: Minute
            
        Returns:
            Tuple of (hour_12, minute, period)
        """
        period = "AM" if hour < 12 else "PM"
        hour_12 = hour % 12
        if hour_12 == 0:
            hour_12 = 12
        return hour_12, minute, period
    
    @staticmethod
    def _format_offset(dt: datetime) -> str:
        """Format UTC offset.
        
        Args:
            dt: Datetime object
            
        Returns:
            Formatted offset string
        """
        offset = dt.strftime("%z")
        if offset:
            return f"{offset[:3]}:{offset[3:]}"
        return "+00:00"
    
    @staticmethod
    def get_available_zones() -> List[str]:
        """Get list of all available time zones.
        
        Returns:
            List of time zone names
        """
        return pytz.all_timezones
    
    @staticmethod
    def validate_timezone(zone: str) -> bool:
        """Validate if timezone is valid.
        
        Args:
            zone: Timezone name
            
        Returns:
            True if valid, False otherwise
        """
        try:
            pytz.timezone(zone)
            return True
        except pytz.exceptions.UnknownTimeZoneError:
            return False
