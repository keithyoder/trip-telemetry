from sensors.sensor import Sensor

class Satellites(Sensor):
    def __init__(self, device):
        super().__init__(device, "gps_satellites", "count", precision=0)

    def value(self):
        try:
            return super().value(self.device.report.sats_valid)
        except:
            return None
