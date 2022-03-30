# A csv is added to the output folder: this csv shows rows of 'interesting' data
# for different geographical areas (e.g. all the loose countries and the sum for
# the EU). The 'interesting' data will consist of the same type of fields the
# European Commission is using.
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from helpers.Scenario import ScenarioCollection
from helpers.ETM_API import SessionWithUrlBase
from helpers.helpers import process_arguments
from helpers.file_helpers import read_yml

if __name__ == "__main__":

    base_url, _, _ = process_arguments(sys.argv)

    print('Opening CSV files:')
    scenarios = ScenarioCollection.from_csv('regional_overview_scenarios')
    scenarios.setup_connections(SessionWithUrlBase(base_url))

    print('Connecting to ETM')
    queries = read_yml('regional_overview.yml')

    unpack_queries = {k: v for section in queries for k,v in section['queries'].items()}
    sections = {v: section['section'] for section in queries for v in section['queries'].keys()}

    for scenario in scenarios:
        scenario.area_code = scenario.short_name

    scenarios.query_all_and_export_outcomes(unpack_queries, 'regional_overview.csv', sections)

    print('\nAll done!')
