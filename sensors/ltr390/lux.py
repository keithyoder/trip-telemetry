from dash_daq import LEDDisplay

class Lux:
    def __init__(self, device):
        super().__init__(self, device, "ltr390_lux", "lumens")

    def value(self):
        try:
            return super().value(self.device.lux)
        except:
            return None

    def dashboard_gauge(self):
        return LEDDisplay(
            id=self.key,
            label="Lux (lumens)",
            value=26.5
        )