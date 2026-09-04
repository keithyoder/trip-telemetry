from sensors.sensor import Sensor
from dash_daq import LEDDisplay
import adafruit_ltr390

RESOLUTION_BITS = {
    adafruit_ltr390.Resolution.RESOLUTION_13BIT: 13,
    adafruit_ltr390.Resolution.RESOLUTION_16BIT: 16,
    adafruit_ltr390.Resolution.RESOLUTION_17BIT: 17,
    adafruit_ltr390.Resolution.RESOLUTION_18BIT: 18,
    adafruit_ltr390.Resolution.RESOLUTION_19BIT: 19,
    adafruit_ltr390.Resolution.RESOLUTION_20BIT: 20,
}

class UVIndex(Sensor):
    def __init__(self, device):
        super().__init__(device, "ltr390_uv_index", "raw")

    def value(self):
        try:
            raw = self.device.uvs
            bits = RESOLUTION_BITS.get(self.device.resolution, 20)
            max_raw = (2 ** bits) - 1
            return None if raw >= max_raw else super().value(self.device.uvi)
        except:
            return None
        
    def dashboard_gauge(self):
        return LEDDisplay(
            id=self.key,
            label="UV Index",
            value=26.5
        )