class Sensor:
    def __init__(self, device, key, unit, precision=2):
        self.device = device
        self.key = key
        self.unit = unit
        self.precision = precision
        
    def value(self, value):
        return round(value, self.precision)
