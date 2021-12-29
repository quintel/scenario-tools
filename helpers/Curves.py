import sys
import pandas as pd
from pathlib import Path
from helpers.file_helpers import get_folder, check_duplicates


class CurveFile:
    """
    Creates an object containing all the curves specified in a curve file
    in the data/input/curves folder.
    """
    def __init__(self, file_name, data_df):
        self.file_name = file_name
        self._validate(data_df)

        self.curves = set()
        self._add_curves(data_df)


    def _validate_length(self, data_df):
        if len(data_df.index) != 8760:
            print(f'Curves should have 8760 values. Please check {self.file_name}')
            sys.exit(1)


    def _validate_types(self, data_df):
        # Generate series returning True for all columns of numeric type
        type_series = data_df.apply(
                        lambda s: pd.to_numeric(s, errors='coerce')
                        .notnull().all())
        # Exit if one column contains non-numeric values
        if not type_series.all():
            print("All curves should only consist of numeric values "
                  f"Please check {self.file_name}")
            sys.exit(1)


    def _validate_columns(self, data_df):
        columns = list(data_df.columns.str.lower())
        check_duplicates(columns, self.file_name, 'column')


    def _validate(self, data_df):
        self._validate_length(data_df)
        self._validate_types(data_df)
        self._validate_columns(data_df)


    def _add_curves(self, data_df):
        '''Create and add a Curve for each column in the data_df'''
        for key, arr in data_df.iteritems():
            self.curves.add(Curve(key, arr))


    @classmethod
    def from_csv(cls, file_name):
        file = get_folder('input_curves_folder') / f'{file_name}.csv'
        if not file.exists():
            print(f'Curve {file} was not found. Exiting...')
            sys.exit()

        return cls(file_name, pd.read_csv(file, dtype=str))


class Curve():
    """
    Creates a curve object containing the (hourly) data points of a custom curve
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
        path = get_folder('input_curves_folder') / folder / f'{self.key}.csv'

        if path.exists():
            return

        pd.Series(self.data).to_csv(path, index=False, header=False)


