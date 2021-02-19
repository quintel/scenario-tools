# ETM scenario tools

This repository contains a Python tool to create and update scenarios in the [Energy Transition Model](https://pro.energytransitionmodel.com/) (ETM) and export scenario outcomes using an [API](https://www.energytransitionmodel.com/api). The tool can be operated by altering CSV input files. No coding experience is required.

 * [Getting started](#getting-started)
 * [Input data](#input-data)
   * [scenario_list.csv](#scenario_listcsv)
   * [scenario_settings.csv](#scenario_settingscsv)
   * [queries.csv](#queriescsv)
   * [data_downloads.csv](#data_downloadscsv)
   * [curves](#curves)
 * [Running the script](#running-the-script)
 * [Output](#output)
 * [Contact](#questions-and-remarks
 )

### Getting started

Make sure you have [Python 3](https://www.python.org/downloads/) installed. Then, install all required libraries by opening a terminal window in the `scenario-tools` folder (or navigate to this folder in the terminal using `cd "path/to/scenario-tools folder"`) and running the following command:

```
pip install -r requirements.txt
```

### Input data
To create, update and query ETM scenarios you can edit the following CSV files in the `data/input` folder:

 * [`scenario_list.csv`](#scenario_listcsv) - Contains general information about the scenarios, such as the region and target year
 * [`scenario_settings.csv`](#scenario_settingscsv) - Contains the ETM slider values for each of the scenarios specified in `scenario_list.csv`
 * [`queries.csv`](#queriescsv) - Contains a list of queries (scenario outcomes) you would like to retrieve for each scenario.
 * [`data_downloads.csv`](#data_downloadscsv) - Contains a list of data exports you would like to retrieve for each scenario.

 In addition, you may add CSV files containing custom supply, demand and price [curves](#curves) to the `data/input/curves` folder.

#### scenario_list.csv
The `scenario_list.csv` file contains the following columns:
 * **short_name**. Here you can specify an identifier for each scenario. NOTE: short_names must be unique!
 * **title**. Scenario title. This is displayed in the ETM front-end.
 * **area_code**. Scenario region. A full list of available area codes can be found on [Github](https://github.com/quintel/etsource/tree/production/datasets).
 * **end_year**. The target year / year of interest of each scenario.
 * **description**. Scenario description. This is displayed in the model’s front-end.
 * **id**. Can be left empty if you want to create a new scenario. If you want to update an existing scenario, enter its ETM scenario ID here.
 * **protected**. Either `TRUE` or `FALSE`. If set to `TRUE`, Quintel will keep the scenario compatible with future updates of the ETM. Use this if the scenario should remain accessible for a longer period of time, for example because it is updated periodically or is published in a report. If left empty, it defaults to `FALSE`.
 * **curve_file**. The name of a CSV file containing custom hourly profiles. For example interconnector price curves, solar production curves or industry heat demand curves. The CSV file should be placed in the `data/input/curves` folder.
 * **flexibility_order**. To specify the order in which flexibility options are utilised. Can be left empty to use the default order. Options should be separated by a space. E.g.: `“household_batteries mv_batteries power_to_gas”`. The full list of options can be found on [Github](https://github.com/quintel/etsource/blob/production/config/flexibility_order.yml).
 * **heat_network_order**. To specify the order in which dispatchable district heating technologies are utilised if there is a shortage of supply. Can be left empty to use the default order. Options should be separated by a space. E.g.: `"energy_heat_network_storage energy_heat_burner_hydrogen”`. The full list of technologies can be found on [Github](https://github.com/quintel/etsource/blob/production/config/heat_network_order.yml).


#### scenario_settings.csv
The `scenario_settings.csv` file contains the slider settings of your scenarios. The first column contains the keys of all sliders (‘inputs’) that will be set. If a slider is missing from this list, it will inherit the default value. The default value is the value the slider is on when starting a new scenario. The other columns contain the scenario `short_names` (specified in `scenario_list.csv`) and the corresponding slider values. A list of all slider keys can be found [here](https://pro.energytransitionmodel.com/saved_scenarios/10114.csv) (CSV file).

*Example file:*

| input  | scenario_short_name_1   | scenario_short_name_2   |
|---|---|---|
| households_number_of_residences  | 40000  | 37000  |
| transport_useful_demand_passenger_kms  | -1.5  | 2.3  |
| transport_vehicle_using_electricity_efficiency  | 0  | 1.2  |


#### queries.csv
The `queries.csv` file contains a list of queries that will be collected for each scenario. A query is a small ‘request’ for information on a specific topic. For example, each item in the ETM’s dashboard is a query (‘total annual costs’, ‘total CO<sub>2</sub> reduction’). Similarly, each series of a chart in the ETM is a query (‘electricity demand for households space heating’, ‘gas demand for households space heating’ etc.). A list of all available queries can be found on [Github](https://github.com/quintel/etsource/tree/production/gqueries).

*Example file:*

| query  |
|---|
| dashboard_co2_emissions_versus_start_year |
| dashboard_total_costs |
| dashboard_blackout_hours |


#### data_downloads.csv
The `data_downloads.csv` allows you to specify all [data export](https://pro.energytransitionmodel.com/scenario/data/data_export/energy-flows) CSVs that will be downloaded for each scenario. The file contains two columns. One column for specifying which *annual* data exports you are interested in and one column specifying the *hourly* data exports.

*Example file:*

| annual_data  | hourly_data |
|---|---|
| energy_flow | electricity_price
| application_demands | hydrogen
| production_parameters | heat_network
| | household_heat

#### curves
In the `data/input/curves` folder you can add custom demand, supply and price curves to use in your scenarios. These curves can be used to overwrite the default ETM [profiles](https://docs.energytransitionmodel.com/main/curves#modifying-profiles). In the `scenario_list.csv` file you specify for each scenario which CSV curve file to use by adding the file name to the `curve_file` column.

Each file should look as follows:
 * The first row of each column should contain the key of the category you want to upload a custom curve for. A full ist of available keys can be found on [Github](https://github.com/quintel/etsource/blob/production/config/user_curves.yml). Example: *interconnector_1_price*
 * Row 2-8761 should contain the hourly values (one for each hour per year)
 * You can add multiple columns to customize multiple profiles
 * You can add multiple CSV files in case you want to use different profiles for different scenarios

 *Example file:*

| interconnector_1_price  | industry_chemicals_heat |
|---|---|
| 23.4 | 0.023
| 30.4 | 0.021
| 31.2 | 0.034
| 9.8 | 0.045
| ... | ...

### Running the script
To run the script, open a terminal window in the `scenario-tools` folder (or navigate to this folder in the terminal using `cd "path/to/scenario-tools folder"`) and run:

```
python scenario_from_csv.py
```
The script will create or update the scenarios specified in `scenario_list.csv` using the slider settings specified in `scenario_settings.csv` and (optionally) a curve file in the `data/input/curves` folder. For each scenario it will collect query data for all queries in `queries.csv` and download all the data export CSVs specified in `data_downloads.csv`. Once completed, it will print links to your scenarios in the terminal.

If you are creating new scenarios (i.e. you have left the `id` column in `scenario_list.csv` empty), the script will automatically add the IDs of the newly created scenarios to the `scenario_list.csv` file. This ensures that the next time you run the script your scenarios will be updated (rather than creating new ones).


Optionally, you can add the arguments `beta` or `local` to create or query scenarios on the ETM [beta server](https://beta-pro.energytransitionmodel.com/) or your local machine. The latter assumes your local engine runs at `localhost:3000` and local model at `localhost:4000`. I.e.:
```
python scenario_from_csv.py beta
```
or
```
python scenario_from_csv.py local
```

### Output
The script creates/updates the scenarios in the Energy Transition Model and prints the corresponding URLs in the terminal. In addition, it adds the following to the `data/output` folder:
 * A `scenario_outcomes.csv` file containing the query outcomes for all scenarios, including a column containing the values for the present year and the unit of each query
 * Sub folders for each scenario `short_name` containing the data exports


### Questions and remarks

If you have any questions and/or remarks, you may reach out to us by:
* Creating an [issue](https://github.com/quintel/scenario-tools/issues) on this repository and assign one of the Quintel members, e.g.:
  * [Roos de Kok](https://www.github.com/redekok)
  * [Michiel den Haan](https://www.github.com/michieldenhaan)
* Sending an e-mail to [info@quintel.com](mailto:info@quintel.com)
