from sensors.sensor import Sensor

class Longitude(Sensor):
    def __init__(self, device):
        super().__init__(device, "gps_longitude", "degrees", precision=5)

    def value(self):
        try:
            return super().value(self.device.report.lon)
        except:
            return None
