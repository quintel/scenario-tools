# external modules
import sys
import pandas as pd
from pathlib import Path

# project modules
from ETM_API import ETM_API, SessionWithUrlBase
from Scenario import Scenario

if len(sys.argv) > 1:
    if sys.argv[1].lower() == 'beta':
        base_url = "https://beta-engine.energytransitionmodel.com/api/v3"
        model_url = "https://beta-pro.energytransitionmodel.com"
    elif sys.argv[1].lower() == 'local':
        base_url = "http://localhost:3000/api/v3"
        model_url = "http://localhost:4000"
else:
    base_url = "https://engine.energytransitionmodel.com/api/v3"
    model_url = "https://pro.energytransitionmodel.com"

session = SessionWithUrlBase(base_url)


def generate_scenario_objects():
    scenarios = []

    path = Path(__file__).parent / "data" / "input" / "scenario_list.csv"

    try:
        scenario_list = pd.read_csv(path, dtype=str)
    except FileNotFoundError:
        print("File 'scenario_list.csv' not found in data/input folder. Aborting..")
        sys.exit(1)

    scenario_list.columns = scenario_list.columns.str.lower()
    columns = list(scenario_list.columns)

    for elem in columns:
        if columns.count(elem) > 1:
            print(f"Warning! {elem} is included twice as a column in scenario_list.csv. "
                  "Please remove one!")
            sys.exit(1)

    short_names = scenario_list["short_name"]
    duplicates = scenario_list[short_names.duplicated()]["short_name"]

    if not duplicates.empty:
        print("Error: short_name must be unique for all scenarios. "
              f"Duplicates found: {duplicates.to_string(index=False)}. Aborting..")
        sys.exit()

    for idx in scenario_list.index:
        scenario = Scenario(scenario_list.iloc[idx])
        scenario.structure_orders()
        scenarios.append(scenario)

    return scenarios


def add_scenario_settings(scenarios):
    path = Path(__file__).parent / "data" / "input" / "scenario_settings.csv"
    try:
        scenario_settings = pd.read_csv(path, index_col=0, dtype=str)
    except FileNotFoundError:
        print("Cannot find scenario_settings.csv file in the data/input folder")
        scenario_settings = pd.DataFrame()

    for scenario in scenarios:
        try:
            scenario.user_values = dict(scenario_settings[scenario.short_name])
        except KeyError:
            print(f"No scenario settings found for {scenario.short_name}")
            scenario.user_values = dict()

    return scenarios


def load_scenarios():
    return add_scenario_settings(generate_scenario_objects())


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


def update_etm_user_values(ETM, scenario):
    # Update slider user values
    ETM.change_inputs(scenario.user_values, scenario.short_name)

    # Update flexibility order
    ETM.change_flexibility_order(scenario.flexibility_order)

    # Update heat network order
    ETM.change_heat_network_order(scenario.heat_network_order)

    # Upload custom curve
    # curve_type = "interconnector_1_price"
    # path = Path(__file__).parent / "data" / "input" / "electricity_price.csv"

    # ETM.upload_custom_curve(curve_type, path=path)


def export_scenario_queries(scenarios):
    path = Path(__file__).parent / "data" / "output" / "scenario_outcomes.csv"

    merged_df = pd.DataFrame()
    for i, scenario in enumerate(scenarios):
        if scenario.query_results.empty:
            pass
        else:
            short_name = scenario.short_name
            df = scenario.query_results.rename(columns={'future': short_name})

            if i < len(scenarios)-1:
                df = df[[short_name]]
            else:
                df = df[[short_name, "unit"]]

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


download_dict = generate_data_download_dict()
scenarios = load_scenarios()

for scenario in scenarios:
    # Create scenario
    if not scenario.id:
        ETM = ETM_API(session)

        ETM.create_new_scenario(
            scenario.title,
            scenario.area_code,
            scenario.end_year)

        scenario.id = ETM.id

    ETM = ETM_API(session, scenario.id)

    # Update scenario properties
    ETM.update_scenario_properties(
        scenario.title,
        scenario.description,
        scenario.protected)

    # Update scenario settings
    update_etm_user_values(ETM, scenario)

    # Query results
    scenario.query_results = ETM.get_query_results(generate_query_list())

    # Download data exports
    export_scenario_data_downloads(ETM, scenario.short_name, download_dict)

# Write out scenario IDs
export_scenario_ids(scenarios)

# Write out query results
export_scenario_queries(scenarios)

# Print URLs
for scenario in scenarios:
    print(f"{scenario.short_name}: {model_url}/scenarios/{scenario.id}")
