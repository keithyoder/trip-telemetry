from sensors.sensor import Sensor
from dash_daq import LEDDisplay
from obd import commands


class CoolantTemp(Sensor):
    def __init__(self, device):
        super().__init__(device, "obd_coolant_temp", "\u00b0C", precision=1)
        self.cmd = commands.COOLANT_TEMP
        self.min = -20
        self.max = 130

    def value(self):
        try:
            return super().value(self.device.query(self.cmd))
        except:
            return None

    def dashboard_gauge(self):
        return LEDDisplay(
            id=self.key,
            label="Coolant Temp (\u00b0C)",
            value=0
        )