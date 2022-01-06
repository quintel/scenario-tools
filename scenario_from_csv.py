# external modules
import sys

# project modules
from helpers.ETM_API import ETM_API, SessionWithUrlBase
from helpers.Scenario import ScenarioCollection
from helpers.Curves import load_curve_file_dict
from helpers.helpers import process_arguments, print_bold
from helpers.file_helpers import query_list, data_download_dict

if __name__ == "__main__":

    base_url, model_url, query_only_mode = process_arguments(sys.argv)

    session = SessionWithUrlBase(base_url)

    print("Opening CSV files:")

    scenarios = ScenarioCollection.from_csv()

    if query_only_mode:
        scenarios.filter_query_only()
    else:
        curve_file_dict = load_curve_file_dict(scenarios)
        scenarios.add_settings()

    query_list = query_list()
    data_download_dict = data_download_dict()


    print(f"\nProcessing {len(scenarios)} scenarios..")
    if query_only_mode:
        print_bold("\n'Query-only' mode is enabled. Only scenario "
                   "outcomes will be collected, no changes to scenarios will "
                   "be made.")

    for scenario in scenarios:
        print(f"\nProcessing scenario {scenario.short_name}..")
        API_scenario = ETM_API(session)
        API_scenario.initialise_scenario(scenario)

        # Do this in the loop to save memory
        if scenario.heat_demand: scenario.set_heat_demand_curves()

        if not query_only_mode:
            API_scenario.update_scenario(scenario, curve_file_dict)

        API_scenario.query_scenario(scenario, query_list, data_download_dict)

    scenarios.export_scenario_outcomes()
    scenarios.export_ids()

    print("\n\nAll done! Open the scenarios in the Energy Transition Model:")
    scenarios.print_urls(model_url)
