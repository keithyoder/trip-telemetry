from sensors.sensor import Sensor
from dash_daq import LEDDisplay
from obd import commands


class IntakeManifoldPressure(Sensor):
    def __init__(self, device):
        super().__init__(device, "obd_intake_manifold_pressure", "kPa", precision=1)
        self.cmd = commands.INTAKE_PRESSURE
        self.min = 0
        self.max = 255

    def value(self):
        try:
            return super().value(self.device.query(self.cmd))
        except:
            return None

    def dashboard_gauge(self):
        return LEDDisplay(
            id=self.key,
            label="Intake Manifold Pressure (kPa)",
            value=0
        )