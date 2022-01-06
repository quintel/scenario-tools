'''Tests for the ETM_API class'''

import pytest
from unittest import mock
from pathlib import Path

from helpers.ETM_API import SessionWithUrlBase, ETM_API
from helpers.Curves import Curve
from helpers.settings import Settings
from helpers.heat_demand.config import insulation_config

### FIXTURES & HELPERS & CONSTANTS ###

BASE_URL = 'http://fake.session'


@pytest.fixture
def default_api():
    '''
    Uses base_url http://fake.session

    Returns:
        ETM_API
    '''
    return ETM_API(SessionWithUrlBase(BASE_URL))


@pytest.fixture
def heat_curve_keys():
    return insulation_config.curve_keys


def mock_etm_response(requests_mock, endpoint='/scenarios/', resp=[], status_code=200):
    '''Mocks an etm request'''
    requests_mock.put(
        BASE_URL + endpoint,
        json=resp,
        status_code=status_code
    )


### TESTS ###

def test_update_scenario_with_heat_demand(default_api, default_scenario, requests_mock,
    heat_curve_keys):
    Settings.add('input_curves_folder', 'tests/fixtures/')

    default_scenario.id = 12345
    default_api.initialise_scenario(default_scenario)
    default_scenario.heat_demand_curves = (Curve(key, 8760*[0]) for key in heat_curve_keys)

    # Discard all things to be updated but heat_demand
    for setting in ['user_values', 'flexibility_order', 'heat_network_order', 'curve_file']:
        setattr(default_scenario, setting, None)

    # Mock basic scenarios endpoint and custom curves endpoint to be succesful
    mock_etm_response(requests_mock, endpoint=f'/scenarios/{default_scenario.id}')
    for curve_key in heat_curve_keys:
        mock_etm_response(
            requests_mock,
            endpoint=f'/scenarios/{default_scenario.id}/custom_curves/weather/{curve_key}'
        )

    # No errors thrown
    default_api.update_scenario(default_scenario, {})

    # Cleanup curves that were written
    for file in Path('tests/fixtures/heat_demand').glob('insulation_*.csv'):
        file.unlink()


def test_update_scenario_with_missing_heat_demand_curves(default_api, default_scenario, requests_mock):
    Settings.add('input_curves_folder', 'tests/fixtures/')

    default_scenario.id = 12345
    default_api.initialise_scenario(default_scenario)

    # No heat demand curves were set
    default_scenario.heat_demand_curves = None

    # Discard all things to be updated but heat_demand
    for setting in ['user_values', 'flexibility_order', 'heat_network_order', 'curve_file']:
        setattr(default_scenario, setting, None)

    # Mock basic scenarios endpoint
    mock_etm_response(requests_mock, endpoint=f'/scenarios/{default_scenario.id}')

    # No errors thrown
    default_api.update_scenario(default_scenario, {})


def test_update_scenario_with_heat_demand_curves_with_angry_engine(default_api, default_scenario, requests_mock,
    heat_curve_keys):
    Settings.add('input_curves_folder', 'tests/fixtures/')

    default_scenario.id = 12345
    default_api.initialise_scenario(default_scenario)
    default_scenario.heat_demand_curves = (Curve(key, 8760*[0]) for key in heat_curve_keys)

    # Discard all things to be updated but heat_demand
    for setting in ['user_values', 'flexibility_order', 'heat_network_order', 'curve_file']:
        setattr(default_scenario, setting, None)

    # Mock basic scenarios endpoint and custom curves endpoint to be succesful
    mock_etm_response(requests_mock, endpoint=f'/scenarios/{default_scenario.id}')
    for curve_key in heat_curve_keys:
        mock_etm_response(
            requests_mock,
            endpoint=f'/scenarios/{default_scenario.id}/custom_curves/weather/{curve_key}',
            resp={'errors': [f'No such custom curve: {curve_key}']},
            status_code=422
        )

    # Should fail
    with pytest.raises(SystemExit):
        default_api.update_scenario(default_scenario, {})

    # Cleanup curves that were written
    for file in Path('tests/fixtures/heat_demand').glob('insulation_*.csv'):
        file.unlink()
