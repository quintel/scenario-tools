# system modules
import os

# external modules
import pandas as pd
from pathlib import Path

# project modules
from ETM_API import ETM_API, SessionWithUrlBase
from config import EXISTING_SCENARIOS as scenarios

base_url = 'https://engine.energytransitionmodel.com/api/v3'
model_url = 'https://pro.energytransitionmodel.com'
session = SessionWithUrlBase(base_url)


def export_energy_flows(ETM, scenario_name, scenario_properties):
    flows = ETM.get_energy_flows()

    path = Path(__file__).parent / 'data' / 'output' / f'{ETM.scenario_id}_{scenario_name}' / f'energy_flow.{ETM.scenario_id}.csv'

    # Create file/folders if non-existent
    os.makedirs(os.path.dirname(path), exist_ok=True)

    flows.to_csv(path, index=False)


def export_application_demands(ETM, scenario_name, scenario_properties):
    demands = ETM.get_application_demands()

    path = Path(__file__).parent / 'data' / 'output' / f'{ETM.scenario_id}_{scenario_name}' / f'application_demands.{ETM.scenario_id}.csv'

    # Create file/folders if non-existent
    os.makedirs(os.path.dirname(path), exist_ok=True)

    demands.to_csv(path, index=False)


def export_production_parameters(ETM, scenario_name, scenario_properties):
    params = ETM.get_production_parameters()

    path = Path(__file__).parent / 'data' / 'output' / f'{ETM.scenario_id}_{scenario_name}' / f'production_parameters.{ETM.scenario_id}.csv'

    # Create file/folders if non-existent
    os.makedirs(os.path.dirname(path), exist_ok=True)

    params.to_csv(path, index=False)


def export_electricity_curves(ETM, scenario_name, scenario_properties):
    curves = ETM.get_hourly_electricity_curves()

    path = Path(__file__).parent / 'data' / 'output' / f'{ETM.scenario_id}_{scenario_name}' / f'merit_order.{ETM.scenario_id}.csv'

    # Create file/folders if non-existent
    os.makedirs(os.path.dirname(path), exist_ok=True)

    curves.to_csv(path, index=False)


def export_electricity_price_curve(ETM, scenario_name, scenario_properties):
    curve = ETM.get_hourly_electricity_price_curve()

    path = Path(__file__).parent / 'data' / 'output' / f'{ETM.scenario_id}_{scenario_name}' / f'electricity_price_curve.{ETM.scenario_id}.csv'

    # Create file/folders if non-existent
    os.makedirs(os.path.dirname(path), exist_ok=True)

    curve.to_csv(path, index=False)


def export_household_heat_curves(ETM, scenario_name, scenario_properties):
    curves = ETM.get_hourly_household_heat_curves()

    path = Path(__file__).parent / 'data' / 'output' / f'{ETM.scenario_id}_{scenario_name}' / f'household_heat.{ETM.scenario_id}.csv'

    # Create file/folders if non-existent
    os.makedirs(os.path.dirname(path), exist_ok=True)

    curves.to_csv(path, index=False)


def export_gas_curves(ETM, scenario_name, scenario_properties):
    curves = ETM.get_hourly_gas_curves()

    path = Path(__file__).parent / 'data' / 'output' / f'{ETM.scenario_id}_{scenario_name}' / f'network_gas.{ETM.scenario_id}.csv'

    # Create file/folders if non-existent
    os.makedirs(os.path.dirname(path), exist_ok=True)

    curves.to_csv(path, index=False)


def export_hydrogen_curves(ETM, scenario_name, scenario_properties):
    curves = ETM.get_hourly_hydrogen_curves()

    path = Path(__file__).parent / 'data' / 'output' / f'{ETM.scenario_id}_{scenario_name}' / f'hydrogen.{ETM.scenario_id}.csv'

    # Create file/folders if non-existent
    os.makedirs(os.path.dirname(path), exist_ok=True)

    curves.to_csv(path, index=False)


def export_heat_network_curves(ETM, scenario_name, scenario_properties):
    curves = ETM.get_hourly_heat_network_curves()

    path = Path(__file__).parent / 'data' / 'output' / f'{ETM.scenario_id}_{scenario_name}' / f'heat_network.{ETM.scenario_id}.csv'

    # Create file/folders if non-existent
    os.makedirs(os.path.dirname(path), exist_ok=True)

    curves.to_csv(path, index=False)


for scenario_name, scenario_properties in scenarios.items():
    if not scenario_properties['id']:
        ETM = ETM_API(session)

        ETM.create_new_scenario(
            scenario_properties['title'],
            scenario_properties['area_code'],
            scenario_properties['end_year'])

        scenario_properties['id'] = ETM.scenario_id

    ETM = ETM_API(session, scenario_properties['id'])

#    export_energy_flows(ETM, scenario_name, scenario_properties)
    export_application_demands(ETM, scenario_name, scenario_properties)
    export_production_parameters(ETM, scenario_name, scenario_properties)
    # export_electricity_curves(ETM, scenario_name, scenario_properties)
    # export_electricity_price_curve(ETM, scenario_name, scenario_properties)
    # export_household_heat_curves(ETM, scenario_name, scenario_properties)
    # export_gas_curves(ETM, scenario_name, scenario_properties)
    # export_hydrogen_curves(ETM, scenario_name, scenario_properties)
    # export_heat_network_curves(ETM, scenario_name, scenario_properties)
