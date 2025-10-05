from sensors.sensor import Sensor

class Altitude(Sensor):
    def __init__(self, device):
        super().__init__(device, "gps_altitude", "meters", precision=0)

    def value(self):
        try:
            return super().value(self.device.report.alt)
        except:
            return None
