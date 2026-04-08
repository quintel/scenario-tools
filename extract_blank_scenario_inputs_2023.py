import requests
import csv
import yaml

# Define the base URL of the API
base_url = "https://engine.energytransitionmodel.com/api/v3"

# List of area codes for which you want to create blank scenarios
area_codes = [
    "GM0482_alblasserdam",
    "GM0505_dordrecht",
    "GM0523_hardinxveld_giessendam",
    "GM0531_hendrik_ido_ambacht",
    "GM0590_papendrecht",
    "GM0610_sliedrecht",
    "GM0642_zwijndrecht",
]

# Personal Access Token for authentication
with open("config/local.settings.yml") as f:
    access_token = yaml.safe_load(f)["personal_etm_token"]

# Function to create a blank scenario
def create_blank_scenario(area_code):
    url = f"{base_url}/scenarios"
    payload = {"scenario": {"area_code": area_code, "end_year": 2050}}
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 422:
        print(f"Error creating scenario for area code {area_code}: {response.json().get('errors')}")
        return None
    response.raise_for_status()
    return response.json()["id"]

# Function to get all scenario inputs and their values
def get_scenario_inputs(scenario_id):
    url = f"{base_url}/scenarios/{scenario_id}/inputs"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# Main script
scenario_inputs = {}

for area_code in area_codes:
    scenario_id = create_blank_scenario(area_code)
    print(f"Created scenario for area code {area_code} with ID: {scenario_id}")

    inputs = get_scenario_inputs(scenario_id)
    scenario_inputs[area_code] = {k: v['default'] for k, v in inputs.items()}

# Get all unique input keys
all_input_keys = set()
for inputs in scenario_inputs.values():
    all_input_keys.update(inputs.keys())

# Create a CSV file
csv_filename = "scenario_inputs_municipalities_nl_2023.csv"
with open(csv_filename, mode='w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["Input Name"] + area_codes)
    for input_key in sorted(all_input_keys):
        row = [input_key] + [scenario_inputs[code].get(input_key, "") for code in area_codes]
        writer.writerow(row)

print(f"Scenario inputs have been exported to {csv_filename}")
