import pymongo
from helpers.today import Today

def MongoClient():
    client = pymongo.MongoClient('localhost', 27017)
    db = client['pi_i2c_logger']
    collection = db['logs']
    return client, db, collection

class MongoDBLogger:
    def __init__(self):
        self.client, self.db, self.collection = MongoClient()

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
                        "$gte": Today.start(),
                        "$lt": Today.end()
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