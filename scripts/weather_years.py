import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import argparse
import yaml
import pandas as pd
from helpers.ETM_API import ETM_API, SessionWithUrlBase
from helpers.Scenario import ScenarioCollection
from helpers.Curves import CurveFile

class HeatDemandCurveGenerator:
    def __init__(self, settings_path='config/local.settings.yml'):
        self.settings = self.load_settings(settings_path)
        self.curves = None
        self.weather_curves = None

    def load_settings(self, settings_path):
        # Load the settings from the provided YAML file
        with open(settings_path, 'r') as file:
            settings = yaml.safe_load(file)
        return settings

    def generate_heat_demand_curves(self, scenario):
        # Set the heat demand curves for the specific scenario
        scenario.heat_demand = str(Path(self.settings['input_curves_folder']).resolve() / scenario.heat_demand)
        scenario.set_heat_demand_curves()
        # Store the generated heat demand curves for further processing
        self.curves = list(scenario.heat_demand_curves)

    def generate_building_curves(self, scenario):
        scenario.heat_demand = str(Path(self.settings['input_curves_folder']).resolve() / scenario.heat_demand)
        scenario.set_building_agriculture_curves()
        # Store the generated building curves for further processing
        self.curves.extend(scenario.heat_demand_curves)

    def load_user_weather_curves(self):
        # Load weather curves from the input/curves folder
        curves_folder = Path(self.settings['input_curves_folder']).resolve()

        # Separate handling for generated and user-supplied weather curves
        insulation_types = ["terraced_houses", "apartments", "semi_detached_houses", "detached_houses"]
        insulation_levels = ["high", "medium", "low"]
        generatable_curves = [f"insulation_{house_type}_{level}" for house_type in insulation_types for level in insulation_levels]
        generatable_curves.extend(["buildings_heating", "agriculture_heating"])

        # Load user-uploaded weather curves (files starting with 'weather_')
        weather_curve_files = list(curves_folder.glob("weather_*.csv"))
        self.weather_curves = {}

        for weather_curve_file in weather_curve_files:
            curve_file = CurveFile.from_csv(weather_curve_file)
            self.weather_curves.update({curve.key: curve for curve in curve_file.curves})

        # Handle missing generated curves
        for curve_name in generatable_curves:
            if curve_name not in self.weather_curves:
                print(f"{curve_name} not found in input. Generating curve.")

    def create_etm_session(self):
        # Create a session using the helper class with base URL from settings
        session = SessionWithUrlBase(self.settings['local_engine_url'])
        return session

    def upload_to_etm(self, session, scenario):
        # Set up connection with ETM API
        api = ETM_API(session, scenario)
        curve_file_dict = self.prepare_curve_file_dict()

        # Upload the curves to the scenario
        print(f"Uploading curves to scenario: {scenario.short_name}")
        api.update(curve_file_dict)

    def prepare_curve_file_dict(self):
        # Create a dictionary for both heat demand curves and weather curves to be uploaded to ETM
        curve_file_dict = {curve.key: curve for curve in self.curves}
        curve_file_dict.update(self.weather_curves)
        return curve_file_dict

    def export_curves(self, scenario):
        output_folder = Path(self.settings['output_curves_folder']).resolve() / scenario.short_name
        output_folder.mkdir(parents=True, exist_ok=True)

        # Export heat demand curves
        for curve in self.curves:
            curve.to_csv(folder=str(output_folder))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate and export weather curves.")
    args = parser.parse_args()

    settings_path = 'config/local.settings.yml'  # Change this to point to your local settings file

    generator = HeatDemandCurveGenerator(settings_path)
    for scenario in ScenarioCollection.from_csv():  # Load scenarios from scenario_list.csv
        print(f"Loaded scenario: {scenario.short_name}")
        generator.generate_heat_demand_curves(scenario)
        generator.load_user_weather_curves()
        generator.generate_building_curves(scenario)

        generator.export_curves(scenario)

        # Create the ETM session and upload the curves for this scenario
        session = generator.create_etm_session()
        generator.upload_to_etm(session, scenario)
