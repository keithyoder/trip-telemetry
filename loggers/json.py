import json

class JSONLogger:
    def __init__(self, filename):
        self.file = open(filename, 'w')

    def close(self):
        self.file.close()

    def write(self, data):
        json.dump(data, self.file)
        self.file.write('\n')
        self.file.flush()