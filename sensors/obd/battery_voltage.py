from sensors.sensor import Sensor
from dash_daq import LEDDisplay
from obd import commands


class BatteryVoltage(Sensor):
    """
    Reads voltage as measured by the ELM327 adapter itself on pin 16 of the
    OBD-II connector (commands.ELM_VOLTAGE) -- this is NOT a PID the car's
    ECU answers, it's the adapter's own voltmeter. Meaning differs by
    ignition state:
      - engine off:     battery resting voltage (~12.6V healthy)
      - engine running: alternator charging voltage (~13.5-14.5V healthy)
    """

    def __init__(self, device):
        super().__init__(device, "obd_battery_voltage", "V", precision=2)
        self.cmd = commands.ELM_VOLTAGE
        self.min = 10
        self.max = 16

    def value(self):
        try:
            return super().value(self.device.query(self.cmd))
        except:
            return None

    def dashboard_gauge(self):
        return LEDDisplay(
            id=self.key,
            label="Battery Voltage (V)",
            value=0
        )