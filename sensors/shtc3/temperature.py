from sensors.sensor import Sensor
from dash import dcc
import plotly.graph_objects as go
from dash_daq import GraduatedBar

class Temperature(Sensor):
    def __init__(self, device):
        super().__init__(device, "shtc3_temperature", "C")

    def value(self):
        try:
            temperature, _ = self.device.measurements
            return super().value(temperature)
        except:
            return None

    def figure(self, min, max, current):
        base_gauge = go.Indicator(
                mode="gauge+number",
                value=current,
                title={"text": "Room Temperature (°C)"},
                gauge={
                    "axis": {"range": [0, 40]},
                    "bar": {"color": "black"},
                    "steps": [
                        {"range": [0, 10], "color": "#f8f9fa"},
                        {"range": [10, 20], "color": "#74b9ff"},
                        {"range": [20, 30], "color": "#ffeaa7"},
                        {"range": [30, 40], "color": "#d63031"},
                    ],
                    "threshold": {   # one threshold (current temp pointer)
                        "line": {"color": "black", "width": 4},
                        "thickness": 0.75,
                        "value": current
                    }
                }
            )

        # extra indicators with only threshold lines
        min_threshold = go.Indicator(
            mode="gauge",
            value=min,
            gauge={
                "axis": {"range": [0, 40], "visible": False},
                "bar": {"color": "rgba(0,0,0,0)"},
                "bgcolor": "rgba(0,0,0,0)",
                "steps": [],
                "threshold": {
                    "line": {"color": "green", "width": 4},
                    "thickness": 0.75,
                    "value": min
                }
            },
            domain={'x': [0, 1], 'y': [0, 1]}  # overlay exactly
        )

        max_threshold = go.Indicator(
            mode="gauge",
            value=max,
            gauge={
                "axis": {"range": [0, 40], "visible": False},
                "bar": {"color": "rgba(0,0,0,0)"},
                "bgcolor": "rgba(0,0,0,0)",
                "steps": [],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": max
                }
            },
            domain={'x': [0, 1], 'y': [0, 1]}
        )

        fig = go.Figure([base_gauge, min_threshold, max_threshold])
        fig.update_layout(height=400, width=500)

        return fig

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