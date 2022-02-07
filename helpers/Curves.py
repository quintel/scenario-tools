import pandas as pd

from helpers.file_helpers import read_csv, get_folder, check_duplicates
from helpers.helpers import exit


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
            exit(f'Curves should have 8760 values. Please check {self.file_name}')


    def _validate_types(self, data_df):
        # Generate series returning True for all columns of numeric type
        type_series = data_df.apply(
                        lambda s: pd.to_numeric(s, errors='coerce')
                        .notnull().all())
        # Exit if one column contains non-numeric values
        if not type_series.all():
            exit("All curves should only consist of numeric values "
                  f"Please check {self.file_name}")


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
        return cls(file_name, read_csv(file_name, curve=True, dtype=str))


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


def load_curve_file_dict(scenarios):
    # TODO: move to Scenarios
    curve_csvs = set([s.curve_file for s in scenarios if s.curve_file])

    return {file: CurveFile.from_csv(file) for file in curve_csvs}
