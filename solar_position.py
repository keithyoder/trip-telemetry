from datetime import datetime, timedelta
import math
import pytz


class SolarPosition:
    RISE_SET_ANGLE = 90.833  # degrees, angle below horizon at sunrise/sunset
    CIVIL_TWILIGHT_ANGLE = 96.0  # degrees, angle below horizon at civil twilight

    def __init__(self, date, coordinates, timezone="America/Recife"):
        # ensure datetime with tz
        if isinstance(date, datetime):
            self.date = date.astimezone(pytz.timezone(timezone))
        else:
            self.date = datetime.combine(date, datetime.min.time(), tzinfo=pytz.timezone(timezone))

        self.coordinates = coordinates
        self.offset = self.date.utcoffset().total_seconds()

        # precompute everything
        self.dawn = self._to_datetime(
            720 - 4 * (self.coordinates['longitude'] + self._degrees(self._hora_angle(self.CIVIL_TWILIGHT_ANGLE))) - self._eqtime()
        )
        self.sunrise = self._to_datetime(
            720 - 4 * (self.coordinates['longitude'] + self._degrees(self._hora_angle(self.RISE_SET_ANGLE))) - self._eqtime()
        )
        self.solar_noon = self._to_datetime(
            720 - 4 * self.coordinates['longitude'] - self._eqtime()
        )
        self.sunset = self._to_datetime(
            720 - 4 * (self.coordinates['longitude'] + self._degrees(-1 * self._hora_angle(self.RISE_SET_ANGLE))) - self._eqtime()
        )
        self.dusk = self._to_datetime(
            720 - 4 * (self.coordinates['longitude'] + self._degrees(-1 * self._hora_angle(self.CIVIL_TWILIGHT_ANGLE))) - self._eqtime()
        )
        self.day_length = self.sunset - self.sunrise  # timedelta

    # -------------------------
    # Private helpers
    # -------------------------

    def _fractional_year(self):
        doy = self.date.timetuple().tm_yday
        return 2 * math.pi * (doy - 1 + (self.date.hour - 12) / 24.0) / 365.0

    def _eqtime(self):
        g = self._fractional_year()
        return 229.18 * (
            0.000075 + 0.001868 * math.cos(g)
            - 0.032077 * math.sin(g)
            - 0.014615 * math.cos(2 * g)
            - 0.040849 * math.sin(2 * g)
        )

    def _declination(self):
        g = self._fractional_year()
        return (
            0.006918
            - 0.399912 * math.cos(g)
            + 0.070257 * math.sin(g)
            - 0.006758 * math.cos(2 * g)
            + 0.000907 * math.sin(g)
            - 0.002697 * math.cos(3 * g)
            + 0.00148 * math.sin(3 * g)
        )

    def _radians(self, degrees):
        return degrees * math.pi / 180

    def _degrees(self, radians):
        return radians * 180 / math.pi

    def _to_datetime(self, minutes):
        start_of_day = self.date.replace(hour=0, minute=0, second=0, microsecond=0)
        return start_of_day + timedelta(minutes=minutes, seconds=self.offset)

    def _hora_angle(self, angle):
        lat = self._radians(self.coordinates['latitude'])
        dec = self._declination()
        return math.acos(
            (math.cos(self._radians(angle)) / (math.cos(lat) * math.cos(dec)))
            - (math.tan(lat) * math.tan(dec))
        )
