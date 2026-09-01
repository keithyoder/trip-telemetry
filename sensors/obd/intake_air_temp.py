from sensors.sensor import Sensor
from dash_daq import LEDDisplay
from obd import commands


class IntakeAirTemp(Sensor):
    def __init__(self, device):
        super().__init__(device, "obd_intake_air_temp", "\u00b0C", precision=1)
        self.cmd = commands.INTAKE_TEMP
        self.min = -20
        self.max = 80

    def value(self):
        try:
            return super().value(self.device.query(self.cmd))
        except:
            return None

    def dashboard_gauge(self):
        return LEDDisplay(
            id=self.key,
            label="Intake Air Temp (\u00b0C)",
            value=0
        )