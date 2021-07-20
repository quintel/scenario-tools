import sys
import pandas as pd
from pathlib import Path


def read_csv(folder, file):
    path = Path(__file__).parents[1] / f"{folder}/{file}.csv"

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


def read_scenario_list():
    print(" Reading scenario list")
    path = Path(__file__).parents[1] / "data/input"
    scenario_file = "scenario_list"

    scenario_list = read_csv(path, scenario_file)

    return scenario_list


def read_template_list():
    print(" Reading template list")
    path = Path(__file__).parents[1] / "data/input"
    template_file = "template_list"

    template_list = read_csv(path, template_file)

    return template_list


def validate_scenario_list(scenario_list):
    columns = list(scenario_list.columns.str.lower())
    short_names = [s.lower() for s in scenario_list["short_name"].tolist()]

    check_duplicates(columns, scenario_list, "column")
    check_duplicates(short_names, scenario_list, "short name")


def validate_template_list(template_list):
    ids = [s.lower() for s in template_list["id"].tolist()]

    check_duplicates(ids, template_list, "id")


def read_curve_file(file_name):
    if file_name:
        folder = Path(__file__).parents[1] / "data/input/curves"

        curve_df = read_csv(folder, file_name)

        return curve_df


def check_duplicate_scenario_settings(df):
    inputs = df.index
    duplicates = inputs[inputs.duplicated()]

    if len(duplicates) > 0:
        duplicates_output = "\n\t".join([d for d in set(duplicates)])
        print("\nError: The following sliders are included more than once "
              f"in scenario_settings.csv:\n\t{duplicates_output}")
        sys.exit()


def read_scenario_settings():
    path = Path(__file__).parents[1] / "data" / "input" / "scenario_settings.csv"
    try:
        print(" Reading scenario_settings")
        scenario_settings = pd.read_csv(
            path, index_col=0).astype('str')
        scenario_settings = scenario_settings.dropna()
        check_duplicate_scenario_settings(scenario_settings)
    except FileNotFoundError:
        print("Cannot find scenario_settings.csv file in the data/input folder")
        scenario_settings = pd.DataFrame()

    return scenario_settings


def generate_query_list():
    path = Path(__file__).parents[1] / "data" / "input" / "queries.csv"
    try:
        print(" Reading query_list")
        query_list = pd.read_csv(path)

        return query_list["query"].tolist()

    except FileNotFoundError:
        query_list = None
        print("File 'queries.csv' is missing. No query data will be collected")


def generate_data_download_dict():
    path = Path(__file__).parents[1] / "data" / "input" / "data_downloads.csv"
    try:
        print(" Reading data_downloads")
        df = pd.read_csv(path)

        download_dict = {
            "annual_data": df["annual_data"].dropna().tolist(),
            "hourly_data": df["hourly_data"].dropna().tolist()
        }

    except FileNotFoundError:
        download_dict = None

    return download_dict


def export_scenario_ids(scenarios):
    path = Path(__file__).parents[1] / "data" / "input" / "scenario_list.csv"
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
    path = Path(__file__).parents[1] / "data" / "output" / "scenario_outcomes.csv"
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


def export_template_settings(templates):
    root = Path(__file__).parents[1]
    output_path = root / Path(f"data/output")
    output_path.mkdir(parents=True, exist_ok=True)

    path = Path(__file__).parents[1] / "data" / "output" / "template_settings.csv"

    ids = []
    titles = []
    all_keys = []
    for template in templates:
        ids.append(template.id)
        titles.append(template.title)
        for input in template.user_values.keys():
            all_keys.append(input)
    cols = pd.MultiIndex.from_tuples(zip(titles, ids))
    unique_keys = list(set(all_keys))

    df = pd.DataFrame(columns=ids, index=unique_keys)

    for template in templates:
        template_id = template.id
        for input_key, val in template.user_values.items():
            df.loc[input_key, template_id] = val

    df.columns = cols
    df.to_csv(path, index=True, header=True)


def print_ids(scenarios, model_url):
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
