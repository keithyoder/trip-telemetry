import gpsd
from devices.device import Device
from sensors.gps.latitude import Latitude
from sensors.gps.longitude import Longitude
from sensors.gps.altitude import Altitude
from sensors.gps.speed import Speed
from sensors.gps.time import Time
from sensors.gps.climb import Climb
from sensors.gps.satellites import Satellites
from sensors.gps.heading import Heading
from helpers.solar_position import SolarPosition

class GPS(Device):
    def __init__(self):
        super().__init__("GPS")
        try:
            gpsd.connect()
            self.connected = True
        except:
            self.connected = False
        self.values = {}
        self.report = None
        self.device = None
        self.sensors = [
            Time(self),
            Latitude(self),
            Longitude(self),
            Altitude(self),
            Speed(self),
            Climb(self),
            Satellites(self),
            Heading(self)
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
        return self.connected