import pandas as pd
import numpy as np
import logging
from pathlib import Path
from helpers.Curves import Curve
from helpers.settings import Settings

from .house import House
from .config import insulation_config
from .smoothing import calculate_smoothed_demand

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# General constants
HOURS = 8760
HOURS_PER_DAY = 24

class WeatherYearsGenerator:
    def __init__(self, temp=None, irr=None, wind_speed=None, therm=None, g2a_params=None):
        """
        Initialize the WeatherYearsGenerator with necessary data.

        Params:
            temp (pd.Series): Outside temperature curve of length 8760
            irr (pd.Series): Solar irradiation curve of length 8760
            wind_speed (pd.Series): Wind speed curve of length 8760
            therm (pd.DataFrame): Thermostat settings with columns low, medium, high for 24 hours
            g2a_params (pd.DataFrame): G2A parameters with columns reference, slope, constant
        """
        self.temp = temp.reset_index(drop=True) if temp is not None else None
        self.irr = irr.reset_index(drop=True) if irr is not None else None
        self.wind_speed = wind_speed.reset_index(drop=True) if wind_speed is not None else None
        self.therm = therm if therm is not None else None
        self.g2a_params = g2a_params if g2a_params is not None else None

        # Flags to determine which profiles can be generated
        self.can_generate_house = True
        self.can_generate_buildings_agriculture = True

        # Validate availability of necessary data for each profile type
        if self.temp is None:
            logger.warning("Cannot generate any heat demand profiles without temperature or if they already exist.")
            self.can_generate_house = False
            self.can_generate_buildings_agriculture = False

        if self.irr is None or self.therm is None:
            logger.warning("Cannot generate housing heat demand profiles without both irradiation and thermostat settings or if they already exist.")
            self.can_generate_house = False

        if self.wind_speed is None or self.g2a_params is None:
            logger.warning("Cannot generate building and agriculture heat demand profiles without both wind speed and G2A parameters or if they already exist.")
            self.can_generate_buildings_agriculture = False

        # Validate inputs if all necessary data is present
        if self.can_generate_house and self.can_generate_buildings_agriculture:
            self.validate_inputs()

    def validate_inputs(self):
        """Ensure that all input data have the correct lengths."""
        if self.temp is not None and len(self.temp) != HOURS:
            raise ValueError("Temperature data must have exactly 8760 hourly values.")
        if self.irr is not None and len(self.irr) != HOURS:
            raise ValueError("Irradiation data must have exactly 8760 hourly values.")
        if self.wind_speed is not None and len(self.wind_speed) != HOURS:
            raise ValueError("Wind speed data must have exactly 8760 hourly values.")
        if self.g2a_params is not None:
            if not all(col in self.g2a_params.columns for col in ['reference', 'slope', 'constant']):
                raise ValueError("G2A parameters must include 'reference', 'slope', and 'constant' columns.")

    def generate_all_profiles(self):
        """Generate heat demand profiles for houses, buildings, and agriculture."""
        curves = []

        if self.can_generate_house:
            logger.info("Generating house heat demand profiles...")
            house_curves = self.generate_house_profiles()
            curves.extend(house_curves)
        else:
            logger.info("Skipping house heat demand profiles generation due to missing data.")

        if self.can_generate_buildings_agriculture:
            logger.info("Generating building and agriculture heat demand profiles...")
            building_agriculture_curves = self.generate_building_agriculture_profiles()
            curves.extend(building_agriculture_curves)
        else:
            logger.info("Skipping building and agriculture heat demand profiles generation due to missing data.")

        return curves

    def generate_house_profiles(self):
        """
        Generates profiles for the heat demand of the five house types for three
        insulation types, resulting in 5 * 3 = 15 profiles.

        Returns:
            list of Curve objects
        """
        if self.irr is None or self.therm is None or self.temp is None:
            logger.error("Insufficient data to generate house profiles.")
            return []

        irr_kwh_m2 = insulation_config.from_J_cm2_to_Kwh_m2(self.irr)

        curves = []
        for house_type in insulation_config.HOUSE_NAMES:
            for insulation_type in insulation_config.INSULATION_TYPES:
                curve_name = f'insulation_{house_type}_{insulation_type}'
                try:
                    demand_curve = self._heat_demand_curve(house_type, insulation_type, self.temp, irr_kwh_m2, self.therm)
                    curves.append(Curve(curve_name, demand_curve))
                    logger.debug(f"Generated curve: {curve_name}")
                except Exception as e:
                    logger.error(f"Failed to generate curve {curve_name}: {e}")
        return curves

    def _heat_demand_curve(self, house_type, insulation_type, temp, irr, therm):
        """
        Calculates the heat demand curve for a house and insulation type.

        Returns:
            np.array of length 8760 containing the heat demand curve
        """
        house = House(house_type, insulation_type, therm)
        heat_demand = np.array([
            self._heat_demand_at_hour(house, hour, temp, irr)
            for hour in range(HOURS)
        ])
        return self._smoothe_and_aggregate(heat_demand, insulation_type)

    def _heat_demand_at_hour(self, house, hour, temp, irr):
        """
        Calculates the heat demand for the house type at the specified hour.

        Returns:
            float value of heat demand
        """
        # Hour of the day (0 to 23)
        hour_of_the_day = hour % HOURS_PER_DAY
        return house.calculate_heat_demand(temp[hour], irr[hour], hour_of_the_day)

    def _smoothe_and_aggregate(self, curve, insulation_type):
        """
        Smooth demand curve to turn individual household curves into average/aggregate
        curves of a whole neighbourhood.
        """
        smoothed_curve = calculate_smoothed_demand(curve, insulation_type)
        return self._normalize(smoothed_curve)

    def _normalize(self, curve):
        """Normalizes a curve to sum up to 1/3600."""
        total = np.sum(curve)
        if total == 0:
            logger.warning("Total heat demand is zero during normalization.")
            return curve
        return curve / total / 3600

    def generate_building_agriculture_profiles(self):
        """Generate Curve objects for the buildings and agriculture heating profiles."""
        if self.temp is None or self.wind_speed is None or self.g2a_params is None:
            logger.error("Insufficient data to generate building and agriculture profiles.")
            return []

        try:
            buildings_heating = self._make_heat_demand_profile(self.temp, self.wind_speed)
            agriculture_heating = buildings_heating.copy()  # Assuming same profile

            building_curve = Curve("buildings_heating", buildings_heating)
            agriculture_curve = Curve("agriculture_heating", agriculture_heating)

            logger.debug("Generated building and agriculture heating profiles.")
            return [building_curve, agriculture_curve]
        except Exception as e:
            logger.error(f"Failed to generate building/agriculture profiles: {e}")
            return []

    def _make_heat_demand_profile(self, temperature, wind_speed):
        """Generate a heat demand profile for buildings based on temperature and wind speed."""
        # Effective temperature = temperature - (wind speed / 1.5)
        effective_temp = temperature - (wind_speed / 1.5)

        # Ensure G2A parameters are aligned
        if len(self.g2a_params) != HOURS:
            # If parameters are constants, repeat them
            if len(self.g2a_params) == 1:
                parameters = self.g2a_params.iloc[0].to_dict()
                parameters_df = pd.DataFrame([parameters] * HOURS)
                logger.debug("G2A parameters are constants; repeating for all hours.")
            else:
                raise ValueError("G2A parameters length mismatch and not a single constant value.")
        else:
            parameters_df = self.g2a_params.reset_index(drop=True)

        # Combine effective temperature with G2A parameters
        parameters_df['effective'] = effective_temp.values

        # Apply the heat demand calculation
        profile = parameters_df.apply(
            lambda row: self._calculate_building_heat_demand(
                row['effective'], row['reference'], row['slope'], row['constant']
            ), axis=1
        )

        # Normalize the profile
        profile = self._normalize(profile)
        return profile.values  # Ensure it's a NumPy array

    def _calculate_building_heat_demand(self, effective, reference, slope, constant):
        """Calculates the required heating demand for buildings."""
        if effective < reference:
            return (reference - effective) * slope + constant
        else:
            return constant
