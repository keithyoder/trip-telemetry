from trip_detector import TripDetector
from dash_daq import LEDDisplay
from sensors.sensor import Sensor

class OdometerToday(Sensor):
    def __init__(self):
        super().__init__(None, "odometer_today", "km", precision=2)
        self.detector = TripDetector()

    def value(self):
        try:
            trips = self.detector.todays_trips()
            total_distance = sum(trip['total_distance_meters'] for trip in trips)
            return super().value(total_distance / 1000)  # Convert to kilometers
        except Exception as e:
            return None

    def dashboard_gauge(self):
        return LEDDisplay(
            id=self.key,
            label="Total Distance Today (km)",
            value=0.0,
            color="#FFFFFF",  # White numbers
            backgroundColor="#000000",  # Black background
            size=32,  # Adjust size as needed
        )