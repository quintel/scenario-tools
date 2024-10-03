import pandas as pd
from pathlib import Path
from helpers.Curves import Curve
from helpers.settings import Settings

class BuildingsModel:

    def _calculate_heat_demand(self, effective: float, reference: float, slope: float, constant: float) -> float:
        """Calculates the required heating demand for the hour."""
        return (reference - effective) * slope + constant if effective < reference else constant

    def _make_parameters(self, effective: pd.Series) -> pd.DataFrame:
        """Combine effective temperature with reference, slope, and constant parameters."""

        # Ensure reference, slope, and constant all have the same length as effective
        if not (len(self.reference) == len(self.slope) == len(self.constant) == len(effective)):
            raise ValueError("The length of 'reference', 'slope', 'constant', and 'effective' must be equal.")

        # Create DataFrame with reference, slope, constant, and effective values
        parameters = pd.DataFrame({
            "reference": self.reference,
            "slope": self.slope,
            "constant": self.constant,
            "effective": effective
        })

        return parameters

    def make_heat_demand_profile(self, temperature: pd.Series, wind_speed: pd.Series) -> pd.Series:
        """Generate a heat demand profile for buildings based on temperature and wind speed."""

        # Ensure temperature and wind_speed have 8760 values
        if len(temperature) != 8760 or len(wind_speed) != 8760:
            raise ValueError("Both temperature and wind_speed must have exactly 8760 hourly values.")

        # Effective temperature = temperature - (wind speed / 1.5)
        effective = temperature - (wind_speed / 1.5)
        effective = pd.Series(effective, name="effective", dtype=float)

        # Combine effective temperature with G2A parameters
        profiles = self._make_parameters(effective)

        # Apply the heat demand calculation for each row
        profile = profiles.apply(lambda row: self._calculate_heat_demand(
            row["effective"], row["reference"], row["slope"], row["constant"]), axis=1)

        # Scale the profile and assign it a name
        profile = pd.Series(profile, name="buildings_heating", dtype=float)
        profile = profile / profile.sum() / 3.6e3  # Scale profile to energy demand

        return profile

    def generate_curves(self, temperature: pd.Series, wind_speed: pd.Series) -> list:
        """Generate Curve objects for the buildings and agriculture heating profiles."""

        # Generate the heat demand profile for buildings
        buildings_heating = self.make_heat_demand_profile(temperature, wind_speed)
        agriculture_heating = buildings_heating.copy()  # Assume agriculture heating follows the same profile

        # Create Curve objects for both profiles
        building_curve = Curve("buildings_heating", buildings_heating)
        agriculture_curve = Curve("agriculture_heating", agriculture_heating)

        return [building_curve, agriculture_curve]

    def load_from_folder(self, folder: str):
        """Load G2A parameters, temperature, and wind speed from CSV files."""
        folder_path = Path(Settings.get('input_curves_folder')) / folder

        # Load G2A parameters from CSV
        params_file = folder_path / "G2A_parameters.csv"
        df = pd.read_csv(params_file)
        self.reference = df['reference']
        self.slope = df['slope']
        self.constant = df['constant']

        # Load temperature and wind speed from CSV
        temperature_file = folder_path / "temperature.csv"
        wind_speed_file = folder_path / "wind_speed.csv"

        # Load data into Series
        self.temperature = pd.read_csv(temperature_file, header=None).squeeze()
        self.wind_speed = pd.read_csv(wind_speed_file, header=None).squeeze()

    def generate_and_export_curves(self, output_folder: str):
        """Generate and export heat demand curves to CSV files."""
        # Ensure temperature and wind speed data are loaded
        if not hasattr(self, 'temperature') or not hasattr(self, 'wind_speed'):
            raise ValueError("Temperature and wind speed data must be loaded before generating the profile.")

        # Generate the Curve objects
        curves = self.generate_curves(self.temperature, self.wind_speed)

        # Export each curve to CSV
        for curve in curves:
            curve.to_csv(folder=output_folder)
