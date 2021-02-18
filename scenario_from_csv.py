# external modules
import sys
import pandas as pd
from pathlib import Path

# project modules
from ETM_API import ETM_API, SessionWithUrlBase
from Scenario import Scenario


def read_csv(folder, file):
    path = Path(__file__).parent / f"{folder}/{file}.csv"

    try:
        df = pd.read_csv(path, dtype=str)
    except FileNotFoundError:
        print(f"File '{file}.csv' not found in '{folder}' folder. Aborting..")
        sys.exit(1)

    return df


def check_duplicates(arr, file_name, attribute_type):
    arr_lower = [e.lower() for e in arr]
    for elem in arr_lower:
        if arr_lower.count(elem) > 1:
            print(f"Warning! '{elem}' is included twice as a "
                  f"{attribute_type} in {file_name}. "
                  "Please remove one!")
            sys.exit(1)


def validate_scenario_list(scenario_file, columns, short_names):

    check_duplicates(columns, scenario_file, "column")
    check_duplicates(short_names, scenario_file, "short name")


def generate_scenario_objects():
    scenario_file = "scenario_list"
    scenarios = []

    scenario_list = read_csv("data/input", scenario_file)

    columns = list(scenario_list.columns.str.lower())
    short_names = [s.lower() for s in scenario_list["short_name"].tolist()]

    validate_scenario_list(scenario_file, columns, short_names)

    for idx in scenario_list.index:
        scenario = Scenario(scenario_list.iloc[idx])
        scenario.structure_orders()
        scenarios.append(scenario)

    return scenarios


def read_scenario_settings():
    path = Path(__file__).parent / "data" / "input" / "scenario_settings.csv"
    try:
        scenario_settings = pd.read_csv(path, index_col=0, dtype=str)
    except FileNotFoundError:
        print("Cannot find scenario_settings.csv file in the data/input folder")
        scenario_settings = pd.DataFrame()

    return scenario_settings


def add_scenario_settings(scenario, scenario_settings):
    try:
        scenario.user_values = dict(scenario_settings[scenario.short_name])
    except KeyError:
        print(f"No scenario settings found for {scenario.short_name}")


def add_curves(scenario):
    file_name = scenario.curve_file
    if file_name:
        folder = Path(__file__).parent / "data/input/curves"

        curve_df = read_csv(folder, file_name)
        scenario.custom_curves = curve_df.to_dict(orient='list')


def load_scenarios():
    scenarios = generate_scenario_objects()
    scenario_settings = read_scenario_settings()

    for scenario in scenarios:
        add_scenario_settings(scenario, scenario_settings)
        add_curves(scenario)

    return scenarios


def generate_query_list():
    path = Path(__file__).parent / "data" / "input" / "queries.csv"
    try:
        query_list = pd.read_csv(path)

        return query_list["query"].tolist()

    except FileNotFoundError:
        query_list = pd.DataFrame()
        print("File 'queries.csv' is missing. No query data will be collected")


def generate_data_download_dict():
    path = Path(__file__).parent / "data" / "input" / "data_downloads.csv"
    try:
        df = pd.read_csv(path)

        download_dict = {
            "annual_data": df["annual_data"].dropna().tolist(),
            "hourly_data": df["hourly_data"].dropna().tolist()
        }

    except FileNotFoundError:
        download_dict = {
            "annual_data": [],
            "hourly_data": []
        }

    return download_dict


def export_scenario_ids(scenarios):
    path = Path(__file__).parent / "data" / "input" / "scenario_list.csv"
    scenario_list = pd.read_csv(path)

    for scenario in scenarios:
        try:
            int(scenario.id)
            id = str(scenario.id)
        except ValueError:
            id = ''

        scenario_list.loc[scenario_list["short_name"] ==
                          scenario.short_name, "id"] = id

    scenario_list.to_csv(path, index=False, header=True)


def export_scenario_queries(scenarios):
    path = Path(__file__).parent / "data" / "output" / "scenario_outcomes.csv"
    areas = []

    merged_df = pd.DataFrame()
    for i, scenario in enumerate(scenarios):
        if scenario.query_results.empty:
            pass
        else:
            short_name = scenario.short_name
            df = scenario.query_results.rename(columns={'future': short_name})
            relevant_columns = []

            if scenario.area_code not in areas:
                present = f"{scenario.area_code}_present"
                df = df.rename(columns={'present': present})
                relevant_columns.append(present)
                areas.append(scenario.area_code)

            relevant_columns.append(short_name)

            if i == len(scenarios) - 1:
                relevant_columns.append("unit")

            df = df[relevant_columns]

            merged_df = pd.concat([merged_df, df], axis=1)

    merged_df.to_csv(path, index=True, header=True)


def export_scenario_data_downloads(etm_api, short_name, download_dict):

    root = Path(__file__).parent
    output_path = root / Path(f"data/output/{short_name}")
    output_path.mkdir(parents=True, exist_ok=True)

    for download in download_dict["annual_data"]:
        df = etm_api.get_data_download(download)
        df.to_csv(f"{output_path}/{download}.csv")

    for download in download_dict["hourly_data"]:
        df = etm_api.get_data_download(download, hourly=True)
        df.to_csv(f"{output_path}/{download}.csv")


def print_ids(scenarios, model_url):
    for scenario in scenarios:
        print(f"{scenario.short_name}: {model_url}/scenarios/{scenario.id}")


def process_arguments(args):
    if len(args) > 1:
        if args[1].lower() == 'beta':
            base_url = "https://beta-engine.energytransitionmodel.com/api/v3"
            model_url = "https://beta-pro.energytransitionmodel.com"
        elif args[1].lower() == 'local':
            base_url = "http://localhost:3000/api/v3"
            model_url = "http://localhost:4000"
    else:
        base_url = "https://engine.energytransitionmodel.com/api/v3"
        model_url = "https://pro.energytransitionmodel.com"

    return base_url, model_url


if __name__ == "__main__":

    base_url, model_url = process_arguments(sys.argv)

    session = SessionWithUrlBase(base_url)

    download_dict = generate_data_download_dict()
    query_list = generate_query_list()

    scenarios = load_scenarios()

    for scenario in scenarios:

        API_scenario = ETM_API(session)
        API_scenario.initialise_scenario(scenario)

        API_scenario.update_scenario(scenario)

        API_scenario.query_scenario(scenario, query_list, download_dict)

    export_scenario_ids(scenarios)

    export_scenario_queries(scenarios)

    print_ids(scenarios, model_url)
