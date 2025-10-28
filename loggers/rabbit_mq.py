import pymongo
import pika
import json
import os
from datetime import datetime
from bson import ObjectId
from dotenv import load_dotenv
import threading
import time
from loggers.mongodb import MongoClient

load_dotenv()

class RabbitMQLogger:
    def __init__(self, rabbitmq_config=None, sync_interval=30):
        """
        Offline-first logger that queues to MongoDB and syncs to RabbitMQ when connected
        
        Parameters:
        - rabbitmq_config: Dict with RabbitMQ connection settings
        - sync_interval: Seconds between sync attempts (default: 30)
        """
        self.client, self.db, self.collection = MongoClient()
        
        # Collection for unsent messages queue
        self.queue_collection = self.db['rabbitmq_queue']
        self.queue_collection.create_index('created_at')
        
        # RabbitMQ config
        self.rabbitmq_config = rabbitmq_config or {
            'host': os.getenv('RABBITMQ_HOST', 'trip.tessi.com.br'),
            'port': int(os.getenv('RABBITMQ_PORT', 5672)),
            'vhost': os.getenv('RABBITMQ_VHOST', 'trip_sync'),
            'user': os.getenv('RABBITMQ_USER'),
            'password': os.getenv('RABBITMQ_PASSWORD'),
            'queue': os.getenv('RABBITMQ_QUEUE', 'telemetry_sync'),
            'connection_timeout': int(os.getenv('RABBITMQ_TIMEOUT', 5))
        }
        
        self.rabbitmq_connection = None
        self.rabbitmq_channel = None
        self.is_connected = False
        self.sync_interval = sync_interval
        
        # Start background sync thread
        self.running = True
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        
        print("[INIT] RabbitMQ Queue Logger initialized")
        print(f"[QUEUE] Queue size: {self.get_queue_size()} messages")

    def _setup_rabbitmq(self):
        """Attempt to connect to RabbitMQ"""
        try:
            user = self.rabbitmq_config.get('user')
            password = self.rabbitmq_config.get('password')
            host = self.rabbitmq_config.get('host')
            
            if not user or not password or not host:
                return False
            
            credentials = pika.PlainCredentials(user, password)
            parameters = pika.ConnectionParameters(
                host=host,
                port=self.rabbitmq_config.get('port', 5672),
                virtual_host=self.rabbitmq_config.get('vhost', '/'),
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=self.rabbitmq_config.get('connection_timeout', 5),
                connection_attempts=1,
                socket_timeout=self.rabbitmq_config.get('connection_timeout', 5)
            )
            
            # Close existing connection if any
            if self.rabbitmq_connection and not self.rabbitmq_connection.is_closed:
                self.rabbitmq_connection.close()
            
            self.rabbitmq_connection = pika.BlockingConnection(parameters)
            self.rabbitmq_channel = self.rabbitmq_connection.channel()
            self.rabbitmq_channel.queue_declare(
                queue=self.rabbitmq_config.get('queue', 'telemetry_sync'),
                durable=True
            )
            
            self.is_connected = True
            print(f"[OK] Connected to RabbitMQ at {host}")
            return True
            
        except Exception as e:
            self.is_connected = False
            if self.rabbitmq_connection and not self.rabbitmq_connection.is_closed:
                try:
                    self.rabbitmq_connection.close()
                except:
                    pass
            return False

    def _clean_value(self, value):
        """Convert a value to JSON-serializable format"""
        if isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, ObjectId):
            return str(value)
        elif isinstance(value, dict):
            return self._clean_document(value)
        elif isinstance(value, list):
            return [self._clean_value(v) for v in value]
        elif isinstance(value, bytes):
            return value.decode('utf-8', errors='ignore')
        else:
            return value

    def _clean_document(self, document):
        """Convert MongoDB document to plain JSON"""
        clean = {}
        for key, value in document.items():
            clean[key] = self._clean_value(value)
        return clean

    def _publish_message(self, message):
        """Publish a single message to RabbitMQ"""
        if not self.is_connected or not self.rabbitmq_channel:
            return False
        
        try:
            if self.rabbitmq_connection.is_closed:
                return False
            
            self.rabbitmq_channel.basic_publish(
                exchange='',
                routing_key=self.rabbitmq_config.get('queue', 'telemetry_sync'),
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                )
            )
            return True
            
        except Exception as e:
            print(f"[ERROR]  Publish failed: {e}")
            self.is_connected = False
            return False

    def _sync_queue(self):
        """Sync queued messages to RabbitMQ"""
        if not self.is_connected:
            if not self._setup_rabbitmq():
                return 0
        
        # Get oldest messages first
        queued_messages = list(self.queue_collection.find().sort('created_at', 1).limit(100))
        
        if not queued_messages:
            return 0
        
        synced_count = 0
        
        for queued_msg in queued_messages:
            message = queued_msg.get('message')
            
            if self._publish_message(message):
                # Successfully published, remove from queue
                self.queue_collection.delete_one({'_id': queued_msg['_id']})
                synced_count += 1
            else:
                # Failed to publish, stop trying
                break
        
        if synced_count > 0:
            print(f"[OK] Synced {synced_count} messages to RabbitMQ")
            remaining = self.get_queue_size()
            if remaining > 0:
                print(f"[QUEUE] {remaining} messages remaining in queue")
        
        return synced_count

    def _sync_loop(self):
        """Background thread that continuously tries to sync"""
        print(f"[QUEUE] Sync loop started (interval: {self.sync_interval}s)")
        
        while self.running:
            try:
                queue_size = self.get_queue_size()
                
                if queue_size > 0:
                    if not self.is_connected:
                        print(f"[SYNC] Attempting to connect... ({queue_size} messages queued)")
                    
                    self._sync_queue()
                
                # Sleep for sync interval
                time.sleep(self.sync_interval)
                
            except Exception as e:
                print(f"[ERROR] Sync loop error: {e}")
                time.sleep(self.sync_interval)

    def write(self, data):
        """Write data to MongoDB and queue for RabbitMQ"""
        try:
            # Ensure timestamp is in ISO format
            if 'timestamp' not in data:
                data['timestamp'] = datetime.now().isoformat()
            elif isinstance(data['timestamp'], datetime):
                data['timestamp'] = data['timestamp'].isoformat()
            
            data['_id'] = data['timestamp']
            
            # Save to MongoDB logs
            self.collection.insert_one(data)
            print(f"[OK] Saved to MongoDB: {data['_id']}")
            
            # Prepare message for RabbitMQ
            clean_doc = self._clean_document(data)
            message = {
                'collection': 'logs',
                'document': clean_doc,
                'timestamp': clean_doc.get('timestamp')
            }
            
            # Try to publish immediately if connected
            if self.is_connected and self._publish_message(message):
                print(f"[OK] Published to RabbitMQ: {data['_id']}")
            else:
                # Queue for later sync
                self.queue_collection.insert_one({
                    'message': message,
                    'created_at': datetime.now(),
                    'log_id': data['_id']
                })
                print(f"[QUEUE] Queued for sync: {data['_id']}")
                
        except Exception as e:
            print(f"[ERROR] Write error: {e}")

    def get_queue_size(self):
        """Get number of messages waiting to be synced"""
        return self.queue_collection.count_documents({})

    def get_connection_status(self):
        """Check if connected to RabbitMQ"""
        return self.is_connected

    def force_sync(self):
        """Manually trigger a sync attempt"""
        print("[SYNC] Manual sync triggered")
        return self._sync_queue()

    def clear_queue(self):
        """Clear all queued messages (use with caution!)"""
        count = self.get_queue_size()
        self.queue_collection.delete_many({})
        print(f"[CLEAR]  Cleared {count} messages from queue")

    def close(self):
        """Close connections and stop sync thread"""
        print("[STOP] Shutting down logger...")
        self.running = False
        
        # Wait for sync thread to finish
        if self.sync_thread.is_alive():
            self.sync_thread.join(timeout=5)
        
        # Final sync attempt
        if self.get_queue_size() > 0:
            print("[SYNC] Final sync attempt...")
            self._sync_queue()
        
        # Close connections
        if self.rabbitmq_connection and not self.rabbitmq_connection.is_closed:
            try:
                self.rabbitmq_connection.close()
                print("[CLOSE] RabbitMQ connection closed")
            except:
                pass
        
        self.client.close()
        print("[CLOSE] MongoDB connection closed")
        print(f"[QUEUE] Final queue size: {self.get_queue_size()}")