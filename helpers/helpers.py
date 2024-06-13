'''Helpers for parsing commandline arguments and communicating with user'''

from .settings import Settings

BETA = ['beta', 'staging']
LOCAL = ['local', 'localhost']
PRO = ['pro', 'production']

QUERY_ONLY = ['query_only', 'query-only', 'query', 'read_only', 'read-only',
    'read', 'results_only', 'results-only', 'results']
COMPLETE = ['complete', 'Complete', 'compleet', 'Compleet']

# PRINTING --------------------------------------------------------------------

def warn(*text, **options):
    '''Prints text in a warning color'''
    print(f'\033[93m{" ".join(text)}\033[0m', **options)


def exit(*text, err=None, **options):
    '''Prints text in a failing color and exits'''
    print(f'\033[91m{" ".join(text)}\033[0m', **options)
    if err:
        raise SystemExit() from err
    else:
        raise SystemExit()


def print_bold(*text, **options):
    '''Prints text in bold'''
    print(f'\033[1m{" ".join(text)}\033[0m', **options)


# COMMANDLINE ARGUMENTS PARSING -----------------------------------------------

def convert_to_lower(arr):
    return [s.lower() for s in arr]


def validate_arguments(args):
    invalid = set(args) - set(LOCAL + BETA + PRO + QUERY_ONLY + COMPLETE)
    if invalid:
        print("\n\033[1m" + "WARNING: The following arguments are invalid and "
              f"will be ignored: {', '.join(invalid)}\033[0m"
              "\nPlease only use the following arguments:" +
              f"\nQuery-only mode: {QUERY_ONLY[0]}" +
              f"\nQuery-only mode: {COMPLETE[0]}" +
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
    complete_mode = bool(set(COMPLETE) & set(args))
    base_url, model_url = process_environment(arguments)

    return base_url, model_url, query_only_mode, complete_mode
