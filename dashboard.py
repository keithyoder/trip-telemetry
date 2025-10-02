from dash import Dash, html, dcc, Input, Output, callback
import dash_daq as daq

app = Dash()

app.layout = html.Div([
    daq.LEDDisplay(
        id='my-LED-display-1',
        label="Temperature (°C)",
        value=26.5
    ),
])

@callback(
    Output('my-LED-display-1', 'value'),
    Input('my-LED-display-slider-1', 'value')
)
def update_output(value):
    return str(value)

if __name__ == '__main__':
    app.run(debug=True)
