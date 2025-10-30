from sensors.sensor import Sensor

class Heading(Sensor):
    def __init__(self, device):
        super().__init__(device, "gps_heading", "degrees", precision=1)

    def value(self):
        try:
            return super().value(self.device.report.track)
        except:
            return None
