'''
Runs during test collection. You can also supply fixtures here that should be loaded
before each test
'''
from os import sys, path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import pytest
import pandas as pd
from helpers.Scenario import Scenario

@pytest.fixture
def default_scenario(test_data=None):
    '''
    Returns a default Scenario. You can supply other test data if you want
    '''
    index = [
        'short_name','title','area_code','end_year',
        'description','id','keep_compatible','flexibility_order',
        'heat_network_order','curve_file','heat_demand'
    ]
    test_data = test_data if test_data else [
        'test_scen',
        'Scenario-Tools Test Scenario',
        'GM0363_amsterdam',
        2050,
        "Scenario created by DfE and SONI.",
        835167,
        '',
        'opac mv_batteries',
        'energy_heat_burner_waste_mix energy_heat_burner_network_gas',
        '2050_price_curves',
        'heat_demand'
    ]

    return Scenario(pd.Series(test_data, index=index))
