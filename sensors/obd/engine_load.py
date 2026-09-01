from sensors.sensor import Sensor
from dash_daq import LEDDisplay
from obd import commands


class EngineLoad(Sensor):
    def __init__(self, device):
        super().__init__(device, "obd_engine_load", "%", precision=1)
        self.cmd = commands.ENGINE_LOAD
        self.min = 0
        self.max = 100

    def value(self):
        try:
            return super().value(self.device.query(self.cmd))
        except:
            return None

    def dashboard_gauge(self):
        return LEDDisplay(
            id=self.key,
            label="Engine Load (%)",
            value=0
        )