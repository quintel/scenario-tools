from helpers.heat_demand import generate_profiles
from helpers.file_helpers import read_csv

HOUSE_NAMES = [
    "terraced_houses", "corner_houses",
    "semi_detached_houses", "apartments", "detached_houses"
]

def test_generate_profiles():
    temperature = read_csv('data/input/heat_demand', 'temperature', squeeze=True, header=None).astype(float)
    irradiation = read_csv('data/input/heat_demand', 'irridiation', squeeze=True, header=None).astype(float) # J/cm^2

    counter = 0
    for curve in generate_profiles(temperature, irradiation):
        assert_curve(curve)
        counter += 1

    assert counter == 15


def assert_curve(curve):
    assert len(curve.data) == 8760
    assert abs(sum(curve.data) - 1 / 3600.0) < 1 / 1000000.0
    assert curve.key.split('_')[-1] in ['low', 'high', 'medium']
    assert '_'.join(curve.key.split('_')[1:-1]) in HOUSE_NAMES
