from unittest import mock

from helpers.heat_demand import generate_profiles
from helpers.file_helpers import read_csv
from helpers.heat_file_utils import read_heat_demand_input
from helpers.settings import Settings

HOUSE_NAMES = [
    "terraced_houses", "corner_houses",
    "semi_detached_houses", "apartments", "detached_houses"
]

def test_generate_profiles():
    # Patch settings
    Settings.add('input_curves_folder', 'tests/fixtures/')

    temperature = read_heat_demand_input('heat_demand', 'temperature')
    irradiation = read_heat_demand_input('heat_demand',  'irradiation') # J/cm^2
    thermostat = read_csv('heat_demand/thermostat', curve=True).astype(float)

    counter = 0
    for curve in generate_profiles(temperature, irradiation, thermostat):
        assert_curve(curve)
        counter += 1

    assert counter == 15


def assert_curve(curve):
    assert len(curve.data) == 8760
    assert abs(sum(curve.data) - 1 / 3600.0) < 1 / 1000000.0
    assert curve.key.split('_')[-1] in ['low', 'high', 'medium']
    assert '_'.join(curve.key.split('_')[1:-1]) in HOUSE_NAMES
