import matplotlib.pyplot as plt
import matplotlib.animation as animation
import json
from sensors.usb_obd import USBOBD
from sensors.bmp581 import BMP581
from loggers.json import JSONLogger
from datetime import datetime, UTC

# Constants
AFR = 14.7         # Stoichiometric AFR for gasoline
FUEL_DENSITY = 745 # g/L
HISTORY_LENGTH = 60  # seconds of data
LOG_FILE = "dashboard_log.json"

#usb_odb = USBOBD('/dev/tty.usbserial-1130')
bmp581 = BMP581()

sensor_list = ["temperature_C", "pressure_hPa", "altitude_m"]
#sensor_list = list(usb_odb.COMMANDS.keys())

# Data buffers
sensor_data = []
time_data = []

# Plot setup
plt.style.use("ggplot")
fig, axs = plt.subplots(4, 2, figsize=(12, 8))
fig.suptitle("Live OBD-II Dashboard", fontsize=16)
plot_lines = {}

# Assign plots
for ax, sensor in zip(axs.flat, sensor_list):
    line, = ax.plot([], [], label=sensor)
    plot_lines[sensor] = line
    ax.set_title(sensor)
    ax.set_xlim(0, HISTORY_LENGTH)
    ax.set_ylim(0, 100)
    ax.legend()
    ax.grid(True)

# Logging setup
logger = JSONLogger(LOG_FILE)

# Update function
def update(frame):
    timestamp = datetime.now(UTC).isoformat()
    time_data.append(timestamp)
    if len(time_data) > HISTORY_LENGTH:
        time_data.pop(0)

    # Read OBD values
    #usb_odb.read()
    bmp581.read()
    # Write JSON log entry
    logger.write({"timestamp": timestamp, **bmp581.values})


    sensor_data.append(bmp581.values)
    if len(sensor_data) > HISTORY_LENGTH:
        sensor_data.pop(0)

    # Update plots
    for sensor, line in plot_lines.items():
        y = [data[sensor] for data in sensor_data]
        x = list(range(len(y)))
        line.set_data(x, y)
        ax = line.axes

        # Dynamic Y-axis scaling
        y_non_null = [v for v in y if v is not None]
        if y_non_null:
            ymin = min(y_non_null) * 0.9
            ymax = max(y_non_null) * 1.1
            if ymin == ymax:
                ymax += 1
            ax.set_ylim(ymin, ymax)
        ax.set_xlim(0, HISTORY_LENGTH)

    return plot_lines.values()

# Start animation
ani = animation.FuncAnimation(fig, update, interval=1000)
print("Dashboard running. Close the window to stop.")

try:
    plt.tight_layout()
    plt.show()
finally:
    print("Closing connection and log file.")
    #usb_odb.close()
    logger.close()
