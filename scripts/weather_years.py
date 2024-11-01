import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import argparse
import yaml
from helpers.ETM_API import ETM_API, SessionWithUrlBase
from helpers.Scenario import ScenarioCollection
from helpers.helpers import process_arguments

class HeatDemandCurveGenerator:
    def __init__(self, settings_path='config/local.settings.yml', base_url=None):
        self.settings = self.load_settings(settings_path)
        self.curves = None
        self.weather_curves = None
        self.base_url = base_url

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

    def create_etm_session(self, base_url=None):
        # Create a session using the helper class with base URL from settings
        session = SessionWithUrlBase(self.base_url)
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
        return curve_file_dict

    def export_curves(self, scenario):
        output_folder = Path(self.settings['output_curves_folder']).resolve() / scenario.short_name
        output_folder.mkdir(parents=True, exist_ok=True)

        # Export heat demand curves
        for curve in self.curves:
            curve.to_csv(folder=str(output_folder))

if __name__ == "__main__":
    base_url, model_url, query_only_mode,_ = process_arguments(sys.argv)
    parser = argparse.ArgumentParser(description="Generate and export weather curves.")

    print("Uploading to:", base_url)
    settings_path = 'config/local.settings.yml'  # Change this to point to your local settings file

    generator = HeatDemandCurveGenerator(settings_path, base_url)
    for scenario in ScenarioCollection.from_csv():  # Load scenarios from scenario_list.csv
        print(f"Loaded scenario: {scenario.short_name}")
        generator.generate_heat_demand_curves(scenario)
        generator.export_curves(scenario)

        # Create the ETM session and upload the curves for this scenario
        session = generator.create_etm_session()
        generator.upload_to_etm(session, scenario)
    scenarios = ScenarioCollection.from_csv()
    scenarios.export_ids()
    scenarios.print_urls(model_url)
