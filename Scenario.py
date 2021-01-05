import pandas as pd

ATTRIBUTES = [
    "short_name",
    "id",
    "title",
    "area_code",
    "end_year",
    "description",
    "protected",
    "flexibility_order",
    "heat_network_order",
]


class Scenario:

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

    def add_user_values(self, user_values):
        self.user_values = user_values

    def to_dict(self):
        parameters = {}
        for key in ATTRIBUTES:
            parameters[key] = getattr(self, key)

        return parameters
