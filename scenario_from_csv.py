# external modules
import sys

# project modules
from helpers.ETM_API import ETM_API, SessionWithUrlBase
from helpers.helpers import (process_arguments,
                             initialise_scenarios,
                             load_curve_file_dict,
                             update_scenarios,
                             print_ids)
from helpers.file_helpers import (generate_query_list,
                                  generate_data_download_dict,
                                  export_scenario_ids,
                                  export_scenario_queries)

if __name__ == "__main__":

    base_url, model_url = process_arguments(sys.argv)

    session = SessionWithUrlBase(base_url)

    print("Opening CSV files:")
    scenarios = initialise_scenarios()
    curve_file_dict = load_curve_file_dict(scenarios)

    download_dict = generate_data_download_dict()
    query_list = generate_query_list()

    update_scenarios(scenarios)

    for scenario in scenarios:
        print(f"\nProcessing scenario {scenario.short_name}..")
        API_scenario = ETM_API(session)
        API_scenario.initialise_scenario(scenario)

        API_scenario.update_scenario(scenario, curve_file_dict)

        API_scenario.query_scenario(scenario, query_list, download_dict)

    export_scenario_queries(scenarios)
    export_scenario_ids(scenarios)

    print_ids(scenarios, model_url)
