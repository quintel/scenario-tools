'''Helpers for parsing commandline arguments'''

from .Curves import CurveFile
from .settings import Settings

BETA = ['beta', 'staging']
LOCAL = ['local', 'localhost']
PRO = ['pro', 'production']

QUERY_ONLY = ['query_only', 'query-only', 'query', 'read_only', 'read-only',
    'read', 'results_only', 'results-only', 'results']


def load_curve_file_dict(scenarios):
    # TODO: move to Scenarios
    curve_csvs = set([s.curve_file for s in scenarios if s.curve_file])

    if curve_csvs:
        print(" Reading curve files")

    return {file: CurveFile.from_csv(file) for file in curve_csvs}


# COMMANDLINE ARGUMENTS PARSING -----------------------------------------------

def convert_to_lower(arr):
    return [s.lower() for s in arr]


def validate_arguments(args):
    invalid = set(args) - set(LOCAL + BETA + PRO + QUERY_ONLY)
    if invalid:
        print("\n\033[1m" + "WARNING: The following arguments are invalid and "
              f"will be ignored: {', '.join(invalid)}\033[0m"
              "\nPlease only use the following arguments:" +
              f"\nQuery-only mode: {QUERY_ONLY[0]}" +
              f"\nEnvironments: {PRO[0]}, {BETA[0]} or {LOCAL[0]}.\n")


def process_environment(args):
    if set(args) & set(BETA):
        base_url = "https://beta-engine.energytransitionmodel.com/api/v3"
        model_url = "https://beta-pro.energytransitionmodel.com"
    elif set(args) & set(LOCAL):
        base_url = Settings.get('local_engine_url')
        model_url = Settings.get('local_model_url')
    else:
        base_url = "https://engine.energytransitionmodel.com/api/v3"
        model_url = "https://pro.energytransitionmodel.com"

    return base_url, model_url


def process_arguments(args):
    '''Processes the commandline args'''
    arguments = convert_to_lower(args[1:]) if len(args) > 1 else []

    validate_arguments(arguments)
    query_only_mode = bool(set(QUERY_ONLY) & set(args))
    base_url, model_url = process_environment(arguments)

    return base_url, model_url, query_only_mode
