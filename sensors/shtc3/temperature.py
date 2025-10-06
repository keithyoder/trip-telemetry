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
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=current,
            title={"text": "Room Temperature (°C)"},
            gauge={
                "axis": {"range": [0, 40], "tickwidth": 1, "tickcolor": "darkblue"},
                "bar": {"color": "red"},
                "steps": [
                    {"range": [0, 10], "color": "#f8f9fa"},
                    {"range": [10, 20], "color": "#74b9ff"},
                    {"range": [20, 30], "color": "#ffeaa7"},
                    {"range": [30, 40], "color": "#d63031"},
                ],
                "threshold": {
                    "line": {"color": "black", "width": 4},
                    "thickness": 0.75,
                    "value": current
                }
            }
        ))
        for t in [{"value": min, "color": "black"}, {"value": max, "color": "red"}]:
            fig.add_shape(
                type="line",
                x0=0.5, x1=0.5,  # center of gauge
                y0=0, y1=1,      # spans the gauge
                xref="paper", yref="paper",
                line=dict(color=t["color"], width=3),
                name=f"thr_{t['value']}"
            )
            fig.add_annotation(
                x=0.5, y=1.05, xref="paper", yref="paper",
                text=f"{t['label']}: {t['value']}°C",
                showarrow=False,
                font=dict(color=t["color"], size=12)
            )
        fig.update_layout(
            height=200,  # increase height
            width=300,   # increase width
            margin=dict(l=40, r=40, t=60, b=40)
        )
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