from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class Today:
    """Utility class for getting day boundaries in UTC"""
    
    @staticmethod
    def _get_local_midnight(offset_days: int = 0) -> datetime:
        """
        Get local midnight with optional day offset, converted to UTC
        
        Parameters:
        - offset_days: Number of days to offset (0=today, 1=tomorrow, -1=yesterday)
        
        Returns:
        - datetime object in UTC timezone
        """
        # Get current time in local timezone (more efficient than two calls)
        now_local = datetime.now().astimezone()
        
        # Get midnight of the target day
        local_midnight = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Apply offset if needed
        if offset_days != 0:
            local_midnight += timedelta(days=offset_days)
        
        # Convert to UTC
        return local_midnight.astimezone(ZoneInfo("UTC"))
    
    @staticmethod
    def start() -> datetime:
        """Get start of today (00:00:00) in UTC"""
        return Today._get_local_midnight(0)
    
    @staticmethod
    def end() -> datetime:
        """Get end of today (tomorrow's 00:00:00) in UTC"""
        return Today._get_local_midnight(1)
    
    @staticmethod
    def tomorrow_start() -> datetime:
        """Get start of tomorrow (00:00:00) in UTC"""
        return Today._get_local_midnight(1)
    
    @staticmethod
    def yesterday_start() -> datetime:
        """Get start of yesterday (00:00:00) in UTC"""
        return Today._get_local_midnight(-1)
    
    @staticmethod
    def yesterday_end() -> datetime:
        """Get end of yesterday (today's 00:00:00) in UTC"""
        return Today._get_local_midnight(0)
    
    @staticmethod
    def get_day_range(offset_days: int = 0) -> tuple[datetime, datetime]:
        """
        Get start and end of a day as a tuple
        
        Parameters:
        - offset_days: Number of days to offset (0=today, 1=tomorrow, -1=yesterday)
        
        Returns:
        - Tuple of (start, end) datetime objects in UTC
        """
        start = Today._get_local_midnight(offset_days)
        end = Today._get_local_midnight(offset_days + 1)
        return (start, end)
    
    @staticmethod
    def today_range() -> tuple[datetime, datetime]:
        """Get (start, end) tuple for today"""
        return Today.get_day_range(0)
    
    @staticmethod
    def yesterday_range() -> tuple[datetime, datetime]:
        """Get (start, end) tuple for yesterday"""
        return Today.get_day_range(-1)
    
    @staticmethod
    def tomorrow_range() -> tuple[datetime, datetime]:
        """Get (start, end) tuple for tomorrow"""
        return Today.get_day_range(1)