class Device:
    def __init__(self, name):
        self.name = name
        self.values = {}

    def read_values(self):
        raise NotImplementedError("This method should be overridden by subclasses.")

    def is_connected(self):
        raise NotImplementedError("This method should be overridden by subclasses.")

    def __str__(self):
        return f"Sensor: {self.name}"