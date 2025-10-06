from sensors.sensor import Sensor
from dash import dcc

class Temperature(Sensor):
    def __init__(self, device):
        super().__init__(device, "shtc3_temperature", "C")
        self.description = "Temperature"
        self.min = 0
        self.max = 40

    def value(self):
        try:
            temperature, _ = self.device.measurements
            return super().value(temperature)
        except:
            return None

    def figure(self, current, daily_range):
        return super().current_max_min(current, daily_range)

    def dashboard_gauge(self):
        return dcc.Graph(
            id=self.key
        )
        # return GraduatedBar(
        #     id=self.key,
        #     color={"gradient":True,"ranges":{"blue":[0,15],"yellow":[15,30],"red":[30,40]}},
        #     showCurrentValue=True,
        #     step=0.5,
        #     max=40,
        #     value=25
        # )