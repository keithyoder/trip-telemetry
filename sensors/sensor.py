import plotly.graph_objects as go

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

    def current_max_min(self, min, max, current):
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
            value=min,
            gauge={
                "axis": {"range": [self.min, self.max], "visible": False},
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
                "axis": {"range": [self.min, self.max], "visible": False},
                "bar": {"color": "rgba(0,0,0,0)"},
                "bgcolor": "rgba(0,0,0,0)",
                "steps": [],
                "threshold": {
                    "line": {"color": "yellow", "width": 4},
                    "thickness": 0.75,
                    "value": max
                }
            },
            domain={'x': [0, 1], 'y': [0, 1]}
        )

        fig = go.Figure([base_gauge, min_threshold, max_threshold])
        fig.update_layout(height=300, width=400)

        return fig