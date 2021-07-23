import pandas as pd

ATTRIBUTES = [
    "id",
    "title",
    "user_values"
]


class Template:
    """
    Creates a scenario template object, containing all relevant scenario data
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

    def add_user_values(self, scenario_settings):
        self.user_values = scenario_settings
