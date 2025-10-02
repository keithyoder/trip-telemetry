from dash import Dash, html, dcc, Input, Output, callback
import dash_daq as daq

app = Dash()

app.layout = html.Div([
    daq.LEDDisplay(
        id='my-LED-display-1',
        label="Temperature (°C)",
        value=26.5
    ),
    dcc.Interval(
        id='interval-component',
        interval=1*1000, # in milliseconds
        n_intervals=0
    )
])

@callback(
    Output('my-LED-display-1', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_output(value):
    from sensors.bmp581 import BMP581
    bmp581 = BMP581(1019)
    bmp581.read()
    return f"{bmp581.values['bmp581_temperature_C']:.2f}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
