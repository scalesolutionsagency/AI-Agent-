"""Time formatting utilities."""

from typing import Dict, Any


class TimeFormatter:
    """Format time data for display."""
    
    @staticmethod
    def format_time(hour: int, minute: int, second: int, format_24: bool = True) -> str:
        """Format time as string.
        
        Args:
            hour: Hour value
            minute: Minute value
            second: Second value
            format_24: True for 24-hour, False for 12-hour
            
        Returns:
            Formatted time string
        """
        if format_24:
            return f"{hour:02d}:{minute:02d}:{second:02d}"
        else:
            period = "AM" if hour < 12 else "PM"
            hour_12 = hour % 12
            if hour_12 == 0:
                hour_12 = 12
            return f"{hour_12:02d}:{minute:02d}:{second:02d} {period}"
    
    @staticmethod
    def format_time_without_seconds(hour: int, minute: int, format_24: bool = True) -> str:
        """Format time without seconds.
        
        Args:
            hour: Hour value
            minute: Minute value
            format_24: True for 24-hour, False for 12-hour
            
        Returns:
            Formatted time string
        """
        if format_24:
            return f"{hour:02d}:{minute:02d}"
        else:
            period = "AM" if hour < 12 else "PM"
            hour_12 = hour % 12
            if hour_12 == 0:
                hour_12 = 12
            return f"{hour_12:02d}:{minute:02d} {period}"
    
    @staticmethod
    def format_full_info(data: Dict[str, Any], format_24: bool = True, show_seconds: bool = True) -> Dict[str, str]:
        """Format complete time info for display.
        
        Args:
            data: Time data dictionary
            format_24: True for 24-hour format
            show_seconds: Whether to include seconds
            
        Returns:
            Formatted display dictionary
        """
        if "error" in data:
            return {
                "timezone": data["timezone"],
                "time": "ERROR",
                "date": "Unknown",
                "error": data["error"]
            }
        
        if show_seconds:
            time_str = TimeFormatter.format_time(
                data["hour"],
                data["minute"],
                data["second"],
                format_24
            )
        else:
            time_str = TimeFormatter.format_time_without_seconds(
                data["hour"],
                data["minute"],
                format_24
            )
        
        return {
            "timezone": data["timezone"],
            "time": time_str,
            "date": data["date"],
            "day": data["day_of_week"],
            "offset": data["utc_offset"],
            "dst": "DST" if data["is_dst"] else "STD"
        }
