import sys
import pandas as pd
from helpers.file_helpers import check_duplicates


class CurveFile:
    """
    Creates an object containing all the curves specified in a curve file
    in the data/input/curves folder.
    """
    def __init__(self, file_name, data_df):
        self.file_name = file_name
        self.curves = set()
        self.data_df = data_df

    def validate_length(self):
        if len(self.data_df) != 8760:
            print()
            sys.exit(1)

    def validate_types(self):
        # Generate series returning True for all columns of numeric type
        type_series = self.data_df.apply(
                        lambda s: pd.to_numeric(s, errors='coerce')
                        .notnull().all())
        # Exit if one column contains non-numeric values
        if not type_series.all():
            print("All curves should only consist of numeric values "
                  f"Please check {self.file_name}")
            sys.exit(1)

    def validate_columns(self):
        columns = list(self.data_df.columns.str.lower())
        check_duplicates(columns, self.file_name, 'column')

    def validate(self):
        self.validate_length()
        self.validate_types()
        self.validate_columns()

    def add_curves(self):
        for key, arr in self.data_df.iteritems():
            curve = Curve(key, arr)
            self.curves.add(curve)


class Curve():
    """
    Creates a curve object containing the (hourly) data points of a custom curve
    """
    def __init__(self, key, data):
        self.key = key
        self.data = data
