import time
from sensors.sensor import Sensor
from dash_daq import LEDDisplay
from obd import commands


class FuelUsed(Sensor):
    """
    Fuel volume (mL) consumed since the last time this sensor was
    read, via the speed-density method (RPM + ENGINE_LOAD) and a
    blended stoichiometric AFR for the current ethanol/gasoline mix.

    Deliberately NOT expressed as a rate divided by speed or distance
    (unlike FuelRateEstimate's L/100km) -- that division blows up at
    low speed, as confirmed against real drive data (a 2 km/h moment
    produced an 89 L/100km reading despite a perfectly normal fuel
    rate). This sensor sidesteps that entirely: it's just "how much
    fuel flowed in this interval," summable over ANY later time range
    -- a full trip, a day, a fill-to-fill period -- with no need to
    know trip boundaries or distance at record time.

    Uses wall-clock elapsed time (time.monotonic()) between calls
    rather than assuming a clean 1-second read cadence, since actual
    intervals drift slightly with serial round-trip latency. The
    interval is clamped to MAX_INTERVAL_SECONDS so a long gap (service
    restart, a hang, a slow query) contributes a bounded amount rather
    than multiplying a normal fuel rate by an abnormally long duration
    and producing a spurious spike -- the same class of problem as the
    low-speed L/100km blowup, just triggered by time instead of speed.

    Same underlying accuracy caveats as FuelRateEstimate -- ENGINE_LOAD
    is the ECU's own manufacturer-normalized airflow estimate (not an
    independent measurement), and ETHANOL_BLEND_PCT is a fixed
    assumption, not measured. This sensor changes HOW the estimate is
    expressed (a summable delta rather than an unstable rate), not the
    fundamental trustworthiness ceiling of the underlying estimate.
    """

    DISPLACEMENT_L = 2.0            # Pajero TR4 2.0 (2014), confirmed 1999cc
    ETHANOL_BLEND_PCT = 30          # update if the actual/mandated blend changes
    ETHANOL_DENSITY_KG_L = 0.789
    GASOLINE_DENSITY_KG_L = 0.745
    AFR_ETHANOL = 9.0
    AFR_GASOLINE = 14.7
    AIR_DENSITY_G_L = 1.184         # at 25degC, 101.3 kPa (SAE standard conditions)
    MAX_INTERVAL_SECONDS = 3.0      # normal cadence is ~1s; anything longer
                                     # (restart, hang, slow query) gets clamped
                                     # rather than multiplied straight into the total

    def __init__(self, device):
        super().__init__(device, "obd_fuel_used_ml", "mL", precision=3)
        self.rpm_cmd = commands.RPM
        self.load_cmd = commands.ENGINE_LOAD
        self.min = 0
        self.max = 5  # this is a per-reading delta, not a total -- stays small

        eth_frac_v = self.ETHANOL_BLEND_PCT / 100.0
        gas_frac_v = 1 - eth_frac_v
        eth_mass = eth_frac_v * self.ETHANOL_DENSITY_KG_L
        gas_mass = gas_frac_v * self.GASOLINE_DENSITY_KG_L
        total_mass = eth_mass + gas_mass
        eth_frac_m = eth_mass / total_mass
        gas_frac_m = gas_mass / total_mass
        self.afr_blend = eth_frac_m * self.AFR_ETHANOL + gas_frac_m * self.AFR_GASOLINE
        self.blend_density_kg_l = total_mass

        self._last_time = None

    def value(self):
        now = time.monotonic()
        try:
            rpm = self.device.query(self.rpm_cmd)
            load_pct = self.device.query(self.load_cmd)

            if rpm is None or load_pct is None:
                self._last_time = now
                return None

            max_airflow_g_s = self.DISPLACEMENT_L * (rpm / 120.0) * self.AIR_DENSITY_G_L
            actual_airflow_g_s = max_airflow_g_s * (load_pct / 100.0)
            fuel_mass_g_s = actual_airflow_g_s / self.afr_blend
            fuel_vol_l_s = fuel_mass_g_s / (self.blend_density_kg_l * 1000.0)

            if self._last_time is None:
                # first reading ever -- no prior interval to measure
                dt = 0.0
            else:
                dt = min(now - self._last_time, self.MAX_INTERVAL_SECONDS)
            self._last_time = now

            fuel_used_ml = fuel_vol_l_s * dt * 1000.0
            return super().value(fuel_used_ml)
        except:
            self._last_time = now
            return None

    def dashboard_gauge(self):
        return LEDDisplay(
            id=self.key,
            label="Fuel Used (mL)",
            value=0
        )
