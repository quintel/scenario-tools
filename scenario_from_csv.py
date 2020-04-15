# external modules
import pandas as pd
from pathlib import Path

# project modules
from ETM_API import ETM_API, SessionWithUrlBase
from config import SCENARIOS

base_url = 'https://engine.energytransitionmodel.com/api/v3'
model_url = 'https://pro.energytransitionmodel.com'
session = SessionWithUrlBase(base_url)


def read_user_values():
    path = Path(__file__).parent / 'data' / 'input' / 'user_values.csv'
    df = pd.read_csv(f'{path}')

    for scenario_name, scenario_properties in SCENARIOS.items():
        user_values = dict(zip(df['input'], df[scenario_name]))
        scenario_properties['user_values'].update(user_values)


def update_etm_user_values(ETM, scenario_name, scenario_properties):
    ETM.change_inputs(scenario_properties['user_values'])

    print(f"{scenario_name}: {model_url}/scenarios/{ETM.scenario_id}")


def export_electricity_curves(ETM, scenario_name, scenario_properties):
    curves = ETM.get_hourly_electricity_curves()

    path = Path(__file__).parent / 'data' / 'output' / f'merit_order.{ETM.scenario_id}.csv'
    curves.to_csv(path, index=False)


read_user_values()

for scenario_name, scenario_properties in SCENARIOS.items():
    if not scenario_properties['id']:
        ETM = ETM_API(session)

        ETM.create_new_scenario(
            scenario_properties['title'],
            scenario_properties['area_code'],
            scenario_properties['end_year'])

        scenario_properties['id'] = ETM.scenario_id

    ETM = ETM_API(session, scenario_properties['id'])
    update_etm_user_values(ETM, scenario_name, scenario_properties)
    export_electricity_curves(ETM, scenario_name, scenario_properties)
