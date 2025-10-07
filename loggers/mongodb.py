from pymongo import MongoClient
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def MongoClient():
    client = MongoClient('localhost', 27017)
    db = client['pi_i2c_logger']
    collection = db['logs']
    return client, db, collection

class MongoDBLogger:
    def __init__(self):
        self.client, self.db, self.collection = MongoClient()
        self.local_tz = datetime.now().astimezone().tzinfo

    def today_start(self):
        local_midnight = datetime.now(self.local_tz).replace(hour=0, minute=0, second=0, microsecond=0)

        # Convert to UTC
        return local_midnight.astimezone(ZoneInfo("UTC"))
    
    def tomorrow_start(self):
        local_midnight = datetime.now(self.local_tz).replace(hour=0, minute=0, second=0, microsecond=0)
        return (local_midnight + timedelta(days=1)).astimezone(ZoneInfo("UTC"))

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
        pipeline = [
            {
                '$addFields': {
                    'ts': { '$toDate': "$timestamp" }
                }
            },
            {
                "$match": {
                    "ts": {
                        "$gte": self.today_start(),
                        "$lt": self.tomorrow_start()
                    },
                    key: {"$ne": None}   # <- exclude nulls
                }
            },
            {
                "$group": {
                    "_id": None,
                    "maxReading": {
                        "$top": {
                            "sortBy": {key: -1},
                            "output": {
                                "value": "$"+key,
                                "time": "$timestamp"
                            }
                        }
                    },
                    "minReading": {
                        "$top": {
                            "sortBy": {key: 1},
                            "output": {
                                "value": "$"+key,
                                "time": "$timestamp"
                            }
                        }
                    }
                }
            }
        ]
        return list(self.collection.aggregate(pipeline))