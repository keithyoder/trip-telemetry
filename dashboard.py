from dash import Dash, html, dcc, Input, Output, callback
import dash_daq as daq
import time
from sensors.bmp581 import BMP581
bmp581 = BMP581(1019)
app = Dash()

app.layout = html.Div([
    daq.LEDDisplay(
        id='my-LED-display-1',
        label="Temperature (°C)",
        value=26.5
    ),
    daq.LEDDisplay(
        id='my-LED-display-2',
        label="Barometric Pressure (hPa)",
        value=26.5
    ),
    dcc.Interval(
        id='interval-component',
        interval=1*1000, # in milliseconds
        n_intervals=0
    )
])

@callback(
    [Output('my-LED-display-1', 'value'),
    Output('my-LED-display-2', 'value')],
    Input('interval-component', 'n_intervals')
)
def update_output(n):
    temperature = bmp581.values['bmp581_temperature_C']
    pressure = bmp581.values['bmp581_pressure_hPa']
    if bmp581.values['bmp581_temperature_C'] is None:
        temperature = '----' 
    else:
        temperature = f"{bmp581.values['bmp581_temperature_C']:.1f}"
    if bmp581.values['bmp581_pressure_hPa'] is None:    
        pressure = '----' 
    else:
        pressure = f"{bmp581.values['bmp581_pressure_hPa']:.1f}"
    return [temperature, pressure]

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
    while True:
        bmp581.read()
        time.sleep(1)

