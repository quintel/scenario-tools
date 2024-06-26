import pandas as pd
from pathlib import Path
import yaml

from .settings import Settings
from helpers.helpers import warn, exit

def get_folder(kind):
    '''
    Kind can be input_file_folder, output_file_folder, input_curves_folder, 
    input_orders_folder, output_curves_folder, output_orders_folder
    '''
    folder_path = Path(__file__).parents[1] / Settings.get(kind) if Settings.get(kind).startswith('data') else Path(Settings.get(kind)).resolve()
    folder_path.mkdir(parents=True, exist_ok=True)
    
    return folder_path


def verify_path(path):
    if path.exists():
        return path

    exit(f'Could not find {path}, please create the folder if it does not exist.')


def read_csv(file, sep=Settings.get('csv_separator'), decimal=Settings.get('decimal_seperator'), curve=False, order=False, raises=True, silent=False, **options):
    '''Returns a pd.DataFrame'''
    path = get_folder('input_curves_folder') if curve else get_folder('input_orders_folder') if order else get_folder('input_file_folder')
    path = path / f'{file}.csv'

    if path.exists():
        if not silent: print(f' Reading {file}')
        return pd.read_csv(path, sep=sep, decimal=decimal, **options).dropna(how='all')

    text = f"File '{file}.csv' not found in '{path.parent}' folder."

    if raises:
        exit(f'{text} Aborting...')
    else:
        warn(f'{text} Skipping...')
        return pd.DataFrame()


def write_csv(df, name, folder='', sep=Settings.get('csv_separator'), decimal=Settings.get('decimal_seperator'), **options):
    path = get_folder('output_file_folder') / folder / f'{name}.csv'
    path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(path, sep=sep, decimal=decimal, **options)


def read_yml(file):
    with open('config/' + file, 'r') as f:
        doc = yaml.load(f, Loader=yaml.FullLoader)
    return doc


def check_duplicates(arr, file_name, attribute_type):
    arr_lower = [e.lower() for e in arr]
    for elem in arr_lower:
        if arr_lower.count(elem) > 1:
            exit(f"Warning! '{elem}' is included twice as a "
                  f"{attribute_type} in {file_name}. "
                  "Please remove one!")


def check_duplicate_index(df):
    '''Exits when sliders occur than once in the settings'''
    if df.index.duplicated().any():
        dups = '\n\t'.join(set(df.index[df.index.duplicated()]))
        exit("\nError: The following sliders are included more than once "
              f"in scenario_settings.csv:\n\t{dups}")


def query_list():
    '''Reads the list of requested queries from the csv'''
    df = read_csv('queries', raises=False)
    if df.empty:
        return []
    else:
        return df["query"].tolist()


def data_download_dict():
    df = read_csv('data_downloads', raises=False)
    if df.empty:
        return {}

    return {
        "annual_data": df["annual_data"].dropna().tolist(),
        "hourly_data": df["hourly_data"].dropna().tolist()
    }
