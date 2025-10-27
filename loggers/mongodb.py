import pymongo
import pika
import json
from bson import json_util
from helpers.today import Today
from dotenv import load_dotenv
from os import environ as env
from datetime import datetime
from bson import ObjectId

load_dotenv()

def MongoClient():
    client = pymongo.MongoClient('localhost', 27017)
    db = client['pi_i2c_logger']
    collection = db['logs']
    return client, db, collection

class MongoDBLogger:
    def __init__(self, enable_rabbitmq=None)):
        self.client, self.db, self.collection = MongoClient()
        if enable_rabbitmq is None:
            enable_rabbitmq = env('RABBITMQ_ENABLED', 'true').lower() in ('true', '1', 'yes')
     
        self.rabbitmq_enabled = enable_rabbitmq
        self.rabbitmq_connection = None
        self.rabbitmq_channel = None
        
        if self.rabbitmq_enabled:
            self._setup_rabbitmq()

    def _setup_rabbitmq(self):
        """Initialize RabbitMQ connection"""
        try:
            credentials = pika.PlainCredentials(env.get('RABBITMQ_USER'), env.get('RABBITMQ_PASSWORD'))
            parameters = pika.ConnectionParameters(
                env.get('RABBITMQ_HOST'),
                env.get('RABBITMQ_PORT', 5672),
                'trip_sync',
                credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            self.rabbitmq_connection = pika.BlockingConnection(parameters)
            self.rabbitmq_channel = self.rabbitmq_connection.channel()
            self.rabbitmq_channel.queue_declare(queue='telemetry_sync', durable=True)
            print("RabbitMQ connected successfully")
        except Exception as e:
            print(f"RabbitMQ connection failed: {e}")
            self.rabbitmq_enabled = False

    def _publish_to_rabbitmq(self, document):
        """Publish document to RabbitMQ"""
        if not self.rabbitmq_enabled or not self.rabbitmq_channel:
            return
        
        try:
            # Clean the document to remove MongoDB types
            clean_doc = self._clean_document(document)
            
            message = {
                'collection': 'logs',
                'document': clean_doc,
                'timestamp': clean_doc.get('timestamp')
            }
            
            # Use regular json.dumps (not json_util.default)
            self.rabbitmq_channel.basic_publish(
                exchange='',
                routing_key='telemetry_sync',
                body=json.dumps(message),  # Regular JSON, not MongoDB extended JSON
                properties=pika.BasicProperties(
                    delivery_mode=2,
                )
            )
            print(f"Published to RabbitMQ: {document.get('_id')}")
        except Exception as e:
            print(f"RabbitMQ publish error: {e}")
            self._setup_rabbitmq()

    def _clean_document(self, document):
        """Convert MongoDB document to plain JSON"""
        clean = {}
        for key, value in document.items():
            clean[key] = self._clean_value(value)
        return clean

    def _clean_value(self, value):
        """Clean a single value"""
        if isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, ObjectId):
            return str(value)
        elif isinstance(value, dict):
            return self._clean_document(value)
        elif isinstance(value, list):
            return [self._clean_value(v) for v in value]
        else:
            return value

    def close(self):
        """Close MongoDB and RabbitMQ connections"""
        if self.rabbitmq_connection and not self.rabbitmq_connection.is_closed:
            self.rabbitmq_connection.close()
        self.client.close()

    def write(self, data):
        try:
            data['_id'] = data['timestamp']  # Use timestamp as ID
            self.collection.insert_one(data)
            
            # Publish to RabbitMQ after successful MongoDB insert
            if self.rabbitmq_enabled:
                self._publish_to_rabbitmq(data)
                
        except Exception as e:
            # Avoid infinite recursion in case logging fails
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