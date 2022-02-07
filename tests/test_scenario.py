
import pytest
import pandas as pd
from unittest import mock
from pathlib import Path

from helpers.settings import Settings
from helpers.Curves import Curve
from helpers.Scenario import ScenarioCollection

def test_heat_demand_in_scenario(default_scenario):
    assert default_scenario.heat_demand == 'heat_demand'
    assert not default_scenario.heat_demand_curves


def test_set_heat_demand_in_scenario(default_scenario):
    Settings.add('input_curves_folder', 'tests/fixtures/')

    default_scenario.set_heat_demand_curves()

    assert default_scenario.heat_demand_curves

    first_curve = next(default_scenario.heat_demand_curves)
    assert isinstance(first_curve, Curve)
    assert first_curve.key == 'insulation_terraced_houses_low'
    assert len(first_curve.data) == 8760


def test_collection_from_csv():
    Settings.add('input_file_folder', 'tests/fixtures/')

    collection = ScenarioCollection.from_csv()
    assert len(collection) == 1
    for scenario in collection:
        assert scenario.short_name
        assert scenario.heat_demand is None


def test_collection_export():
    Settings.add('input_file_folder', 'tests/fixtures/')
    Settings.add('output_file_folder', 'tests/fixtures/')
    collection = ScenarioCollection.from_csv()

    outcome_path = Path('tests/fixtures/scenario_outcomes.csv')

    # Without query results
    collection.export_scenario_outcomes()
    outcome = pd.read_csv(outcome_path)
    assert outcome.empty

    outcome_path.unlink()

    # With query results
    for scenario in collection:
        scenario.query_results = pd.DataFrame({'present':[2,3,4],'future': [1,2,3], 'unit': ['MW', 'MW', 'TJ']},
            index=['query_1', 'query_2', 'query_3'])

    collection.export_scenario_outcomes()
    outcome = pd.read_csv(outcome_path, index_col=0)
    assert not outcome.empty
    assert 'GM0363_amsterdam_present' in outcome.columns
    assert 'unit' in outcome.columns
    assert outcome['test_scen'].loc['query_1'] == 1

    outcome_path.unlink()
