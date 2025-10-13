from datetime import datetime, timedelta, date
from zoneinfo import ZoneInfo
import math
from functools import lru_cache


class SolarPosition:
    """
    Calculate solar position and twilight times for a given location and date.
    Uses NOAA solar calculations algorithm.
    """
    
    RISE_SET_ANGLE = 90.833  # degrees, angle below horizon at sunrise/sunset
    CIVIL_TWILIGHT_ANGLE = 96.0  # degrees, angle below horizon at civil twilight
    
    # Pre-compute constants
    TWO_PI = 2 * math.pi
    PI_OVER_180 = math.pi / 180
    DEG_180_OVER_PI = 180 / math.pi

    def __init__(self, date_input, coordinates, timezone="America/Recife"):
        """
        Initialize solar position calculator
        
        Parameters:
        - date_input: datetime or date object
        - coordinates: dict with 'latitude' and 'longitude' keys
        - timezone: timezone string (e.g., 'America/Recife')
        """
        # Ensure datetime with timezone
        tz = ZoneInfo(timezone)
        if isinstance(date_input, datetime):
            self.date = date_input.astimezone(tz)
        else:
            self.date = datetime.combine(date_input, datetime.min.time(), tzinfo=tz)

        self.coordinates = coordinates
        self.lat = coordinates['latitude']
        self.lon = coordinates['longitude']
        self.offset = self.date.utcoffset().total_seconds()
        
        # Pre-compute values used multiple times
        self._frac_year = self._fractional_year()
        self._eq_time = self._eqtime()
        self._decl = self._declination()
        self._lat_rad = self._radians(self.lat)
        
        # Pre-compute base calculation (used in all time calculations)
        self._base_minutes = 720 - 4 * self.lon
        
        # Calculate all times (pre-computed in constructor for efficiency)
        self.dawn = self._calculate_time(self.CIVIL_TWILIGHT_ANGLE, rising=True)
        self.sunrise = self._calculate_time(self.RISE_SET_ANGLE, rising=True)
        self.solar_noon = self._to_datetime(self._base_minutes - self._eq_time)
        self.sunset = self._calculate_time(self.RISE_SET_ANGLE, rising=False)
        self.dusk = self._calculate_time(self.CIVIL_TWILIGHT_ANGLE, rising=False)
        self.day_length = self.sunset - self.sunrise  # timedelta

    # -------------------------
    # Private calculation helpers
    # -------------------------

    def _fractional_year(self) -> float:
        """Calculate fractional year (gamma) for solar equations"""
        doy = self.date.timetuple().tm_yday
        hour_fraction = (self.date.hour - 12) / 24.0
        return self.TWO_PI * (doy - 1 + hour_fraction) / 365.0

    def _eqtime(self) -> float:
        """Calculate equation of time in minutes"""
        g = self._frac_year
        cos_g = math.cos(g)
        sin_g = math.sin(g)
        cos_2g = math.cos(2 * g)
        sin_2g = math.sin(2 * g)
        
        return 229.18 * (
            0.000075 
            + 0.001868 * cos_g
            - 0.032077 * sin_g
            - 0.014615 * cos_2g
            - 0.040849 * sin_2g
        )

    def _declination(self) -> float:
        """Calculate solar declination in radians"""
        g = self._frac_year
        cos_g = math.cos(g)
        sin_g = math.sin(g)
        cos_2g = math.cos(2 * g)
        sin_2g = math.sin(2 * g)
        cos_3g = math.cos(3 * g)
        sin_3g = math.sin(3 * g)
        
        return (
            0.006918
            - 0.399912 * cos_g
            + 0.070257 * sin_g
            - 0.006758 * cos_2g
            + 0.000907 * sin_2g
            - 0.002697 * cos_3g
            + 0.00148 * sin_3g
        )

    def _radians(self, degrees: float) -> float:
        """Convert degrees to radians (optimized)"""
        return degrees * self.PI_OVER_180

    def _degrees(self, radians: float) -> float:
        """Convert radians to degrees (optimized)"""
        return radians * self.DEG_180_OVER_PI

    def _to_datetime(self, minutes: float) -> datetime:
        """Convert minutes from midnight to datetime"""
        start_of_day = self.date.replace(hour=0, minute=0, second=0, microsecond=0)
        return start_of_day + timedelta(minutes=minutes, seconds=self.offset)

    def _hour_angle(self, angle: float) -> float:
        """
        Calculate hour angle for given solar elevation angle
        
        Parameters:
        - angle: Solar elevation angle in degrees
        
        Returns:
        - Hour angle in radians
        """
        cos_lat = math.cos(self._lat_rad)
        cos_dec = math.cos(self._decl)
        tan_lat = math.tan(self._lat_rad)
        tan_dec = math.tan(self._decl)
        
        cos_angle = math.cos(self._radians(angle))
        
        # Calculate hour angle
        ha_cos = (cos_angle / (cos_lat * cos_dec)) - (tan_lat * tan_dec)
        
        # Handle cases where sun doesn't rise/set (polar regions)
        if ha_cos > 1:
            return 0  # Sun never rises
        elif ha_cos < -1:
            return math.pi  # Sun never sets
        
        return math.acos(ha_cos)

    def _calculate_time(self, angle: float, rising: bool = True) -> datetime:
        """
        Calculate sunrise/sunset time for given angle
        
        Parameters:
        - angle: Solar elevation angle in degrees
        - rising: True for sunrise/dawn, False for sunset/dusk
        
        Returns:
        - datetime object for the event
        """
        ha = self._hour_angle(angle)
        ha_degrees = self._degrees(ha if rising else -ha)
        minutes = self._base_minutes - 4 * ha_degrees - self._eq_time
        return self._to_datetime(minutes)

    # -------------------------
    # Public utility methods
    # -------------------------

    def is_daytime(self, check_time: datetime = None) -> bool:
        """
        Check if given time is during daytime (between sunrise and sunset)
        
        Parameters:
        - check_time: datetime to check (defaults to current time)
        
        Returns:
        - True if daytime, False otherwise
        """
        if check_time is None:
            check_time = datetime.now(self.date.tzinfo)
        return self.sunrise <= check_time <= self.sunset

    def is_twilight(self, check_time: datetime = None) -> bool:
        """
        Check if given time is during twilight (between dawn/dusk and sunrise/sunset)
        
        Parameters:
        - check_time: datetime to check (defaults to current time)
        
        Returns:
        - True if twilight, False otherwise
        """
        if check_time is None:
            check_time = datetime.now(self.date.tzinfo)
        return (self.dawn <= check_time < self.sunrise) or (self.sunset < check_time <= self.dusk)

    def time_until_sunset(self, from_time: datetime = None) -> timedelta:
        """
        Calculate time until sunset
        
        Parameters:
        - from_time: reference time (defaults to current time)
        
        Returns:
        - timedelta until sunset (negative if after sunset)
        """
        if from_time is None:
            from_time = datetime.now(self.date.tzinfo)
        return self.sunset - from_time

    def time_until_sunrise(self, from_time: datetime = None) -> timedelta:
        """
        Calculate time until sunrise
        
        Parameters:
        - from_time: reference time (defaults to current time)
        
        Returns:
        - timedelta until sunrise (negative if after sunrise)
        """
        if from_time is None:
            from_time = datetime.now(self.date.tzinfo)
        return self.sunrise - from_time

    def get_sun_position(self, check_time: datetime = None) -> dict:
        """
        Calculate sun's position (elevation and azimuth) at given time
        
        Parameters:
        - check_time: datetime to calculate position for (defaults to current time)
        
        Returns:
        - Dictionary with:
            - 'elevation': Solar elevation angle in degrees (0° = horizon, 90° = zenith, negative = below horizon)
            - 'azimuth': Solar azimuth angle in degrees (0° = North, 90° = East, 180° = South, 270° = West)
            - 'zenith': Zenith angle in degrees (90° - elevation)
        """
        if check_time is None:
            check_time = datetime.now(self.date.tzinfo)
        
        # Ensure check_time is in the same timezone
        if check_time.tzinfo != self.date.tzinfo:
            check_time = check_time.astimezone(self.date.tzinfo)
        
        # Calculate fractional year for this specific time
        doy = check_time.timetuple().tm_yday
        hour_fraction = (check_time.hour + check_time.minute / 60.0 + check_time.second / 3600.0 - 12) / 24.0
        frac_year = self.TWO_PI * (doy - 1 + hour_fraction) / 365.0
        
        # Calculate equation of time for this time
        cos_g = math.cos(frac_year)
        sin_g = math.sin(frac_year)
        cos_2g = math.cos(2 * frac_year)
        sin_2g = math.sin(2 * frac_year)
        
        eq_time = 229.18 * (
            0.000075 
            + 0.001868 * cos_g
            - 0.032077 * sin_g
            - 0.014615 * cos_2g
            - 0.040849 * sin_2g
        )
        
        # Calculate solar declination for this time
        cos_3g = math.cos(3 * frac_year)
        sin_3g = math.sin(3 * frac_year)
        
        decl = (
            0.006918
            - 0.399912 * cos_g
            + 0.070257 * sin_g
            - 0.006758 * cos_2g
            + 0.000907 * sin_2g
            - 0.002697 * cos_3g
            + 0.00148 * sin_3g
        )
        
        # Calculate time offset in minutes from midnight
        time_offset = (check_time.hour * 60 + check_time.minute + check_time.second / 60.0)
        
        # Calculate true solar time
        true_solar_time = time_offset + eq_time + 4 * self.lon - 60 * (check_time.utcoffset().total_seconds() / 3600)
        
        # Calculate hour angle (in degrees, then convert to radians)
        hour_angle_deg = (true_solar_time / 4.0) - 180.0
        hour_angle_rad = self._radians(hour_angle_deg)
        
        # Calculate solar zenith angle
        cos_lat = math.cos(self._lat_rad)
        sin_lat = math.sin(self._lat_rad)
        cos_decl = math.cos(decl)
        sin_decl = math.sin(decl)
        cos_ha = math.cos(hour_angle_rad)
        sin_ha = math.sin(hour_angle_rad)
        
        # Solar elevation angle
        sin_elevation = sin_lat * sin_decl + cos_lat * cos_decl * cos_ha
        elevation_rad = math.asin(sin_elevation)
        elevation = self._degrees(elevation_rad)
        
        # Solar azimuth angle
        cos_elevation = math.cos(elevation_rad)
        
        # Calculate azimuth (accounting for different quadrants)
        if cos_elevation != 0:
            cos_azimuth = (sin_decl - sin_lat * sin_elevation) / (cos_lat * cos_elevation)
            # Clamp to [-1, 1] to handle floating point errors
            cos_azimuth = max(-1, min(1, cos_azimuth))
            azimuth_rad = math.acos(cos_azimuth)
            azimuth = self._degrees(azimuth_rad)
            
            # Adjust azimuth based on hour angle
            if hour_angle_deg > 0:
                azimuth = 360 - azimuth
        else:
            azimuth = 0  # Sun at zenith or nadir
        
        # Calculate zenith angle
        zenith = 90 - elevation
        
        return {
            'elevation': elevation,
            'azimuth': azimuth,
            'zenith': zenith
        }

    def get_solar_elevation(self, check_time: datetime = None) -> float:
        """
        Get solar elevation angle at given time
        
        Parameters:
        - check_time: datetime to calculate for (defaults to current time)
        
        Returns:
        - Solar elevation angle in degrees
        """
        return self.get_sun_position(check_time)['elevation']

    def get_solar_azimuth(self, check_time: datetime = None) -> float:
        """
        Get solar azimuth angle at given time
        
        Parameters:
        - check_time: datetime to calculate for (defaults to current time)
        
        Returns:
        - Solar azimuth angle in degrees (0° = North, 90° = East, 180° = South, 270° = West)
        """
        return self.get_sun_position(check_time)['azimuth']

    def __repr__(self) -> str:
        """String representation of solar times"""
        return (
            f"SolarPosition(date={self.date.date()}, "
            f"sunrise={self.sunrise.strftime('%H:%M:%S')}, "
            f"sunset={self.sunset.strftime('%H:%M:%S')}, "
            f"day_length={self.day_length})"
        )


# -------------------------
# Convenience factory function with caching
# -------------------------

@lru_cache(maxsize=128)
def get_solar_position(date_key: tuple, lat: float, lon: float, timezone: str) -> SolarPosition:
    """
    Cached factory function for SolarPosition
    
    Parameters:
    - date_key: tuple of (year, month, day) for caching
    - lat: latitude
    - lon: longitude
    - timezone: timezone string
    
    Returns:
    - SolarPosition instance
    
    Usage:
        from datetime import date
        coords = {'latitude': -8.0476, 'longitude': -34.877}
        date_key = (2025, 10, 13)
        solar = get_solar_position(date_key, coords['latitude'], coords['longitude'], 'America/Recife')
    """
    date_obj = date(*date_key)
    coordinates = {'latitude': lat, 'longitude': lon}
    return SolarPosition(date_obj, coordinates, timezone)