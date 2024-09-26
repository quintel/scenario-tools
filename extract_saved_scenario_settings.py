import requests
import pandas as pd
from io import StringIO
import csv

# Dictionary where keys are scenario names and values are saved scenario numbers
scenarios = {
    'NAT_50': '14553',
    'INT_50': '14555',
    # Add more scenarios here
}

# Function to download a CSV file from the URL
def download_csv(scenario_number):
    url = f'https://energytransitionmodel.com/saved_scenarios/{scenario_number}.csv'
    headers = {
        'Accept-Language': 'nl',
        'I18n-Locale': 'nl',
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Check if the request was successful
    
    # Read CSV content with pandas, specifying the delimiter and quotechar
    decoded_content = response.content.decode('utf-8')
    
    # Use pandas to read the CSV with semicolon as a delimiter and proper quoting
    df = pd.read_csv(StringIO(decoded_content), delimiter=';', quotechar='"', engine='python', on_bad_lines='warn')
    
    return df

# Create an empty list to store the dataframes
dfs = []

# Loop through each scenario and download the associated CSV
for scenario_name, scenario_number in scenarios.items():
    df = download_csv(scenario_number)
    
    # Keep columns 1 to 4 and column 6 as common, add the 5th column as scenario-specific values
    df_scenario = df.iloc[:, [0, 1, 2, 3, 5]].copy()  # Take columns 1 to 4 and column 6
    # df_scenario["Thema"] = df.iloc[:,0]
    # df_scenario["Sidebar"] = df.iloc[:,1]
    # df_scenario["Slide"] = df.iloc[:,2]
    # df_scenario["Input"] = df.iloc[:,3]
    # df_scenario["Eenheid"] = df.iloc[:,5]
    df_scenario[scenario_name] = df.iloc[:, 4]  # Scenario-specific column (5th column in the original file)
    
    # Ensure all columns are strings and strip whitespace
    df_scenario = df_scenario.astype(str)
    df_scenario = df_scenario.apply(lambda x: x.str.strip())
    
    dfs.append(df_scenario)

# Print intermediate csvs to inspect what pandas parsed
for i in range(len(dfs)):
    scenario_names = list(scenarios.keys())
    dfs[i].to_csv(scenario_names[i]+".csv", sep=';', index=False, quoting=csv.QUOTE_ALL, quotechar='"')

# Merge all the dataframes on the common columns
combined_df = dfs[0]  # Start with the first dataframe
for df in dfs[1:]:
    combined_df = pd.merge(combined_df, df, on=list(combined_df.columns[:5]), how='outer')

# Save the combined dataframe to a CSV file, ensuring proper quoting and delimiter
combined_df.to_csv('combined_scenarios.csv', index=False, sep=';', quoting=csv.QUOTE_ALL, quotechar='"')

print('CSV files downloaded and combined successfully!')
