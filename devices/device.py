class Device:
    def __init__(self, name):
        self.name = name
        self.values = {}

    def read(self):
        if self.is_connected():
            self.values = {}
            for sensor in self.sensors:
                self.values[sensor.key] = sensor.value()

    def is_connected(self):
        raise NotImplementedError("This method should be overridden by subclasses.")

    def __str__(self):
        return f"Device: {self.name}"
