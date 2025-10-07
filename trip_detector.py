from pymongo import MongoClient
from datetime import datetime, timedelta
from typing import List, Dict
import math
import os
import pandas as pd
from geopandas import GeoDataFrame
from shapely.geometry import LineString, Point

class TripDetector:
    def __init__(self, mongo_uri: str, database: str, collection: str):
        """Initialize connection to MongoDB"""
        self.client = MongoClient(mongo_uri)
        self.db = self.client[database]
        self.collection = self.db[collection]
    
    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two GPS coordinates in meters"""
        R = 6371000  # Earth's radius in meters
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def detect_trips(self, 
                     start_date: datetime = None,
                     end_date: datetime = None,
                     min_speed: float = 1.0,  # m/s (~3.6 km/h)
                     max_stop_duration: int = 300,  # seconds (5 minutes)
                     min_trip_distance: float = 100,  # meters
                     min_trip_duration: int = 60) -> List[Dict]:
        """
        Detect trips from GPS log data
        
        Parameters:
        - start_date/end_date: Filter logs by date range
        - min_speed: Minimum speed to consider vehicle moving (m/s)
        - max_stop_duration: Maximum stop time before trip ends (seconds)
        - min_trip_distance: Minimum distance for valid trip (meters)
        - min_trip_duration: Minimum duration for valid trip (seconds)
        """
        
        # Build query
        query = {}
        if start_date or end_date:
            query['timestamp'] = {}
            if start_date:
                query['timestamp']['$gte'] = start_date
            if end_date:
                query['timestamp']['$lte'] = end_date
        
        # Fetch logs sorted by timestamp
        logs = list(self.collection.find(query).sort('timestamp', 1))
        
        if not logs:
            return []
        
        trips = []
        current_trip = None
        last_moving_time = None
        
        for i, log in enumerate(logs):
            lat = log.get('gps_latitude')
            lon = log.get('gps_longitude')
            speed = log.get('gps_speed', 0)  # m/s
            timestamp = log.get('timestamp')
            
            if lat is None or lon is None:
                continue
            
            is_moving = speed >= min_speed
            
            if is_moving:
                if current_trip is None:
                    # Start new trip
                    current_trip = {
                        'start_time': timestamp,
                        'start_lat': lat,
                        'start_lon': lon,
                        'end_time': timestamp,
                        'end_lat': lat,
                        'end_lon': lon,
                        'max_speed': speed,
                        'total_distance': 0,
                        'points': [log]
                    }
                else:
                    # Continue current trip
                    prev_log = current_trip['points'][-1]
                    distance = self.haversine_distance(
                        prev_log['gps_latitude'], prev_log['gps_longitude'],
                        lat, lon
                    )
                    
                    current_trip['total_distance'] += distance
                    current_trip['end_time'] = timestamp
                    current_trip['end_lat'] = lat
                    current_trip['end_lon'] = lon
                    current_trip['max_speed'] = max(current_trip['max_speed'], speed)
                    current_trip['points'].append(log)
                
                last_moving_time = timestamp
            
            else:
                # Vehicle stopped
                if current_trip is not None and last_moving_time is not None:
                    stop_duration = (timestamp - last_moving_time).total_seconds()
                    
                    if stop_duration > max_stop_duration:
                        # End current trip
                        trip_duration = (current_trip['end_time'] - current_trip['start_time']).total_seconds()
                        
                        # Validate trip
                        if (current_trip['total_distance'] >= min_trip_distance and 
                            trip_duration >= min_trip_duration):
                            
                            trips.append({
                                'trip_id': len(trips) + 1,
                                'start_time': current_trip['start_time'],
                                'end_time': current_trip['end_time'],
                                'duration_seconds': trip_duration,
                                'start_location': {
                                    'lat': current_trip['start_lat'],
                                    'lon': current_trip['start_lon']
                                },
                                'end_location': {
                                    'lat': current_trip['end_lat'],
                                    'lon': current_trip['end_lon']
                                },
                                'total_distance_meters': current_trip['total_distance'],
                                'max_speed_ms': current_trip['max_speed'],
                                'point_count': len(current_trip['points']),
                                'points': current_trip['points']
                            })
                        
                        current_trip = None
                        last_moving_time = None
        
        # Handle ongoing trip at end of data
        if current_trip is not None:
            trip_duration = (current_trip['end_time'] - current_trip['start_time']).total_seconds()
            
            if (current_trip['total_distance'] >= min_trip_distance and 
                trip_duration >= min_trip_duration):
                
                trips.append({
                    'trip_id': len(trips) + 1,
                    'start_time': current_trip['start_time'],
                    'end_time': current_trip['end_time'],
                    'duration_seconds': trip_duration,
                    'start_location': {
                        'lat': current_trip['start_lat'],
                        'lon': current_trip['start_lon']
                    },
                    'end_location': {
                        'lat': current_trip['end_lat'],
                        'lon': current_trip['end_lon']
                    },
                    'total_distance_meters': current_trip['total_distance'],
                    'max_speed_ms': current_trip['max_speed'],
                    'point_count': len(current_trip['points']),
                    'points': current_trip['points']
                })
        
        return trips


    def export_trip_to_kml(self, trip: Dict, output_dir: str = "trips") -> str:
        """
        Export a single trip to KML format
        
        Parameters:
        - trip: Trip dictionary from detect_trips()
        - output_dir: Directory to save KML files
        
        Returns:
        - Path to the created KML file
        """
        os.makedirs(output_dir, exist_ok=True)
        
        trip_id = trip['trip_id']
        start_time = trip['start_time'].strftime('%Y%m%d_%H%M%S')
        filename = f"trip_{trip_id}_{start_time}.kml"

        df = pd.DataFrame(trip['points'])
        line = LineString(zip(df["gps_longitude"], df["gps_latitude"]))
        gdf_line = GeoDataFrame(
            pd.DataFrame([{"id": 1}]),
            geometry=[line],
            crs="EPSG:4326"
        )
        filepath = os.path.join(output_dir, filename)
        gdf_line.to_file(filepath, driver="KML")

    
    def export_all_trips_to_kml(self, trips: List[Dict], output_dir: str = "trips") -> List[str]:
        """
        Export all trips to individual KML files
        
        Parameters:
        - trips: List of trip dictionaries from detect_trips()
        - output_dir: Directory to save KML files
        
        Returns:
        - List of paths to created KML files
        """
        filepaths = []
        for trip in trips:
            filepath = self.export_trip_to_kml(trip, output_dir)
            filepaths.append(filepath)
        
        return filepaths