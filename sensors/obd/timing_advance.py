from sensors.sensor import Sensor
from dash_daq import LEDDisplay
from obd import commands


class TimingAdvance(Sensor):
    def __init__(self, device):
        super().__init__(device, "obd_timing_advance", "\u00b0", precision=1)
        self.cmd = commands.TIMING_ADVANCE
        self.min = -20
        self.max = 60

    def value(self):
        try:
            return super().value(self.device.query(self.cmd))
        except:
            return None

    def dashboard_gauge(self):
        return LEDDisplay(
            id=self.key,
            label="Timing Advance (\u00b0)",
            value=0
        )