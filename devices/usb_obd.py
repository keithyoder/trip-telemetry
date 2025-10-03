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
from obd import OBD, commands

class USBOBD(Device):
    def __init__(self, port):
        super().__init__("OBD")
        self.obd = OBD(port, fast=False)
        self.commands = { "Speed": commands.SPEED }

    def close(self):
        self.obd.close()

    def is_connected(self):
        return self.obd.is_connected()
    
    def supported_commands(self):
        return self.obd.supported_commands

    def read(self):
        values = {}
        for name, cmd in self.commands.items():
            response = self.obd.query(cmd)
            if not response.is_null():
                try:
                    values[name] = float(response.value.magnitude)
                except:
                    values[name] = None
        self.lastest_values = values
