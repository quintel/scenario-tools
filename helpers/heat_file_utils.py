'''Utils for file reading/writing for heat demend'''

from helpers.file_helpers import read_csv, get_folder
from helpers.helpers import exit
from helpers.heat_demand.config import insulation_config
from helpers.Curves import Curve


def read_heat_demand_input(folder, file):
    '''
    Reads a file into a pd.Series from a folder located in data/input/curves

    Params:
        folder (str): The folder inside data/input/curves (see settings.yml)
        file (str): The target file stem, should be a csv containing a single curve of length 8760

    Returns:
        pd.Series containing the curve in the file
    '''
    curve = read_csv(f'{folder}/{file}', curve=True, silent=True,
        header=None).squeeze('columns').astype(float)

    if not curve.size == 8760:
        exit(f'Curve input {file} in {folder} should be of length 8760')

    return curve

def read_thermostat(folder):
    '''
    Reads the thermostat file into a pd.DataFrame, amd performs some checks
    '''
    therm = read_csv(f'{folder}/thermostat', curve=True, silent=True).astype(float)

    if not set(list(therm.columns)) == set(['low', 'medium', 'high']):
        exit(f'Thermostat in {folder} should be supplied for low, medium and high.')

    if not therm.shape[0] == 24:
        exit(f'Thermostat in {folder} should be supplied for 24 hours')

    return therm

def contains_heating_profiles(folder):
    '''
    Checks if all 15 heating profiles are already in the folder

    Params:
        folder (str): The folder inside data/input/curves (see settings.yml)

    Returns:
        bool
    '''
    path = get_folder('input_curves_folder') / folder
    for curve_key in insulation_config.curve_keys:
        if not (path / f'{curve_key}.csv').exists():
            return False

    return True


def read_profiles(folder):
    '''
    Reads all 15 heat profiles from the folder

    Params:
        folder (str): The folder inside data/input/curves (see settings.yml)

    Returns:
        Generator[Curve]
    '''
    for curve_key in insulation_config.curve_keys:
        yield Curve(curve_key, read_heat_demand_input(folder, curve_key))
