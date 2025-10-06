from sensors.sensor import Sensor
from dash import dcc
import plotly.graph_objects as go

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
        return go.Figure(go.Indicator(
            mode="gauge+number",
            value=current,
            title={'text': "Temperature Today"},
            gauge={
                'axis': {'range': [min - 1, max + 1]},
                'bar': {'color': "red"},
                'steps': [
                    {'range': [min, max], 'color': "lightblue"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': current
                }
            }
        ))

    def dashboard_gauge(self):
        return dcc.Graph(
            id=self.key
        )