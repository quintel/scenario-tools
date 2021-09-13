import pandas as pd

from helpers.heat_file_utils import read_heat_demand_input, read_profiles, contains_heating_profiles
from helpers.heat_demand import generate_profiles

ATTRIBUTES = [
    "short_name",
    "id",
    "title",
    "area_code",
    "end_year",
    "description",
    "protected",
    "curve_file",
    "custom_curves",
    "flexibility_order",
    "heat_network_order",
    "heat_demand",
    'heat_demand_curves'
]


class Scenario:
    """
    Creates a scenario object, containing all relevant scenario data
    to be sent to the ETM.
    """
    def __init__(self, scenario_list):
        for key in ATTRIBUTES:
            try:
                if pd.notna(scenario_list[key]):
                    setattr(self, key, scenario_list[key])
                else:
                    setattr(self, key, None)
            except KeyError:
                setattr(self, key, None)

    def structure_orders(self):
        ORDERS = [
            "flexibility_order",
            "heat_network_order"
        ]

        for order in ORDERS:
            current_val = getattr(self, order)
            if not current_val == None:
                to_list = current_val.split(" ")
                setattr(self, order, to_list)

    def add_user_values(self, scenario_settings):
        self.user_values = scenario_settings


    def set_heat_demand_curves(self):
        '''
        Checks if a heat_demand folder was supplied, and sets self.heat_demand_curves
        accordingly.

        self.heat_demand is a folder inside file_helpers.CURVE_BASE (defaulting to data/input/curves)

        self.heat_demand_curves links to a generator method, and can thus generate all 15
        heat demand curves (Curve) iteratively
        '''
        if not self.heat_demand: return

        if contains_heating_profiles(self.heat_demand):
            self.heat_demand_curves = read_profiles(self.heat_demand)

        self.heat_demand_curves = generate_profiles(
            read_heat_demand_input(self.heat_demand, 'temperature'),
            read_heat_demand_input(self.heat_demand, 'irridiation')
        )
