from sensors.sensor import Sensor

class Climb(Sensor):
    def __init__(self, device):
        super().__init__(device, "gps_climb", "m/s", precision=2)

    def value(self):
        try:
            return super().value(self.device.report.climb)
        except:
            return None
