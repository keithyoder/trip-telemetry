from sensors.sensor import Sensor

class Latitude(Sensor):
    def __init__(self, device):
        super().__init__(device, "gps_latitude", "degrees", precision=5)

    def value(self):
        try:
            return super().value(self.device.report.lat)
        except:
            return None
