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
        'user_values'
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


    def add_user_values(self, scenario_settings):
        self.user_values = scenario_settings


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
        check_duplicates(template_df['id'].tolist(), 'template', 'id')

        return cls([Template(template_data) for _, template_data in template_df.iterrows()])
