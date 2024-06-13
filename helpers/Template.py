import pandas as pd
from pathlib import Path
from helpers.file_helpers import read_csv, check_duplicates, get_folder

class Template:
    """
    Creates a scenario template object, containing all relevant scenario data
    to be sent to the ETM.
    """
    ATTRIBUTES = [
        'id',
        'title',
        'user_values',
        'balanced_values'
    ]

    HEAT_ORDERS = [
        "heat_network_order_lt", 
        "heat_network_order_mt", 
        "heat_network_order_ht"
    ]

    CUSTOM_ORDERS = [
        'hydrogen_supply_order',
        'hydrogen_demand_order',
        'forecast_storage_order',
        'households_space_heating_producer_order'
    ]

    def __init__(self, scenario_row):
        for key in self.ATTRIBUTES:
            try:
                if pd.notna(scenario_row[key]):
                    setattr(self, key, scenario_row[key])
                else:
                    setattr(self, key, None)
            except KeyError:
                setattr(self, key, None)

        self.id = int(self.id)
        self.heat_orders = self.HEAT_ORDERS
        self.custom_orders = self.CUSTOM_ORDERS


    def add_user_values(self, scenario_settings):
        self.user_values = scenario_settings

    
    def add_balanced_values(self, scenario_settings_balanced_values):
        self.balanced_values = scenario_settings_balanced_values
    

    def add_custom_curves(self, custom_curves):
        setattr(self, 'custom_curves', custom_curves)


    def custom_curves_to_csv(self):
        if not self.custom_curves.empty:
            self.custom_curves.to_csv(get_folder('output_curves_folder') / f'{self.title}_custom_curves.csv', index=False)
        else:
            print("No custom curves uploaded for this scenario.")


    def add_custom_orders(self, custom_orders):
        setattr(self, 'custom_orders', custom_orders)


    def custom_orders_to_csv(self):
        if not self.custom_orders.empty:
            self.custom_orders.to_csv(get_folder('output_orders_folder') / f'{self.title}_custom_orders.csv', index=False)
        else:
            print("No custom orders uploaded for this scenario.")
        
        
    def add_heat_network_orders(self, heat_network_orders):
        heat_network_orders = heat_network_orders.rename(columns={0: self.title})
        setattr(self, 'heat_network_orders', heat_network_orders)


class TemplateCollection:
    '''Collection of Templates'''
    def __init__(self, collection):
        self.collection = collection


    def __iter__(self):
        yield from self.collection


    def to_csv(self, file_name, user_values=True):
        '''Exports the templates to csv'''
        ids = []
        titles = []
        all_keys = []
        for template in self.collection:
            value_attribute_dict = template.user_values if user_values else template.balanced_values
            ids.append(template.id)
            titles.append(template.title)
            for input in value_attribute_dict.keys():
                all_keys.append(input)
        cols = pd.MultiIndex.from_tuples(zip(titles, ids))
        unique_keys = list(set(all_keys))

        df = pd.DataFrame(columns=ids, index=unique_keys)
        for template in self.collection:
            value_attribute_dict = template.user_values if user_values else template.balanced_values
            template_id = template.id
            for input_key, val in value_attribute_dict.items():
                df.loc[input_key, template_id] = val

        df.columns = cols
        df.to_csv(get_folder('output_file_folder') / f'{file_name}.csv', index=True,
            header=True)

    def heat_network_orders_to_csv(self):
        '''Exports the heat network orders to csv'''
        df = pd.DataFrame(index=[f'heat_network_order_{t}' for t in ['lt','mt','ht']])
        for template in self.collection:
            df = pd.concat([df, template.heat_network_orders], axis=1)
        df.index.names = ['order']
        df.to_csv(get_folder('output_orders_folder') / 'heat_network_orders.csv', index=True)


    @classmethod
    def from_csv(cls):
        '''
        Reads the template csv into a df, does validation, and creates a Template for each row.

        Returns a new TemplateCollection containing the Templates
        '''
        template_df = read_csv('template_list')
        check_duplicates(template_df['id'].astype('str').tolist(), 'template', 'id')

        return cls([Template(template_data) for _, template_data in template_df.iterrows()])
