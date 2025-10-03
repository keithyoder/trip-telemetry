from dash import Dash, html, dcc, Input, Output, callback
import dash_daq as daq
import time
import asyncio
import threading
from datetime import datetime, UTC
from devices.bmp581 import BMP581
from devices.ltr390 import LTR390
from devices.usb_obd import USBOBD
from loggers.json import JSONLogger

LOG_FILE = "dashboard_log.json"

bmp581 = BMP581(1019)
ltr390 = LTR390()
usb_odb = USBOBD('/dev/tty.usbserial-1130')

devices = [bmp581, ltr390, usb_odb]
values = {}

logger = JSONLogger(LOG_FILE)
app = Dash()

app.layout = html.Div(
    style={
        "display": "grid",
        "gridTemplateColumns": "repeat(4, 1fr)",  # 4 columns
        "gridTemplateRows": "repeat(3, auto)",   # 3 rows
        "gap": "20px",
        "padding": "20px"
    },
    children=[
        daq.Thermometer(
            id='thermometer-1',
            min=0,
            max=40,
            value=20,
            height=120,
            showCurrentValue=True,
            units="C",
            style={"gridColumn": "span 2", "gridRow": "span 1"}
        ),
        daq.LEDDisplay(
            id='my-LED-display-2',
            label="Barometric Pressure (hPa)",
            value=26.5,
            style={"gridColumn": "2 / span 1", "gridRow": "1 / span 1"}
        ),
        daq.LEDDisplay(
            id='my-LED-display-3',
            label="Ambient Light (lux)",
            value=26.5,
            style={"gridColumn": "3 / span 1", "gridRow": "1 / span 1"}
        ),
        dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        )
    ]
)

@callback(
    [
        Output('thermometer-1', 'value'),
        Output('my-LED-display-2', 'value'),
        Output('my-LED-display-3', 'value'),
    ],
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
    if ltr390.values['ltr390_lux'] is None:    
        light = '----' 
    else:
        light = f"{ltr390.values['ltr390_lux']:.0f}"
    return [float(temperature), pressure, light]

def read_sensors():
    while True:
        timestamp = datetime.now(UTC).isoformat()
        values = {"timestamp": timestamp}
        for device in devices:
            if device.is_connected():
                device.read()
        time.sleep(1)
        for device in devices:
            values += device.values
        
        logger.write(values)

def run_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever(read_sensors())

if __name__ == '__main__':
    new_loop = asyncio.new_event_loop()
    
    # Start the async sensor reading in a separate thread
    async_thread = threading.Thread(target=run_async_loop, args=(new_loop,))
    async_thread.daemon = True # Allow the main program to exit even if this thread is running
    async_thread.start()

    app.run(host='0.0.0.0', debug=True)
