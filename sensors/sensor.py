import plotly.graph_objects as go
from datetime import timezone

class Sensor:
    def __init__(self, device, key, unit, precision=2):
        self.device = device
        self.key = key
        self.unit = unit
        self.description = f"{key} ({unit})"
        self.min = 0
        self.max = 100
        self.precision = precision
        
    def value(self, value):
        return round(value, self.precision)

    def format_time(self, timestamp):
        return timestamp.replace(tzinfo=timezone.utc).astimezone().strftime('%H:%M')

    def current_max_min(self, current, daily_range):
        step = (self.max - self.min) / 4
        base_gauge = go.Indicator(
                mode="gauge+number",
                value=current,
                title={"text": self.description},
                gauge={
                    "axis": {"range": [self.min, self.max]},
                    "bar": {"color": "black"},
                    "steps": [
                        {"range": [0, step], "color": "#f8f9fa"},
                        {"range": [step, step*2], "color": "#74b9ff"},
                        {"range": [step*2, step*3], "color": "#ffeaa7"},
                        {"range": [step*3, step*4], "color": "#d63031"},
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
            value=daily_range['minReading']['value'],
            gauge={
                "axis": {"range": [self.min, self.max], "visible": False},
                "bar": {"color": "rgba(0,0,0,0)"},
                "bgcolor": "rgba(0,0,0,0)",
                "steps": [],
                "threshold": {
                    "line": {"color": "green", "width": 4},
                    "thickness": 0.75,
                    "value": daily_range['minReading']['value']
                }
            },
            domain={'x': [0, 1], 'y': [0, 1]}  # overlay exactly
        )

        max_threshold = go.Indicator(
            mode="gauge",
            value=daily_range['maxReading']['value'],
            gauge={
                "axis": {"range": [self.min, self.max], "visible": False},
                "bar": {"color": "rgba(0,0,0,0)"},
                "bgcolor": "rgba(0,0,0,0)",
                "steps": [],
                "threshold": {
                    "line": {"color": "yellow", "width": 4},
                    "thickness": 0.75,
                    "value": daily_range['maxReading']['value']
                }
            },
            domain={'x': [0, 1], 'y': [0, 1]}
        )

        fig = go.Figure([base_gauge, min_threshold, max_threshold])
        fig.add_annotation(
            x=0.5, y=-0.2, xref="paper", yref="paper",
            text=f"Min: {daily_range['minReading']['value']:.1f}{self.unit} at {self.format_time(daily_range['minReading']['time'])}",
            showarrow=False,
            font=dict(size=14, color="green")
        )

        fig.add_annotation(
            x=0.5, y=-0.35, xref="paper", yref="paper",
            text=f"Max: {daily_range['maxReading']['value']:.1f}{self.unit} at {self.format_time(daily_range['maxReading']['time'])}",
            showarrow=False,
            font=dict(size=14, color="red")
        )
        fig.update_layout(height=300, width=400)

        return fig