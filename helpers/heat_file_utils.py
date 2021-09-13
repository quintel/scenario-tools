'''Utils for file reading/writing for heat demend'''

from pathlib import Path

from helpers.file_helpers import read_csv, CURVE_BASE
from helpers.heat_demand.config import insulation_config
from helpers.Curves import Curve


def read_heat_demand_input(folder, file):
    '''
    Reads a file into a pd.Series from a folder located in data/input/curves

    Params:
        folder (str): The folder inside data/input/curves (CURVE_BASE)
        file (str): The target file stem, should be a csv containing a single curve of length 8760

    Returns:
        pd.Series containing the curve in the file
    '''
    curve = read_csv(CURVE_BASE + folder, file, squeeze=True, header=None).astype(float)

    if not curve.size == 8760:
        raise ValueError(f'Curve input {file} in {folder} should be of length 8760')

    return curve


def contains_heating_profiles(folder):
    '''
    Checks if all 15 heating profiles are already in the folder

    Params:
        folder (str): The folder inside data/input/curves (CURVE_BASE)

    Returns:
        bool
    '''
    path = Path(__file__).parents[1] / CURVE_BASE / folder
    for curve_key in insulation_config.curve_keys:
        if not (path / f'{curve_key}.csv').exists():
            return False

    return True


def read_profiles(folder):
    '''
    Reads all 15 heat profiles from the folder

    Params:
        folder (str): The folder inside data/input/curves (CURVE_BASE)

    Returns:
        Generator[Curve]
    '''
    for curve_key in insulation_config.curve_keys:
        yield Curve(curve_key, read_heat_demand_input(folder, curve_key))
