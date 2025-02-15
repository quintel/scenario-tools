import logging
from pathlib import Path
import pandas as pd

from helpers.file_helpers import check_duplicate_index, read_csv, check_duplicates, get_folder
from helpers.heat_demand.weather_years_profile_generator import WeatherYearsGenerator
from helpers.heat_file_utils import (contains_building_ag_profiles, load_g2a_parameters, read_building_ag_profiles, read_heat_demand_input, read_profiles,
    contains_heating_profiles, read_thermostat)
from helpers.helpers import warn
from helpers.ETM_API import ETM_API
from helpers.buildings_profile_helper import BuildingsModel
from helpers.settings import Settings



class Scenario:
    """
    Creates a scenario object, containing all relevant scenario data
    to be sent to the ETM.
    """
    ORDERS = ["heat_network_order_lt", "heat_network_order_mt", "heat_network_order_ht"]

    ATTRIBUTES = [
        "short_name",
        "id",
        "title",
        "area_code",
        "end_year",
        "description",
        "keep_compatible",
        "curve_file",
        "custom_curves",
        "flexibility_order",
        "heat_demand",
        'heat_demand_curves'
    ]

    def __init__(self, scenario_list):
        for key in self.ATTRIBUTES:
            try:
                if pd.notna(scenario_list[key]):
                    setattr(self, key, scenario_list[key])
                elif key == 'keep_compatible':
                    setattr(self, key, False)
                else:
                    setattr(self, key, None)
            except KeyError:
                setattr(self, key, None)

        self.query_results = None
        self.user_values = {}
        self.api = None
        if self.id: self.id = int(self.id)

    @property
    def heat_network_orders(self):
        return self._heat_network_orders

    @heat_network_orders.setter
    def heat_network_orders(self, value):
        self._heat_network_orders = value
        self._structure_orders()

    @heat_network_orders.getter
    def heat_network_orders(self):
        try:
            return self._heat_network_orders
        except AttributeError:
            return {}

    def _structure_orders(self):
        for order in self.ORDERS:
            current_val = self._heat_network_orders.pop(order, None)
            if not current_val == None:
                self._heat_network_orders[order.split("_")[-1]] = current_val.split(" ")

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
            'metadata': {
                'title': self.title if self.title else '',
                'description': self.description if self.description else '',
            },
            'keep_compatible': self.keep_compatible
        }

    def set_heat_demand_curves(self):
        if not self.heat_demand:
            return

        input_folder = self.heat_demand
        self.heat_demand_curves = self._check_for_heat_profiles(input_folder)
        curves_length = len(self.heat_demand_curves)

        # Initialize all variables to None
        temp = irr = wind_speed = therm = parameters = None
        if curves_length == 0:
            # Load all necessary data
            temp = self._load_heat_data(read_heat_demand_input, input_folder, 'temperature')
            irr = self._load_heat_data(read_heat_demand_input, input_folder, 'irradiation')
            wind_speed = self._load_heat_data(read_heat_demand_input, input_folder, 'wind_speed')
            therm = self._load_heat_data(read_thermostat, input_folder)
            parameters = self._load_heat_data(load_g2a_parameters, input_folder)
        elif curves_length == 12:
            # Load temperature, wind speed, and parameters only
            temp = self._load_heat_data(read_heat_demand_input, input_folder, 'temperature')
            wind_speed = self._load_heat_data(read_heat_demand_input, input_folder, 'wind_speed')
            parameters = self._load_heat_data(load_g2a_parameters, input_folder)
        elif curves_length == 2:
            # Load temperature, irradiation, and thermostat data
            temp = self._load_heat_data(read_heat_demand_input, input_folder, 'temperature')
            irr = self._load_heat_data(read_heat_demand_input, input_folder, 'irradiation')
            therm = self._load_heat_data(read_thermostat, input_folder)

        # Initialize the weather years generator with the loaded data
        generator = WeatherYearsGenerator(temp, irr, wind_speed, therm, parameters)
        new_profiles = generator.generate_all_profiles()
        for profile in new_profiles:
            self.heat_demand_curves.append(profile)

    def _load_heat_data(self, loader_function, input_folder, data_type=None, ):
        file_loc = self._determine_file_loc(loader_function, data_type, input_folder)
        if file_loc and file_loc.exists():
            try:
                if data_type is None:
                    data = loader_function(self.heat_demand)
                else:
                    data = loader_function(self.heat_demand, data_type)
                return data
            except FileNotFoundError as e:
                logging.warning(f"File not found: {e.filename}")
                return None
            except IOError as e:
                logging.warning(f"I/O error({e.errno}): {e.strerror}")
                return None
        else:
            return None

    def _determine_file_loc(self, loader_function, data_type, input_folder):
        if loader_function == read_heat_demand_input and data_type:
            filename = f"{data_type}.csv"
        elif loader_function == read_thermostat:
            filename = f"thermostat.csv"
        elif loader_function == load_g2a_parameters:
            filename = f"G2A_parameters.csv"
        else:
            logging.error(f"Unknown loader function: {loader_function}")
            return None

        curves = get_folder('input_curves_folder')
        return Path(curves, input_folder, filename)

    def _check_for_heat_profiles(self, input_folder):
        curves = []
        if contains_heating_profiles(self.heat_demand):
            print(f"Found housing heat profiles in {input_folder}, reading")
            gen = read_profiles(input_folder)
            for curve in gen:
                curves.append(curve)
        if contains_building_ag_profiles(self.heat_demand):
            print(f"Found buildings and agriculture heat profiles in {input_folder}, reading")
            gen = read_building_ag_profiles(input_folder)
            for curve in gen:
                curves.append(curve)
        return curves

    def add_results_to_df(self, df, add_present=True):
        if self.query_results is None or self.query_results.empty:
            return df

        if df.empty:
            df = self.query_results[['future', 'unit']].rename(
                columns={'future': self.short_name})
        else:
            df.loc[:, self.short_name] = self.query_results['future']

        if add_present and f'{self.area_code}_present' not in df:
            df.loc[:, f'{self.area_code}_present'] = self.query_results['present']

        return df


    def setup_connection(self, session):
        self.api = ETM_API(session, self)


    def update(self, curve_file_dict):
        '''Updates the scenario in ETM'''
        self.api.update(curve_file_dict)


    def query(self, queries):
        '''Updates the query_results'''
        self.api.query(queries)


    def get_data_downloads(self, downloads):
        yield from self.api.get_data_downloads(downloads)


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


    def add_settings_and_orders(self):
        '''Adds the user values as stated in the scenario_settings to each scenario'''
        scenario_settings = ScenarioCollection.read_settings()
        orders = ScenarioCollection.read_heat_network_orders()

        for scenario in self.collection:
            if scenario.short_name in scenario_settings:
                scenario.user_values = scenario_settings[scenario.short_name].dropna().to_dict()
            else:
                warn(f'    No scenario settings found for {scenario.short_name}')
            if scenario.short_name in orders:
                scenario.heat_network_orders = orders[scenario.short_name].dropna().to_dict()


    def setup_connections(self, session):
        '''Sets up a connection to the ETM for each scenario'''
        for scenario in self.collection:
            scenario.setup_connection(session)


    def query_all_and_export_outcomes(self, queries, target='scenario_outcomes.csv', sections={}):
        '''Queries can be list or dict shortcut to query all and export immedeately'''
        query_list = list(queries.keys()) if isinstance(queries, dict) else queries

        df = pd.DataFrame()

        for scenario in self.collection:
            scenario.query(query_list)
            df = scenario.add_results_to_df(df, add_present=False)

        unit = df.pop('unit')
        df.loc[:,'Total'] = df.sum(axis=1)
        df = df.join(unit)

        if sections:
            df.rename_axis('Subsection', inplace=True)
            df['Section'] = pd.Series(sections)

        if isinstance(queries, dict):
            df.rename(queries, axis='index', inplace=True)

        if sections:
            df.set_index('Section', append=True, inplace=True)
            df = df.reorder_levels(['Section', 'Subsection'])

        df.to_csv(get_folder('output_file_folder') / target, index=True, header=True)


    def export_scenario_outcomes(self, target='scenario_outcomes.csv'):
        '''
        Export the query results of each scenario together in one csv called 'scenario outcomes'
        '''
        df = pd.DataFrame()

        for scenario in self.collection:
            df = scenario.add_results_to_df(df)

        if not df.empty: df = df.join(df.pop('unit'))
        df.to_csv(get_folder('output_file_folder') / target, index=True, header=True)


    def export_ids(self):
        '''Write the newly generated scenario ID's to the scenario_list csv'''
        scenario_list = read_csv('scenario_list', silent=True)
        changed = False

        for scenario in self.collection:
            if not scenario.id:
                continue
            index = scenario_list['short_name'] == scenario.short_name
            scenario_list.loc[index, 'id'] = int(scenario.id)
            changed = True

        if changed:
            path = get_folder('input_file_folder') / "scenario_list.csv"
            scenario_list.to_csv(path, index=False, header=True)

    @classmethod
    def from_csv(cls, target="scenario_list"):
        '''Create a ScenarioCollection from the scenario_list csv'''
        scenarios_df = read_csv(target)

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

    @staticmethod
    def read_heat_network_orders():
        '''Returns a DataFrame of the heat network orders csv'''
        return read_csv('heat_network_orders', raises=False, index_col=0)
