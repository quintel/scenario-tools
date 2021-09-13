
import pytest
import pandas as pd
from unittest import mock

import helpers.file_helpers
from helpers.Curves import Curve

def test_heat_demand_in_scenario(default_scenario):
    assert default_scenario.heat_demand == 'heat_demand'
    assert not default_scenario.heat_demand_curves

@mock.patch("helpers.heat_file_utils.CURVE_BASE", 'tests/fixtures/')
def test_set_heat_demand_in_scenario(default_scenario):
    default_scenario.set_heat_demand_curves()

    assert default_scenario.heat_demand_curves

    first_curve = next(default_scenario.heat_demand_curves)
    assert isinstance(first_curve, Curve)
    assert first_curve.key == 'insulation_terraced_houses_low'
    assert len(first_curve.data) == 8760
