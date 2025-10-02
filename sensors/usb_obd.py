from sensors.sensor import Sensor
from obd import OBD, commands

class USBOBD(Sensor):
    COMMANDS = {
        "RPM": commands.RPM,
        "Throttle": commands.THROTTLE_POS,
        "Coolant Temp": commands.COOLANT_TEMP,
        "Engine Load": commands.ENGINE_LOAD,
        "Speed": commands.SPEED,
        "Fuel Level": commands.FUEL_LEVEL,
        "MAF": commands.MAF,
        "Fuel Rate": commands.FUEL_RATE  # may return None
    }

    def __init__(self, port):
        super().__init__("OBD")
        self.obd = OBD(port, fast=False)
        self.latest_values = {key: None for key in self.COMMANDS}

    def close(self):
        self.obd.close()

    def is_connected(self):
        return self.obd.is_connected()

    def read(self):
        for name, cmd in self.COMMANDS.items():
            response = self.obd.query(cmd)
            if not response.is_null():
                try:
                    self.latest_values[name] = float(response.value.magnitude)
                except:
                    self.latest_values[name] = None

    def read_values(self):
        # Implementation for reading values from USB OBD device
        pass
