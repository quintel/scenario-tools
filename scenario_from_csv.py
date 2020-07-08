# external modules
import pandas as pd
from pathlib import Path

# project modules
from ETM_API import ETM_API, SessionWithUrlBase
from config import NEW_SCENARIOS as scenarios

from random import randrange

base_url = 'https://engine.energytransitionmodel.com/api/v3'
model_url = 'https://pro.energytransitionmodel.com'
session = SessionWithUrlBase(base_url)


def read_user_values():
    path = Path(__file__).parent / 'data' / 'input' / 'user_values.csv'
    df = pd.read_csv(f'{path}')

    for scenario_name, scenario_properties in scenarios.items():
        user_values = dict(zip(df['input'], df[scenario_name]))
        scenario_properties['user_values'].update(user_values)


def update_etm_user_values(ETM, scenario_name, scenario_properties):
    # Update slider user values
    ETM.change_inputs(scenario_properties['user_values'])

    # Update flexibility order
    ETM.change_flexibility_order(scenario_properties['flexibility_order'])

    # Update heat network order
    ETM.change_heat_network_order(scenario_properties['heat_network_order'])

    # Upload custom curve
    curve_type = 'interconnector_1_price'
    path = Path(__file__).parent / 'data' / 'input' / 'electricity_price.csv'

    ETM.upload_custom_curve(curve_type, path=path)

    print(f"{scenario_name}: {model_url}/scenarios/{ETM.scenario_id}")


read_user_values()

for scenario_name, scenario_properties in scenarios.items():
    if not scenario_properties['id']:
        ETM = ETM_API(session)

        protected = True

        ETM.create_new_scenario(
            scenario_properties['title'],
            scenario_properties['area_code'],
            scenario_properties['end_year'],
            scenario_properties['description'],
            protected)

        scenario_properties['id'] = ETM.scenario_id

    ETM = ETM_API(session, scenario_properties['id'])
    update_etm_user_values(ETM, scenario_name, scenario_properties)
