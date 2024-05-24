import pandas as pd
from pathlib import Path
from helpers.file_helpers import read_csv, check_duplicates, get_folder
from helpers import curves_lst

class Template:
    """
    Creates a scenario template object, containing all relevant scenario data
    to be sent to the ETM.
    """
    ATTRIBUTES = [
        'id',
        'title',
        'user_values'
    ]
#TODO: create one function for obtaining order csv
    ORDERS = [
        'heat_network_order_ht',
        'heat_network_order_mt',
        'heat_network_order_lt',
        'hydrogen_supply_order',
        'hydrogen_demand_order',
        'forecasting_storage_order',
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


    def add_user_values(self, scenario_settings):
        self.user_values = scenario_settings
    

    def add_custom_curves(self, custom_curves):
        setattr(self, 'custom_curves', custom_curves)


    def add_heat_network_orders(self, heat_network_order, subtype):
        setattr(self, f'heat_network_order_{subtype}', heat_network_order)
        return heat_network_order
    

    def add_hydrogen_orders(self, hydrogen_order, subtype):
        setattr(self, f'hydrogen_{subtype}_order', hydrogen_order)
        return hydrogen_order
    

    def add_forecasting_storage_order(self, forecasting_storage_order):
        setattr(self, 'forecasting_storage_order', forecasting_storage_order)
        return forecasting_storage_order
    

    def add_households_space_heating_producer_order(self, households_space_heating_producer_order):
        setattr(self, 'households_space_heating_producer_order', households_space_heating_producer_order)
        return households_space_heating_producer_order
    

    def get_hydrogen_orders_csv(self, subtypes):
        column_names = [f'hydrogen_{t}_order' for t in subtypes]
        df = pd.DataFrame(columns = column_names)
        for t in subtypes:
            order_attr = f'hydrogen_{t}_order'
            order_string = " ".join(getattr(self, order_attr)['Order'])
            df[order_attr] = [order_string]
        print(df)
        return df
    

    def get_heat_network_orders_csv(self, heat_levels):
        column_names = [f'heat_network_order_{l}' for l in heat_levels]
        df = pd.DataFrame(columns = column_names)
        for l in heat_levels:
            order_attr = f'heat_network_order_{l}'
            order_string = " ".join(getattr(self, order_attr)['Order'])
            df[order_attr] = [order_string]
        print(df)
        return df
    
    def get_forecasting_storage_order_csv(self):
        df = pd.DataFrame(columns = ['forecasting_storage_order'])
        order_string = " ".join(self.forecasting_storage_order['Order'])
        df['forecasting_storage_order'] = [order_string]
        return df


    def get_households_space_heating_producer_order_csv(self):
        df = pd.DataFrame(columns = ['households_space_heating_producer_order'])
        order_string = " ".join(self.households_space_heating_producer_order['Order'])
        df['households_space_heating_producer_order'] = [order_string]
        return df



class TemplateCollection:
    '''Collection of Templates'''
    def __init__(self, collection):
        self.collection = collection


    def __iter__(self):
        yield from self.collection


    def to_csv(self):
        '''Exports the templates to csv'''
        ids = []
        titles = []
        all_keys = []
        for template in self.collection:
            ids.append(template.id)
            titles.append(template.title)
            for input in template.user_values.keys():
                all_keys.append(input)
        cols = pd.MultiIndex.from_tuples(zip(titles, ids))
        unique_keys = list(set(all_keys))

        df = pd.DataFrame(columns=ids, index=unique_keys)

        for template in self.collection:
            template_id = template.id
            for input_key, val in template.user_values.items():
                df.loc[input_key, template_id] = val

        df.columns = cols
        df.to_csv(get_folder('output_file_folder') / 'template_settings.csv', index=True,
            header=True)


    @classmethod
    def from_csv(cls):
        '''
        Reads the template csv into a df, does validation, and creates a Template for each row.

        Returns a new TemplateCollection containing the Templates
        '''
        template_df = read_csv('template_list')
        check_duplicates(template_df['id'].astype('str').tolist(), 'template', 'id')

        return cls([Template(template_data) for _, template_data in template_df.iterrows()])
