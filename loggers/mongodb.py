from pymongo import MongoClient

class MongoDBLogger:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['pi_i2c_logger']
        self.collection = self.db['logs']

    def close(self):
        self.client.close()

    def write(self, data):
        try:
            data['_id'] = None  # let MongoDB create the ID
            self.collection.insert_one(data)
        except Exception as e:
            # avoid infinite recursion in case logging fails
            print(f"Mongo logging error: {e}")
