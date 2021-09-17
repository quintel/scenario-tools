# external modules
import sys

# project modules
from helpers.ETM_API import ETM_API, SessionWithUrlBase
from helpers.helpers import (process_arguments,
                             initialise_scenarios,
                             load_curve_file_dict,
                             add_scenario_settings,
                             print_ids)
from helpers.file_helpers import (generate_query_list,
                                  generate_data_download_dict,
                                  export_scenario_ids,
                                  export_scenario_queries)

if __name__ == "__main__":

    base_url, model_url, query_only_mode = process_arguments(sys.argv)

    session = SessionWithUrlBase(base_url)

    print("Opening CSV files:")
    scenarios = initialise_scenarios()

    if query_only_mode:
        # only process scenarios with existing scenario id
        scenarios = [scen for scen in scenarios if scen.id]

    else:
        curve_file_dict = load_curve_file_dict(scenarios)
        add_scenario_settings(scenarios)

    download_dict = generate_data_download_dict()
    query_list = generate_query_list()

    print(f"\nProcessing {len(scenarios)} scenarios..")
    if query_only_mode:
        print("\n\033[1m'Query-only' mode is enabled. Only scenario "
              "outcomes will be collected, no changes to scenarios will "
              "be made.\033[0m")
    for scenario in scenarios:
        print(f"\nProcessing scenario {scenario.short_name}..")
        API_scenario = ETM_API(session)
        API_scenario.initialise_scenario(scenario)

        # Do this in the loop to save memory
        if scenario.heat_demand: scenario.set_heat_demand_curves()

        if not query_only_mode:
            API_scenario.update_scenario(scenario, curve_file_dict)

        API_scenario.query_scenario(scenario, query_list, download_dict)

    export_scenario_queries(scenarios)
    export_scenario_ids(scenarios)

    print_ids(scenarios, model_url)
