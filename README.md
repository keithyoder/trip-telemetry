# TripTelemetry

The goal of this project is to create a Python app that will run on a Raspberry Pi installed in a vehicle and record data from different sensors.  The supported sensors are listed here:

[Sensors](SENSORS.md)

Currently data is logged to a MongoDB collection once every second.


### Installation

To create a virtual environment, go to your project’s directory and run the following command. This will create a new virtual environment in a local folder named .venv:

#### Create Virtual Environment
```bash
python3 -m venv .venv
```

#### Activate Virtual Environment
```bash
source .venv/bin/activate
```

#### Deactivate Virtual Environment
```bash
deactivate
```

#### Install Requirements
```bash
python3 -m pip install -r requirements.txt
```