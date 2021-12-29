import sys
import pandas as pd
from pathlib import Path
from .settings import Settings

def get_folder(kind):
    '''kind can be input_file_folder, output_file_folder or input_curves_folder'''
    if Settings.get(kind).startswith('data'):
        return Path(__file__).parents[1] / Settings.get(kind)

    return verify_path(Path(Settings.get(kind)).resolve())


def verify_path(path):
    if path.exists():
        return path

    print(f'Could not find {path}, please create the folder if it does not exist.')
    sys.exit()


def read_csv(file, curve=False, **options):
    '''Returns a pd.DataFrame with datatype string'''
    path = get_folder('input_file_folder') if not curve else get_folder('input_curves_folder')
    path = path / f'{file}.csv'

    if path.exists():
        return pd.read_csv(path, dtype=str, **options)

    print(f"File '{file}.csv' not found in '{get_folder('input_file_folder')}' folder. Aborting..")
    sys.exit(1)


def check_duplicates(arr, file_name, attribute_type):
    arr_lower = [e.lower() for e in arr]
    for elem in arr_lower:
        if arr_lower.count(elem) > 1:
            print(f"Warning! '{elem}' is included twice as a "
                  f"{attribute_type} in {file_name}. "
                  "Please remove one!")
            sys.exit(1)


def validate_scenario_settings(df):
    '''Exits when sliders occur than once in the settings'''
    if df.index.duplicated().any():
        dups = '\n\t'.join(set(df.index[df.index.duplicated()]))
        print("\nError: The following sliders are included more than once "
              f"in scenario_settings.csv:\n\t{dups}")
        sys.exit()


def read_scenario_settings():
    '''Returns a prepped pd.Dataframe containing the scenario setings from the csv'''
    file = get_folder('input_file_folder') / "scenario_settings.csv"

    if file.exists():
        print(" Reading scenario_settings")
        scenario_settings = pd.read_csv(file, index_col=0).astype('str').dropna()
        validate_scenario_settings(scenario_settings)
    else:
        print("Cannot find scenario_settings.csv file in the input folder")
        scenario_settings = pd.DataFrame()

    return scenario_settings


def generate_query_list():
    '''Reads the list of requested queries from the csv'''
    file = get_folder('input_file_folder') / "queries.csv"

    if file.exists():
        return pd.read_csv(file)["query"].tolist()
    else:
        print("File 'queries.csv' is missing. No query data will be collected")
        return []


def generate_data_download_dict():
    file = get_folder('input_file_folder') / "data_downloads.csv"

    if not file.exists():
        return {}

    print(" Reading data_downloads")
    df = pd.read_csv(file)
    download_dict = {
        "annual_data": df["annual_data"].dropna().tolist(),
        "hourly_data": df["hourly_data"].dropna().tolist()
    }

    return download_dict


def export_scenario_ids(scenarios):
    # TODO: check issue on this + move to Scenarios
    path = get_folder('input_file_folder') / "scenario_list.csv"
    scenario_list = pd.read_csv(path)

    for scenario in scenarios:
        try:
            int(scenario.id)
            id = str(scenario.id)
        except ValueError:
            id = ''

        scenario_list.loc[scenario_list["short_name"] == scenario.short_name, "id"] = id

    scenario_list.to_csv(path, index=False, header=True)
