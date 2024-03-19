# external modules
import sys
import pandas as pd
from datetime import datetime

# project moduless
from helpers.ETM_API import SessionWithUrlBase
from helpers.Scenario import Scenario
from helpers.helpers import process_arguments, print_bold
from helpers.file_helpers import write_csv, read_csv

if __name__ == "__main__":
    # Set general variables
    today = datetime.now().strftime("%Y%m%d")
    base_url, model_url, query_only_mode = process_arguments(sys.argv)
    file_name = 'slider_comparison_settings'
    scenario_attributes_name = 'scenario_list'
    
    # Read scenario attributes from scenario_list
    scenario_attributes = read_csv(scenario_attributes_name)
    scenario = Scenario(scenario_attributes.to_dict(orient='records')[0])
    short_name = scenario.short_name
    scenario.setup_connection(SessionWithUrlBase(base_url))

    # Read slider comparison settings csv
    df = read_csv(file_name)
    # Create list with unique slider set names
    sets = df["set_name"].unique()

    # Create dataframe for results
    res_columns = ["set_name", "output_gquery", "unit", "result_start_value", "result_future_value"]
    df_output = pd.DataFrame(columns = res_columns).set_index("set_name")
    slider_column_names = ["slider_start_value", "slider_future_value"]

    # Start obtaining results for each slider set
    for set in sets:
        print_bold(f"\nStarting set: {set}")
        df_tmp = df[df["set_name"] == set].set_index("set_name")
        
        # Get scenario settings and results per start and future slider value
        for i in ["start","future"]:
            print(f"Obtaining results for slider {i} value")
            scenario_settings = df_tmp[["slider_name", f"slider_{i}_value"]]
            scenario_settings = scenario_settings.rename(
                columns={
                    "slider_name": "input",
                    f"slider_{i}_value": short_name
                    }).set_index("input")
            scenario_settings_dict = scenario_settings[short_name].dropna().to_dict()
            # Check if sliders from previous set should be reset
            try:
                duplicates = [key for key in scenario_settings_dict_reset if key in scenario_settings_dict]
                for key in duplicates:
                    scenario_settings_dict_reset.pop(key)
                scenario_settings_dict_merged = {**scenario_settings_dict, **scenario_settings_dict_reset}
                # Add scenario_settings to scenario class user_values
                scenario.user_values = scenario_settings_dict_merged
            except NameError:
                # No previous slider changes
                scenario.user_values = scenario_settings_dict

            # Obtain and update query_results queries
            query_list = df_tmp["output_gquery"].unique().tolist()
            
            # Update scenario and query results
            scenario.update({})
            scenario.query(query_list)

            # Obtain set results in df
            df_res = pd.DataFrame()
            df_res = scenario.add_results_to_df(df_res).rename(columns={short_name: f"result_{i}_value"}).reset_index()
            # Set slider name as index
            df_res.index = df_tmp.index.unique()
            
            # Check for set or individual sliders for correct data transformation
            if len(df_tmp.axes[0]) > 1:
                if i == "start":
                    df_set = pd.concat([df_tmp.iloc[:1], df_res[["unit", f"result_{i}_value"]]], axis=1)
                else:
                    df_set = pd.concat([df_set, df_res[f"result_{i}_value"]], axis=1)
                df_res = df_set
            else:
                if i == "start":
                    df_res_single = pd.concat([df_tmp, df_res[["unit", f"result_{i}_value"]]], axis=1)
                else:
                    df_res_single = pd.concat([df_res_single, df_res[f"result_{i}_value"]], axis=1)
                df_res = df_res_single
        
        # Store set results in dataframe
        df_output = pd.concat([df_output, df_res.drop(["slider_name", "slider_start_value", "slider_future_value"], axis=1)])
        
        # Obtain dictionary with slider resets
        scenario_settings_dict_reset = {k: 'reset' for k, v in scenario_settings_dict.items()}

    # Write results to csv
    write_csv(df_output, f"{today}_slider_comparison_results_{short_name}")
    
    print("\n\nAll done! Open the scenarios in the Energy Transition Model:")
    print(f"{short_name}: {model_url}/scenarios/{scenario.id}")
    