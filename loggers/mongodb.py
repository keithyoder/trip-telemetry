from pymongo import MongoClient
from datetime import datetime, timedelta

class MongoDBLogger:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['pi_i2c_logger']
        self.collection = self.db['logs']

    def close(self):
        self.client.close()

    def write(self, data):
        try:
            data['_id'] = data['timestamp']  # let MongoDB create the ID
            self.collection.insert_one(data)
        except Exception as e:
            # avoid infinite recursion in case logging fails
            print(f"Mongo logging error: {e}")

    def avg_per_minute(self, key):
        pipeline = [
            {
                '$addFields': {
                    'ts': { '$toDate': "$timestamp" }
                }
            },
            {
                '$group': {
                    '_id': {
                        '$dateTrunc': { 'date': "$ts", 'unit': "minute" }
                    },
                    'average': {'$avg': f'${key}'}
                }
            },
            {
                '$sort': {'_id': 1}
            }
        ]
        return list(self.collection.aggregate(pipeline))
    
    def daily_max_min(self, key):
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_start = today_start + timedelta(days=1)
        pipeline = [
            {
                '$addFields': {
                    'ts': { '$toDate': "$timestamp" }
                }
            },
            {
                "$match": {
                    "ts": {
                        "$gte": today_start,
                        "$lt": tomorrow_start
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "maxReading": {
                        "$top": {
                            "sortBy": {"shtc3_temperature": -1},
                            "output": {
                                "value": "$shtc3_temperature",
                                "time": "$timestamp"
                            }
                        }
                    },
                    "minReading": {
                        "$top": {
                            "sortBy": {"shtc3_temperature": 1},
                            "output": {
                                "value": "$shtc3_temperature",
                                "time": "$timestamp"
                            }
                        }
                    }
                }
            }
        ]
        return list(self.collection.aggregate(pipeline))