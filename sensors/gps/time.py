from sensors.sensor import Sensor
from datetime import datetime

class Time(Sensor):
    def __init__(self, device):
        super().__init__(device, "gps_timestamp", "timestamp", precision=-1)

    def value(self):
        try:
            return super().value(datetime.fromisoformat(self.device.report.time))
        except:
            return None
