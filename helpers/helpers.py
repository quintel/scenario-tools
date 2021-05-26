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


def add_scenario_settings(scenarios):
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


def convert_to_lower(arr):
    return [s.lower() for s in arr]


def validate_arguments(args, valid, preferred_arguments):
    invalid = set(args) - set(valid)
    if invalid:
        print("\n\033[1m" + "WARNING: The following arguments are invalid and "
              f"will be ignored: {', '.join(invalid)}\033[0m"
              "\nPlease only use the following arguments:" +
              f"\n{preferred_arguments}\n\n")


def process_query_only(args, valid_options):
    return bool(set(valid_options) & set(args))


def process_environment(args, beta, local, pro):
    if set(args) & set(beta):
        base_url = "https://beta-engine.energytransitionmodel.com/api/v3"
        model_url = "https://beta-pro.energytransitionmodel.com"
    elif set(args) & set(local):
        base_url = "http://localhost:3000/api/v3"
        model_url = "http://localhost:4000"
    else:
        base_url = "https://engine.energytransitionmodel.com/api/v3"
        model_url = "https://pro.energytransitionmodel.com"

    return base_url, model_url


def process_arguments(args):
    beta = ['beta', 'staging']
    local = ['local', 'localhost']
    pro = ['pro', 'production']

    query_only = ['query_only', 'query-only', 'query',
                  'read_only', 'read-only', 'read', 'results_only', 'results-only', 'results']

    preferred_arguments = (f"Query-only mode: {query_only[0]}\n" +
                           f"Environments: {pro[0]}, {beta[0]} or {local[0]}.")

    if len(args) > 1:
        arguments = convert_to_lower(args[1:])
        validate_arguments(arguments, beta + local + pro + query_only, preferred_arguments)
        query_only_mode = process_query_only(arguments, query_only)
        base_url, model_url = process_environment(arguments, beta, local, pro)

    else:
        query_only_mode = False
        base_url, model_url = process_environment('', beta, local, pro)

    return base_url, model_url, query_only_mode
