from sensors.sensor import Sensor
from dash import dcc, Graph
import plotly.graph_objects as go
from dash_daq import LEDDisplay
from dash_dac import dcc

class Temperature(Sensor):
    def __init__(self, device):
        super().__init__(device, "shtc3_temperature", "C")

    def value(self):
        try:
            temperature, _ = self.device.measurements
            return super().value(temperature)
        except:
            return None

    def dashboard_gauge(self):
        return Graph(
            id=self.key,
            figure=go.Figure(go.Indicator(
                mode="gauge+number",
                value=20.0,
                title={'text': "Temperature Today"},
                gauge={
                    'axis': {'range': [19 - 1, 28 + 1]},
                    'bar': {'color': "red"},
                    'steps': [
                        {'range': [19, 28], 'color': "lightblue"}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': 20.0
                    }
                }
            ))
        )