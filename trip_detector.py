from pymongo import MongoClient
from datetime import datetime
from typing import List, Dict, Optional
import math
import os
import pandas as pd
from geopandas import GeoDataFrame
from shapely.geometry import LineString
from loggers.mongodb import MongoClient
from helpers.today import Today

class TripDetector:
    def __init__(self):
        """Initialize connection to MongoDB"""
        _, _, self.collection = MongoClient()
        self.cached_trips = []  # Store all detected trips
        self.last_processed_timestamp = None  # Track last processed log
        self.current_incomplete_trip = None  # Store ongoing trip state
    
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
    
    def clear_cache(self):
        """Clear all cached trips and reset state"""
        self.cached_trips = []
        self.last_processed_timestamp = None
        self.current_incomplete_trip = None
        self.currently_travelling = False
    
    def todays_trips(self, use_cache: bool = True) -> List[Dict]:
        """
        Detect trips for the current day
        
        Parameters:
        - use_cache: If True, only process new logs since last detection
        """
        return self.detect_trips(
            start_date=Today.start(), 
            end_date=Today.end(),
            use_cache=use_cache
        )
    
    def get_all_trips(self) -> List[Dict]:
        """Return all cached trips"""
        return self.cached_trips.copy()
    
    def _finalize_trip(self, current_trip: Dict, trip_id: int, 
                       min_trip_distance: float, min_trip_duration: int) -> Optional[Dict]:
        """
        Validate and format a trip for output
        
        Returns None if trip doesn't meet minimum requirements
        """
        trip_duration = (current_trip['end_time'] - current_trip['start_time']).total_seconds()
        
        # Validate trip meets minimum requirements
        if (current_trip['total_distance'] < min_trip_distance or 
            trip_duration < min_trip_duration):
            return None
        
        return {
            'trip_id': trip_id,
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
            'avg_speed_ms': current_trip['total_distance'] / trip_duration if trip_duration > 0 else 0,
            'point_count': len(current_trip['points']),
            'points': current_trip['points']
        }

    def detect_trips(self, 
                     start_date: datetime = None,
                     end_date: datetime = None,
                     min_speed: float = 1.0,
                     max_stop_duration: int = 300,
                     min_trip_distance: float = 200,
                     min_trip_duration: int = 60,
                     max_stationary_distance: float = 10,
                     min_movement_speed: float = 0.5,
                     use_cache: bool = True) -> List[Dict]:
        """
        Detect trips from GPS log data with intelligent caching
        
        Parameters:
        - start_date/end_date: Filter logs by date range
        - min_speed: Minimum speed to consider vehicle moving (m/s)
        - max_stop_duration: Maximum stop time before trip ends (seconds)
        - min_trip_distance: Minimum distance for valid trip (meters)
        - min_trip_duration: Minimum duration for valid trip (seconds)
        - max_stationary_distance: Max distance for GPS drift detection (meters)
        - min_movement_speed: Minimum speed threshold to validate actual movement (m/s)
        - use_cache: If True, only process logs after last_processed_timestamp
        """
        
        # Build query
        query = {}
        
        if use_cache and self.last_processed_timestamp is not None:
            # Only query logs after last processed timestamp
            query['timestamp'] = {'$gt': self.last_processed_timestamp}
            
            # Also apply end_date if specified
            if end_date:
                query['timestamp']['$lte'] = end_date
        else:
            # Full query with date range
            if start_date or end_date:
                query['timestamp'] = {}
                if start_date:
                    query['timestamp']['$gte'] = start_date
                if end_date:
                    query['timestamp']['$lte'] = end_date
        
        # Fetch logs sorted by timestamp
        logs = list(self.collection.find(query).sort('timestamp', 1))
        
        if not logs:
            # Return cached trips that fall within the date range
            if use_cache and self.cached_trips:
                return self._filter_trips_by_date(self.cached_trips, start_date, end_date)
            return []
        
        # Initialize from cache if available
        if use_cache and self.current_incomplete_trip is not None:
            current_trip = self.current_incomplete_trip
            # Get last log from incomplete trip for continuity
            last_log = current_trip['points'][-1] if current_trip['points'] else None
            last_log_time = current_trip['end_time']
            stopped_since = current_trip.get('stopped_since')
        else:
            current_trip = None
            last_log = None
            last_log_time = None
            stopped_since = None
        
        new_trips = []
        next_trip_id = len(self.cached_trips) + 1
        
        for i, log in enumerate(logs):
            lat = log.get('gps_latitude')
            lon = log.get('gps_longitude')
            speed = log.get('gps_speed', 0)
            timestamp = log.get('timestamp')
            
            # Skip invalid GPS data
            if lat is None or lon is None:
                continue
            
            # Calculate distance from last point if available
            distance_moved = 0
            if last_log is not None:
                distance_moved = self.haversine_distance(
                    last_log['gps_latitude'], last_log['gps_longitude'],
                    lat, lon
                )
            
            # Check for time gap between logs
            if current_trip is not None and last_log_time is not None:
                time_gap = (timestamp - last_log_time).total_seconds()
                
                # End trip if gap exceeds threshold
                if time_gap > max_stop_duration:
                    finalized_trip = self._finalize_trip(
                        current_trip, next_trip_id, 
                        min_trip_distance, min_trip_duration
                    )
                    if finalized_trip:
                        new_trips.append(finalized_trip)
                        self.cached_trips.append(finalized_trip)
                        next_trip_id += 1
                    
                    current_trip = None
                    stopped_since = None
            
            # Determine if vehicle is moving
            is_moving = speed >= min_speed
            
            # Additional validation: check if actually moved significantly
            if is_moving and last_log is not None:
                time_delta = (timestamp - last_log_time).total_seconds() if last_log_time else 1
                if distance_moved < max_stationary_distance and time_delta > 5:
                    is_moving = False
            
            if is_moving:
                stopped_since = None
                
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
                    if distance_moved > 0:
                        current_trip['total_distance'] += distance_moved
                    
                    current_trip['end_time'] = timestamp
                    current_trip['end_lat'] = lat
                    current_trip['end_lon'] = lon
                    current_trip['max_speed'] = max(current_trip['max_speed'], speed)
                    current_trip['points'].append(log)
            else:
                # Vehicle stopped or stationary
                if current_trip is not None:
                    if stopped_since is None:
                        stopped_since = timestamp
                    
                    stop_duration = (timestamp - stopped_since).total_seconds()
                    if stop_duration > max_stop_duration:
                        finalized_trip = self._finalize_trip(
                            current_trip, next_trip_id,
                            min_trip_distance, min_trip_duration
                        )
                        if finalized_trip:
                            new_trips.append(finalized_trip)
                            self.cached_trips.append(finalized_trip)
                            next_trip_id += 1
                        
                        current_trip = None
                        stopped_since = None
            
            last_log = log
            last_log_time = timestamp
        
        # Update state
        self.last_processed_timestamp = logs[-1].get('timestamp') if logs else self.last_processed_timestamp
        
        # Store incomplete trip for next run
        if current_trip is not None:
            current_trip['stopped_since'] = stopped_since
            self.current_incomplete_trip = current_trip
            self.currently_travelling = True
        else:
            self.current_incomplete_trip = None
            self.currently_travelling = False
        
        # Return appropriate trips based on date range
        if use_cache:
            return self._filter_trips_by_date(self.cached_trips, start_date, end_date)
        else:
            # Handle incomplete trip at end for non-cached mode
            if current_trip is not None:
                finalized_trip = self._finalize_trip(
                    current_trip, next_trip_id,
                    min_trip_distance, min_trip_duration
                )
                if finalized_trip:
                    new_trips.append(finalized_trip)
            
            return new_trips
    
    def _filter_trips_by_date(self, trips: List[Dict], start_date: datetime = None, 
                              end_date: datetime = None) -> List[Dict]:
        """Filter trips by date range"""
        if not start_date and not end_date:
            return trips
        
        filtered = []
        for trip in trips:
            trip_start = trip['start_time']
            if start_date and trip_start < start_date:
                continue
            if end_date and trip_start > end_date:
                continue
            filtered.append(trip)
        
        return filtered

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
            pd.DataFrame([{
                "id": trip_id,
                "start": trip['start_time'].isoformat(),
                "end": trip['end_time'].isoformat(),
                "distance_m": trip['total_distance_meters'],
                "duration_s": trip['duration_seconds']
            }]),
            geometry=[line],
            crs="EPSG:4326"
        )
        filepath = os.path.join(output_dir, filename)
        gdf_line.to_file(filepath, driver="KML")
        
        return filepath
    
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
    
    def get_trip_summary(self, trips: List[Dict] = None) -> Dict:
        """
        Generate summary statistics for trips
        
        Parameters:
        - trips: List of trips to summarize (defaults to all cached trips)
        
        Returns:
        - Dictionary with aggregate statistics
        """
        if trips is None:
            trips = self.cached_trips
        
        if not trips:
            return {
                'total_trips': 0,
                'total_distance_km': 0,
                'total_duration_hours': 0,
                'avg_trip_distance_km': 0,
                'avg_trip_duration_minutes': 0,
                'max_speed_kmh': 0
            }
        
        total_distance = sum(t['total_distance_meters'] for t in trips)
        total_duration = sum(t['duration_seconds'] for t in trips)
        max_speed = max(t['max_speed_ms'] for t in trips)
        
        return {
            'total_trips': len(trips),
            'total_distance_km': total_distance / 1000,
            'total_duration_hours': total_duration / 3600,
            'avg_trip_distance_km': (total_distance / len(trips)) / 1000,
            'avg_trip_duration_minutes': (total_duration / len(trips)) / 60,
            'max_speed_kmh': max_speed * 3.6
        }