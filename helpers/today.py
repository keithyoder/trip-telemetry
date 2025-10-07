from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class Today:
    @staticmethod
    def start():
        now = datetime.now()
        local_tz = now.astimezone().tzinfo
        local_midnight = datetime.now(local_tz).replace(hour=0, minute=0, second=0, microsecond=0)
        return local_midnight.astimezone(ZoneInfo("UTC"))
    
    def tomorrow_start(self):
        local_midnight = datetime.now(self.local_tz).replace(hour=0, minute=0, second=0, microsecond=0)
        return (local_midnight + timedelta(days=1)).astimezone(ZoneInfo("UTC"))


    @staticmethod
    def end():
        now = datetime.now()
        local_tz = now.astimezone().tzinfo
        local_midnight = datetime.now(local_tz).replace(hour=0, minute=0, second=0, microsecond=0)
        return (local_midnight + timedelta(days=1)).astimezone(ZoneInfo("UTC"))
