# external modules
import sys
import pandas as pd
from pathlib import Path

# project modules
from ETM_API import ETM_API, SessionWithUrlBase
from Scenario import Scenario

from random import randrange

base_url = "https://engine.energytransitionmodel.com/api/v3"
model_url = "https://pro.energytransitionmodel.com"
session = SessionWithUrlBase(base_url)

def generate_scenario_objects():
    scenarios = []

    path = Path(__file__).parent / "data" / "input" / "scenario_list.csv"
    scenario_list = pd.read_csv(path, dtype=str)

    short_names = scenario_list["short_name"]
    duplicates = scenario_list[short_names.duplicated()]["short_name"]

    if not duplicates.empty:
        print("Error: short_name must be unique for all scenarios. "
              f"Duplicates found: {duplicates.to_string(index=False)}. Aborting..")
        sys.exit()

    for idx in scenario_list.index:
        scenario = Scenario(scenario_list.iloc[idx])
        scenario.structure_orders()
        scenarios.append(scenario)

    return scenarios

def add_scenario_settings(scenarios):
    path = Path(__file__).parent / "data" / "input" / "scenario_settings.csv"
    scenario_settings = pd.read_csv(path, index_col=0, dtype=str)

    for scenario in scenarios:
        try:
            scenario.user_values = dict(scenario_settings[scenario.short_name])
        except KeyError:
            print(f"No scenario settings found for {scenario.short_name}")

    return scenarios

def load_scenarios():
    
    return add_scenario_settings(generate_scenario_objects())


def export_scenario_ids(scenarios):
    path = Path(__file__).parent / "data" / "input" / "scenario_list.csv"
    scenario_list = pd.read_csv(path)

    for scenario in scenarios:
        scenario_list.loc[scenario_list["short_name"] == scenario.short_name, "scenario_id"] = str(scenario.scenario_id)

    scenario_list.to_csv(path, index = False, header=True)

def update_etm_user_values(ETM, scenario):
    # Update slider user values
    ETM.change_inputs(scenario.user_values, scenario.short_name)

    # Update flexibility order
    ETM.change_flexibility_order(scenario.flexibility_order)

    # Update heat network order
    ETM.change_heat_network_order(scenario.heat_network_order)

    # Upload custom curve
    # curve_type = "interconnector_1_price"
    # path = Path(__file__).parent / "data" / "input" / "electricity_price.csv"

    # ETM.upload_custom_curve(curve_type, path=path)

    print(f"{scenario.short_name}: {model_url}/scenarios/{ETM.scenario_id}")

scenarios = load_scenarios()

for scenario in scenarios:
    if not scenario.scenario_id:
        ETM = ETM_API(session)

        protected = True

        ETM.create_new_scenario(
            scenario.title,
            scenario.area_code,
            scenario.end_year,
            scenario.description,
            protected)

        scenario.scenario_id = ETM.scenario_id

    export_scenario_ids(scenarios)

    ETM = ETM_API(session, scenario.scenario_id)
    
    update_etm_user_values(ETM, scenario)

