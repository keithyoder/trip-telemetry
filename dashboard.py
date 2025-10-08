from dash import Dash, html, dcc, Input, Output, callback
import dash_daq as daq
import time
import asyncio
import threading
from datetime import datetime, UTC
from devices.bmp581 import BMP581
from devices.ltr390 import LTR390
from devices.usb_obd import USBOBD
from devices.shtc3 import SHTC3
from devices.gps import GPS
from loggers.mongodb import MongoDBLogger

LOG_FILE = "dashboard_log.json"

bmp581 = BMP581(1019)
ltr390 = LTR390()
shtc3 = SHTC3()
usb_gps = GPS()
usb_odb = USBOBD('/dev/tty.usbserial-1130')

devices = [bmp581, ltr390, usb_odb, shtc3, usb_gps]
values = {}

logger = MongoDBLogger()
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
        bmp581.sensor("bmp581_pressure").dashboard_gauge(),
        ltr390.sensor("ltr390_ambient_light").dashboard_gauge(),
        shtc3.sensor("shtc3_temperature").dashboard_gauge(),
        shtc3.sensor("shtc3_humidity").dashboard_gauge(),
        dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        )
    ]
)

@callback(
    [
        Output('shtc3_temperature', 'figure'),
        Output('bmp581_pressure', 'value'),
        Output('ltr390_ambient_light', 'value'),
        Output('shtc3_humidity', 'figure'),
    ],
    Input('interval-component', 'n_intervals')
)
def update_output(n):
    figure = shtc3.sensor("shtc3_temperature").figure(
        current=values.get("shtc3_temperature", 0),
        daily_range=logger.daily_max_min("shtc3_temperature")[0]
    )
    humidity = shtc3.sensor("shtc3_humidity").figure(
        current=values.get("shtc3_humidity", 0),
        daily_range=logger.daily_max_min("shtc3_humidity")[0]
    )
    if 'bmp581_pressure' not in values:    
        pressure = '0' 
    else:
        pressure = f"{values['bmp581_pressure']:.1f}"

    if 'ltr390_lux' not in values:    
        light = '0' 
    else:
        light = f"{values['ltr390_lux']:.0f}"

    return [figure, pressure, light, humidity]

def read_sensors():
    while True:
        print("before gps")
        print(values.get("timestamp"))
        values["timestamp"] = values.get("gps_timestamp", datetime.now(UTC).replace(microsecond=0))
        print("after gps")
        print(values.get("gps_timestamp"))
        print(values["timestamp"])
        for device in devices:
            if device.is_connected():
                device.read()
        time.sleep(1)
        for device in devices:
            values.update(device.values)
        
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
