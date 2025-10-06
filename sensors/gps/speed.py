from sensors.sensor import Sensor

class Speed(Sensor):
    def __init__(self, device):
        super().__init__(device, "gps_speed", "m/s", precision=2)

    def value(self):
        try:
            return super().value(self.device.report.hspeed)
        except:
            return None
