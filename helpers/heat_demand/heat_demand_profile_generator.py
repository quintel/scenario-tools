
import pandas as pd
import numpy as np
from pathlib import Path
from helpers.Curves import Curve
from helpers.settings import Settings

from .house import House
from .config import insulation_config
from .smoothing import calculate_smoothed_demand

# General constants
HOURS = 8760
HOURS_PER_DAY = 24

class HeatDemandGenerator:
    def __init__(self, temp, irr, wind_speed, therm, g2a_params):
        """
        Initialize the HeatDemandGenerator with necessary data.

        Params:
            temp (pd.Series): Outside temperature curve of length 8760
            irr (pd.Series): Solar irradiation curve of length 8760
            wind_speed (pd.Series): Wind speed curve of length 8760
            therm (pd.DataFrame): Thermostat settings with columns low, medium, high for 24 hours
            g2a_params (pd.DataFrame): G2A parameters with columns reference, slope, constant
        """
        self.temp = temp.reset_index(drop=True)
        self.irr = irr.reset_index(drop=True)
        self.wind_speed = wind_speed.reset_index(drop=True)
        self.therm = therm
        self.g2a_params = g2a_params
        self.validate_inputs()

    def validate_inputs(self):
        """Ensure that all input data have the correct lengths."""
        if len(self.temp) != HOURS or len(self.irr) != HOURS or len(self.wind_speed) != HOURS:
            raise ValueError("Temperature, irradiation, and wind speed data must each have exactly 8760 hourly values.")
        if not all(col in self.g2a_params.columns for col in ['reference', 'slope', 'constant']):
            raise ValueError("G2A parameters must include 'reference', 'slope', and 'constant' columns.")

    def generate_all_profiles(self):
        """Generate heat demand profiles for houses, buildings, and agriculture."""
        curves = []
        curves.extend(self.generate_house_profiles())
        curves.extend(self.generate_building_agriculture_profiles())
        return curves

    def generate_house_profiles(self):
        """
        Generates profiles for the heat demand of the five house types for three
        insulation types, resulting in 5 * 3 = 15 profiles.

        Returns:
            list of Curve objects
        """
        irr_kwh_m2 = insulation_config.from_J_cm2_to_Kwh_m2(self.irr)

        curves = []
        for house_type in insulation_config.HOUSE_NAMES:
            for insulation_type in insulation_config.INSULATION_TYPES:
                curve_name = f'insulation_{house_type}_{insulation_type}'
                demand_curve = self._heat_demand_curve(house_type, insulation_type, self.temp, irr_kwh_m2, self.therm)
                curves.append(Curve(curve_name, demand_curve))
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
        return curve / np.sum(curve) / 3600

    def generate_building_agriculture_profiles(self):
        """Generate Curve objects for the buildings and agriculture heating profiles."""
        # Generate the heat demand profile for buildings
        buildings_heating = self._make_heat_demand_profile(self.temp, self.wind_speed)
        agriculture_heating = buildings_heating.copy()  # Assuming same profile

        # Create Curve objects for both profiles
        building_curve = Curve("buildings_heating", buildings_heating)
        agriculture_curve = Curve("agriculture_heating", agriculture_heating)

        return [building_curve, agriculture_curve]

    def _make_heat_demand_profile(self, temperature, wind_speed):
        """Generate a heat demand profile for buildings based on temperature and wind speed."""
        # Effective temperature = temperature - (wind speed / 1.5)
        effective_temp = temperature - (wind_speed / 1.5)

        # Ensure G2A parameters are aligned
        if len(self.g2a_params) != HOURS:
            # If parameters are constants, repeat them
            parameters = self.g2a_params.iloc[0].to_dict()
            parameters_df = pd.DataFrame([parameters]*HOURS)
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
        return profile

    def _calculate_building_heat_demand(self, effective, reference, slope, constant):
        """Calculates the required heating demand for buildings."""
        if effective < reference:
            return (reference - effective) * slope + constant
        else:
            return constant
