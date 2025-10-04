class Device:
    def __init__(self, name):
        self.name = name
        self.values = {}
        self.sensors = []

    def read(self):
        if self.is_connected():
            for sensor in self.sensors:
                self.values[sensor.key] = sensor.value()

    def sensor(self, key):
        for sensor in self.sensors:
            if sensor.key == key:
                return sensor
        return None
    
    def is_connected(self):
        raise NotImplementedError("This method should be overridden by subclasses.")

    def __str__(self):
        return f"Device: {self.name}"
