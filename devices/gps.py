import gpsd
from devices.device import Device
from sensors.gps.latitude import Latitude
from sensors.gps.longitude import Longitude
from sensors.gps.altitude import Altitude
from sensors.gps.speed import Speed

class GPS(Device):
    def __init__(self):
        super().__init__("GPS")
        gpsd.connect()
        self.values = {}
        self.report = None
        self.device = None
        self.sensors = [
            Latitude(self.device),
            Longitude(self.device),
            Altitude(self.device),
            Speed(self.device)
        ]

    def read(self):
        self.report = gpsd.get_current()
        super().read()

    def is_connected(self):
        return True