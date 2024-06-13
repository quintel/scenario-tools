import pandas as pd

from helpers.file_helpers import read_csv, get_folder, check_duplicates
from helpers.helpers import exit

#TODO: this is a copy of heat orders, not finished yet
class OrderFile:
    """
    Creates an object containing all the custom orders specified in an custom orders file
    in the data/input/curves folder.
    """
    def __init__(self, file_name, data_df):
        self.file_name = file_name
        self._validate(data_df)

        self.orders = set()
        self._add_orders(data_df)


    # def _validate_length(self, data_df):
    #     if len(data_df.index) != 8760:
    #         exit(f'Curves should have 8760 values. Please check {self.file_name}')


    # def _validate_types(self, data_df):
    #     # Generate series returning True for all columns of numeric type
    #     type_series = data_df.apply(
    #                     lambda s: pd.to_numeric(s, errors='coerce')
    #                     .notnull().all())
    #     # Exit if one column contains non-numeric values
    #     if not type_series.all():
    #         exit("All curves should only consist of numeric values "
    #               f"Please check {self.file_name}")


    def _validate_columns(self, data_df):
        columns = list(data_df.columns.str.lower())
        check_duplicates(columns, self.file_name, 'column')


    def _validate(self, data_df):
        # self._validate_length(data_df)
        # self._validate_types(data_df)
        self._validate_columns(data_df)


    def _add_orders(self, data_df):
        '''Create and add an Order for each column in the data_df'''
        for key, arr in data_df.iteritems():
            self.orders.add(Order(key, arr))


    @classmethod
    def from_csv(cls, file_name):
        return cls(file_name, read_csv(file_name, order=True, dtype=str))


class Order():
    """
    Creates an order object containing the specified custom orders per order type
    """
    def __init__(self, key, data):
        self.key = key
        self.data = data


    def to_csv(self, folder=''):
        '''
        Export the Curve to a csv file, if that file does not yet exist

        Params:
            folder (str): The folder in the curves folder where the curve should be written to.
                          Default '' writes straight to the curves folder (no subfolder).
        '''
        path = get_folder('input_orders_folder') / folder / f'{self.key}.csv'

        if path.exists():
            return

        pd.Series(self.data).to_csv(path, index=False, header=False)


def load_order_file_dict(scenarios):
    # TODO: move to Scenarios
    order_csvs = set([s.order_file for s in scenarios if s.order_file])

    return {file: OrderFile.from_csv(file) for file in order_csvs}
