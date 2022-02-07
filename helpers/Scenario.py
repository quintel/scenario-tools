import pandas as pd

from helpers.file_helpers import check_duplicate_index, read_csv, check_duplicates, get_folder
from helpers.heat_file_utils import (read_heat_demand_input, read_profiles,
    contains_heating_profiles, read_thermostat)
from helpers.heat_demand import generate_profiles
from helpers.helpers import warn

class Scenario:
    """
    Creates a scenario object, containing all relevant scenario data
    to be sent to the ETM.
    """
    ORDERS = ["heat_network_order"]

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

    def __init__(self, scenario_list):
        for key in self.ATTRIBUTES:
            try:
                if pd.notna(scenario_list[key]):
                    setattr(self, key, scenario_list[key])
                elif key == 'protected':
                    setattr(self, key, False)
                else:
                    setattr(self, key, None)
            except KeyError:
                setattr(self, key, None)

        self._structure_orders()
        self.query_results = None
        self.user_values = {}
        if self.id: self.id = int(self.id)


    def _structure_orders(self):
        for order in self.ORDERS:
            current_val = getattr(self, order)
            if not current_val == None:
                to_list = current_val.split(" ")
                setattr(self, order, to_list)


    def add_user_values(self, scenario_settings):
        self.user_values = scenario_settings


    def create_params_as_json(self):
        '''Returns the basic scenario parameters as json'''
        return {
                "title": self.title,
                "area_code": self.area_code,
                "end_year": self.end_year
            }


    def properties_as_json(self):
        '''
        Returns the scenario properties settings, like description, title, and protection status
        '''
        return {
            'title': self.title if self.title else '',
            'description': self.description if self.description else '',
            'protected': self.protected
        }


    def set_heat_demand_curves(self):
        '''
        Checks if a heat_demand folder was supplied, and sets self.heat_demand_curves
        accordingly.

        self.heat_demand is a folder inside the input curves folder

        self.heat_demand_curves links to a generator method, and can thus generate all 15
        heat demand curves (Curve) iteratively
        '''
        if not self.heat_demand: return

        elif contains_heating_profiles(self.heat_demand):
            self.heat_demand_curves = read_profiles(self.heat_demand)

        else:
            self.heat_demand_curves = generate_profiles(
                read_heat_demand_input(self.heat_demand, 'temperature'),
                read_heat_demand_input(self.heat_demand, 'irradiation'),
                read_thermostat(self.heat_demand)
            )


class ScenarioCollection:
    def __init__(self, collection):
        self.collection = collection


    def __iter__(self):
        yield from self.collection


    def __len__(self):
        return len(self.collection)


    def filter_query_only(self):
        '''Reduce collection to only hold scenarios with an id'''
        self.collection = [scenario for scenario in self.collection if scenario.id]


    def print_urls(self, model_url):
        '''Print a url for each scenario'''
        for scenario in self.collection:
            print(f"{scenario.short_name}: {model_url}/scenarios/{scenario.id}")


    def add_settings(self):
        '''Adds the user values as stated in the scenario_settings to each scenario'''
        scenario_settings = ScenarioCollection.read_settings()

        for scenario in self.collection:
            if scenario.short_name in scenario_settings:
                scenario.user_values = scenario_settings[scenario.short_name].dropna().to_dict()
            else:
                warn(f'    No scenario settings found for {scenario.short_name}')


    def export_scenario_outcomes(self):
        '''
        Export the query results of each scenario together in one csv called 'scenario outcomes'
        '''
        df = pd.DataFrame()

        for scenario in self.collection:
            if scenario.query_results is None or scenario.query_results.empty:
                continue

            if df.empty:
                df = scenario.query_results[['future', 'unit']].rename(
                    columns={'future': scenario.short_name})
            else:
                df.loc[:, scenario.short_name] = scenario.query_results['future']

            if f'{scenario.area_code}_present' not in df:
                df.loc[:, f'{scenario.area_code}_present'] = scenario.query_results['present']

        df.to_csv(get_folder('output_file_folder') / 'scenario_outcomes.csv', index=True,
            header=True)


    def export_ids(self):
        '''Write the newly generated scenario ID's to the scenario_list csv'''
        scenario_list = read_csv('scenario_list', silent=True)
        changed = False

        for scenario in self.collection:
            if not scenario.id:
                continue
            index = scenario_list['short_name'] == scenario.short_name
            scenario_list.loc[index, 'id'] = str(scenario.id)
            changed = True

        if changed:
            path = get_folder('input_file_folder') / "scenario_list.csv"
            scenario_list.to_csv(path, index=False, header=True)


    @classmethod
    def from_csv(cls):
        '''Create a ScenarioCollection from the scenario_list csv'''
        scenarios_df = read_csv("scenario_list")

        # Validate
        check_duplicates(scenarios_df.columns.tolist(), 'scenario_list', "column")
        check_duplicates(scenarios_df['short_name'].astype('str').tolist(), 'scenario_list', "short name")

        return cls([Scenario(scenario_data) for _, scenario_data in scenarios_df.iterrows()])


    @staticmethod
    def read_settings():
        '''Returns a DataFrame of the scenario settings csv'''
        settings = read_csv('scenario_settings', raises=False, index_col=0)
        check_duplicate_index(settings)

        return settings
