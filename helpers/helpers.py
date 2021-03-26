import pandas as pd
from pathlib import Path

from .Scenario import Scenario
from .Curves import CurveFile

from .file_helpers import (read_scenario_list,
                           validate_scenario_list,
                           read_curve_file,
                           read_scenario_settings)


def initialise_scenarios():
    scenario_list = read_scenario_list()
    validate_scenario_list(scenario_list)

    scenarios = []

    for idx in scenario_list.index:
        scenario = Scenario(scenario_list.iloc[idx])
        scenario.structure_orders()
        scenarios.append(scenario)

    return scenarios


def load_curve_file_dict(scenarios):
    curve_csvs = set([s.curve_file for s in scenarios if s.curve_file])
    curve_dict = {}

    if curve_csvs:
        print(" Reading curve files")
        for file in curve_csvs:
            curve_df = read_curve_file(file)
            curve_file = CurveFile(file, curve_df)
            curve_file.validate()
            curve_file.add_curves()

            curve_dict[file] = curve_file

        return curve_dict


def update_scenarios(scenarios):
    scenario_settings = read_scenario_settings()

    for scenario in scenarios:
        try:
            settings = dict(scenario_settings[scenario.short_name])
            scenario.add_user_values(settings)
        except KeyError:
            print(f"No scenario settings found for {scenario.short_name}")
            scenario.user_values = None


def generate_query_list():
    path = Path(__file__).parents[1] / "data" / "input" / "queries.csv"
    try:
        query_list = pd.read_csv(path)

        return query_list["query"].tolist()

    except FileNotFoundError:
        query_list = pd.DataFrame()
        print("File 'queries.csv' is missing. No query data will be collected")


def print_ids(scenarios, model_url):
    print("\n\nAll done! Open the scenarios in the Energy Transition Model:")
    for scenario in scenarios:
        print(f"{scenario.short_name}: {model_url}/scenarios/{scenario.id}")


def process_arguments(args):
    if len(args) > 1:
        if args[1].lower() in ['beta', 'staging']:
            base_url = "https://beta-engine.energytransitionmodel.com/api/v3"
            model_url = "https://beta-pro.energytransitionmodel.com"
        elif args[1].lower() in ['local', 'localhost']:
            base_url = "http://localhost:3000/api/v3"
            model_url = "http://localhost:4000"
    else:
        base_url = "https://engine.energytransitionmodel.com/api/v3"
        model_url = "https://pro.energytransitionmodel.com"

    return base_url, model_url
