# external modules
import sys

# project modules
from helpers.ETM_API import ETM_API, SessionWithUrlBase
from helpers.Scenario import ScenarioCollection
from helpers.Curves import load_curve_file_dict
from helpers.helpers import process_arguments, print_bold
from helpers.file_helpers import query_list, data_download_dict, write_csv

if __name__ == "__main__":

    base_url, model_url, query_only_mode,_ = process_arguments(sys.argv)

    print("Opening CSV files:")

    scenarios = ScenarioCollection.from_csv()
    scenarios.setup_connections(SessionWithUrlBase(base_url))

    if query_only_mode:
        scenarios.filter_query_only()
    else:
        curve_file_dict = load_curve_file_dict(scenarios)
        scenarios.add_settings_and_orders()

    query_list = query_list()
    data_download_dict = data_download_dict()

    print(f"\nProcessing {len(scenarios)} scenarios..")
    if query_only_mode:
        print_bold("\n'Query-only' mode is enabled. Only scenario "
                   "outcomes will be collected, no changes to scenarios will "
                   "be made.")

    for scenario in scenarios:
        print(f"\nProcessing scenario {scenario.short_name}..")

        if not query_only_mode:
            if scenario.heat_demand:
                scenario.set_heat_demand_curves()
                # scenario.set_building_agriculture_curves()

            scenario.update(curve_file_dict)

        if query_list:
            print(' Getting queries')
            scenario.query(query_list)

        if data_download_dict:
            print(' Getting downloads')
            for name, download in scenario.get_data_downloads(data_download_dict):
                write_csv(download, f'{scenario.short_name}_{name}',
                    folder=scenario.short_name, index=False, header=True)

    scenarios.export_scenario_outcomes()
    scenarios.export_ids()

    print("\n\nAll done! Open the scenarios in the Energy Transition Model:")
    scenarios.print_urls(model_url)
