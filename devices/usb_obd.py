###
# Useful OBD-II commands:
# ETHANOL_PERCENT   - not supported on this vehicle (no dedicated flex-fuel sensor)
# FUEL_LEVEL        - not supported on this vehicle
# FUEL_RATE         - not supported on this vehicle
# SPEED
# COOLANT_TEMP
# RPM
# THROTTLE_POS
# ENGINE_LOAD
# INTAKE_PRESSURE
# TIMING_ADVANCE
# INTAKE_TEMP


from devices.device import Device
from obd import OBD
from sensors.obd.speed import Speed
from sensors.obd.rpm import RPM
from sensors.obd.coolant_temp import CoolantTemp
from sensors.obd.engine_load import EngineLoad
from sensors.obd.intake_manifold_pressure import IntakeManifoldPressure
from sensors.obd.throttle_position import ThrottlePosition
from sensors.obd.timing_advance import TimingAdvance
from sensors.obd.intake_air_temp import IntakeAirTemp
from sensors.obd.battery_voltage import BatteryVoltage


class USBOBD(Device):
    def __init__(self, port):
        super().__init__("OBD")
        self.obd = OBD(port, fast=False)
        self.sensors = [
            Speed(self),
            RPM(self),
            CoolantTemp(self),
            EngineLoad(self),
            IntakeManifoldPressure(self),
            ThrottlePosition(self),
            TimingAdvance(self),
            IntakeAirTemp(self),
            BatteryVoltage(self),
        ]

    def close(self):
        self.obd.close()

    def is_connected(self):
        return self.obd.is_connected()

    def supported_commands(self):
        return self.obd.supported_commands

    def query(self, cmd):
        response = self.obd.query(cmd)
        if not response.is_null():
            try:
                return float(response.value.magnitude)
            except:
                return None