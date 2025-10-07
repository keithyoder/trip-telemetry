import gpsd
from devices.device import Device
from sensors.gps.latitude import Latitude
from sensors.gps.longitude import Longitude
from sensors.gps.altitude import Altitude
from sensors.gps.speed import Speed
from solar_position import SolarPosition

class GPS(Device):
    def __init__(self):
        super().__init__("GPS")
        gpsd.connect()
        self.values = {}
        self.report = None
        self.device = None
        self.sensors = [
            Latitude(self),
            Longitude(self),
            Altitude(self),
            Speed(self)
        ]

    def read(self):
        self.report = gpsd.get_current()
        super().read()

    def solar_position(self):
        if not self.report:
            return None
        coords = {
            'latitude': self.report.lat,
            'longitude': self.report.lon
        }
        sp = SolarPosition(self.report.get_time(), coords, timezone="America/Recife")
        return sp
    
    def is_connected(self):
        return True