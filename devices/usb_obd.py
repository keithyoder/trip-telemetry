###
# Useful OBD-II commands:
# ETHANOL_PERCENT
# FUEL_LEVEL
# SPEED
# COOLANT_TEMP
# RPM
# THROTTLE_POS
# ENGINE_LOAD


from devices.device import Device
from obd import OBD
from sensors.obd.speed import Speed

class USBOBD(Device):
    def __init__(self, port):
        super().__init__("OBD")
        self.obd = OBD(port, fast=False)
        self.sensors = [
            Speed(self)
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
