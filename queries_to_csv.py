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


def read_queries():
    path = Path(__file__).parent / 'data' / 'input' / 'gqueries.csv'
    df = pd.read_csv(f'{path}')

    return list(df['gquery'])


def export_metrics(ETM, scenario_name, queries):
    metrics = ETM.get_current_metrics(queries)

    path = Path(__file__).parent / 'data' / 'output' / f'{ETM.scenario_id}_{scenario_name}' / f'queries.{ETM.scenario_id}.csv'

    # Create file/folders if non-existent
    os.makedirs(os.path.dirname(path), exist_ok=True)

    metrics.to_csv(path, index=True)


queries = read_queries()

for scenario_name, scenario_properties in scenarios.items():
    if not scenario_properties['id']:
        ETM = ETM_API(session)

        ETM.create_new_scenario(
            scenario_properties['title'],
            scenario_properties['area_code'],
            scenario_properties['end_year'])

        scenario_properties['id'] = ETM.scenario_id

    ETM = ETM_API(session, scenario_properties['id'])
    export_metrics(ETM, scenario_name, queries)
