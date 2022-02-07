# ETM scenario tools

This repository contains a Python tool to create and update scenarios in the [Energy Transition Model](https://pro.energytransitionmodel.com/) (ETM) and export scenario outcomes using an [API](https://docs.energytransitionmodel.com/api/intro). The tool can be operated by altering CSV input files. No coding experience is required.

 * [Getting started](#getting-started)
 * [Input data](#input-data)
   * [scenario_list.csv](#scenario_listcsv)
   * [scenario_settings.csv](#scenario_settingscsv)
   * [queries.csv](#queriescsv)
   * [data_downloads.csv](#data_downloadscsv)
   * [curves](#curves)
   * [template_list.csv](#template_listcsv)
 * [Running the script](#running-the-script)
   * [Query-only mode](#query-only-mode)
   * [Specifying environments](#specifying-environments)
 * [Output](#output)
 * [Extra configuration](#configuration)
 * [Contact](#questions-and-remarks)

### Getting started

Make sure you have [Python 3](https://www.python.org/downloads/) installed. Then, install all required libraries by opening a terminal window in the `scenario-tools` folder (or navigate to this folder in the terminal using `cd "path/to/scenario-tools folder"`).

It is recommended (but not required) that you use [`pipenv`](https://pipenv.pypa.io/en/latest/) for running these tools. When using `pipenv`
it will create a virtual environment for you. A virtual environment helps with keeping the libaries you install here separate of your global libraries (in
other words your `scenario-tools` will be in a stable and isolated environment and are thus less likely to break when updating things elswhere on your computer)
and this one comes with some nice shortcuts for running the tools.

You can instal `pipenv` with `pip` or `pip3` if you don't have it installed yet.
```
pip3 install pipenv
```

Then you can create a new environment and install all the libraries in one go by running:
```
pipenv install
```


Alternatively, if you do **not** want to use `pipenv` you can also install the requirements globally by running:
```
pip3 install -r requirements.txt
```


### Input data
To create, update and query ETM scenarios you can edit the following CSV files in the `data/input` folder:

 * [`scenario_list.csv`](#scenario_listcsv) - Contains general information about the scenarios, such as the region and target year
 * [`scenario_settings.csv`](#scenario_settingscsv) - Contains the ETM slider values for each of the scenarios specified in `scenario_list.csv`
 * [`queries.csv`](#queriescsv) - Contains a list of queries (scenario outcomes) you would like to retrieve for each scenario.
 * [`data_downloads.csv`](#data_downloadscsv) - Contains a list of data exports you would like to retrieve for each scenario.

 In addition, you may add CSV files containing custom supply, demand and price [curves](#curves) to the `data/input/curves` folder.

To get scenario settings from an existing scenario (from now on called a scenario "template") you can edit the following CSV file in the `data/input` folder:

 * [`template_list.csv`](#template_listcsv) -  Contains a list of scenario templates specified by its scenario ID

#### scenario_list.csv
The `scenario_list.csv` file contains the following columns:
 * **short_name**. Here you can specify an identifier for each scenario. NOTE: short_names must be unique!
 * **title**. Scenario title. This is displayed in the ETM front-end.
 * **area_code**. Scenario region. A full list of available area codes can be found on [Github](https://github.com/quintel/etsource/tree/production/datasets).
 * **end_year**. The target year / year of interest of each scenario.
 * **description**. Scenario description. This is displayed in the model’s front-end.
 * **id**. Can be left empty if you want to create a new scenario. If you want to update an existing scenario, enter its ETM scenario ID here.
 * **protected**. *Optional.* Either `TRUE` or `FALSE`. If set to `TRUE`, the scenario will be frozen.
  This means that no one will be able to change or update any of the settings, including yourself.
  The scenario will still be queryable. If left empty, it defaults to `FALSE`.
 * **curve_file**. The name of a CSV file containing custom hourly profiles. For example interconnector price curves, solar production curves or industry heat demand curves. The CSV file should be placed in the `data/input/curves` folder.
 * **flexibility_order**. To specify the order in which flexibility options are utilised. Can be left empty to use the default order. Options should be separated by a space. E.g.: `“household_batteries mv_batteries power_to_gas”`. The full list of options can be found on [Github](https://github.com/quintel/etsource/blob/production/config/flexibility_order.yml).
 * **heat_network_order**. To specify the order in which dispatchable district heating technologies are utilised if there is a shortage of supply. Can be left empty to use the default order. Options should be separated by a space. E.g.: `"energy_heat_network_storage energy_heat_burner_hydrogen”`. The full list of technologies can be found on [Github](https://github.com/quintel/etsource/blob/production/config/heat_network_order.yml).
 * **heat_demand**. *Optional - expert feature.* The name of the folder inside `data/input/curves` that contains either 15 heat demand profiles, or the three input files neccesary to generate new profiles.


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

#### curves - heat demand
You can also supply a custom subfolder in the curves folder which contains either heat demand curves, or ways to generate these heat demand curves:

  1. **Supply your own heat demand curves** In this subfolder, supply csv profiles (summing to 1/3600) for all combinations of the following house types and insulation levels: *"terraced_houses", "corner_houses", "semi_detached_houses", "apartments", "detached_houses"* and *"low", "medium", "high"*. The names of the csv files should look like *insulation_apartments_low*. All 15 files should be present. Or;
  2. **Generate heat demand curves** To generate your own heat demand profiles and upload them, three input csv files should be present in the subfolder:
     - temperature: The outside temperature in degrees C for all 8760 hours of the year;
     - irradiation: The irradiation in J/cm2 for all 8760 hours of the year;
     - thermostat: A csv with three columns (*low, medium, high*), with thermostat settings for  24 hours.

  The generated curves will be written to the subfolder, and can be inspected and reused.

The tool will checkout your subfolder and decide for itself which of the two paths to follow. If the 15 profiles are there, these will be used. If the three input files are present, new curves will be generated.

#### template_list.csv
The `template_list.csv` file contains the following columns:

 * **id**. Here you can specify the ETM scenario ID of the scenario template.
 * **title**. Here you can add a title for the template which is also displayed in the template settings output file.

### Running the scripts
To run the script, open a terminal window in the `scenario-tools` folder (or navigate to this folder in the terminal using `cd "path/to/scenario-tools folder"`) and run:
```
pipenv run scenario_from_csv
```
Or, if you opted out of `pipenv`:
```
python scenario_from_csv.py
```
The script will create or update the scenarios specified in `scenario_list.csv` using the slider settings specified in `scenario_settings.csv`, (optionally) a curve file in the `data/input/curves` folder, and (optionally) use the heat demand subfolder of the `curves` folder. For each scenario it will collect query data for all queries in `queries.csv` and download all the data export CSVs specified in `data_downloads.csv`. Once completed, it will print links to your scenarios in the terminal.

If you are creating new scenarios (i.e. you have left the `id` column in `scenario_list.csv` empty), the script will automatically add the IDs of the newly created scenarios to the `scenario_list.csv` file. This ensures that the next time you run the script your scenarios will be updated (rather than creating new ones).

#### Query-only mode
Optionally, you can add the `query_only` argument to run the script in 'query-only mode':

```
pipenv run scenario_from_csv query_only
```

In query-only mode the script will only collect scenario results ([queries](#queriescsv) and [data downloads](#data_downloadscsv)). No changes will be made to existing scenarios, nor will new scenarios be created. The latter means that scenarios in the [`scenario_list.csv`](#scenario_listcsv) without an 'id' will be ignored, as these scenarios have not yet been created.

#### Specifying environments
In addition, you can add the arguments `beta` or `local` to create or query scenarios on the ETM [beta server](https://beta-pro.energytransitionmodel.com/) or your local machine. The latter assumes your local engine runs at `localhost:3000` and local model at `localhost:4000`, but you can change this in `config/settings.yml` at any time. I.e.:
```
pipenv run scenario_from_csv beta
```
or
```
pipenv run scenario_from_csv local
```

#### Using scenario templates
It's also possible to adopt the settings of an existing scenario, which we then call a scenario template. To do this, run the following in the terminal:
```
pipenv run get_template_settings
```
Or, if you opted out of using `pipenv`:
```
python get_template_settings.py
```

The script will create a `template_settings.csv` file in the `data/output/` folder. This file provides an overview of all slider settings for each scenario template. To adopt the values, open the `data/adopt_template_settings.xlsx` file and copy paste the entire sheet into the `template_settings` sheet. In the `adopter` sheet you can choose which scenario template should be used by specifying the template scenario ID. Also, you can choose which scenario settings to adopt by specifying TRUE or FALSE for each input key. By default, all settings are adopted except for the ones representing a capacity (in MW). When you're done, replace the `data/input/scenario_settings.csv` by the sheet `scenario_settings` from the Excel file.

### Output
The script creates/updates the scenarios in the Energy Transition Model and prints the corresponding URLs in the terminal. In addition, it adds the following to the `data/output` folder:

 * A `scenario_outcomes.csv` file containing the query outcomes for all scenarios, including a column containing the values for the present year and the unit of each query
 * Sub folders for each scenario `short_name` containing the data exports

### Configuration
You can change three different kinds of settings in the configuration file `config/settings.yml`: input/output folder settings, settings for [when you run the model locally](#specifying-environments), and CSV settings. Here is a quick overview:

| Setting | What does it do? | Default value |
| --- | --- | --- |
| `input_file_folder` | Location of the main input files, this can be a full path to anywhere on your computer. | `data/input`|
| `input_curves_folder` | Location of where the curve files you wish to use are stored, this can be a full path to anywhere on your computer. | `data/input/curves`|
| `output_file_folder` | Location of where all output files should be written to by the tools. Again, this can be a full path to any folder on your computer. | `data/output` |
|`local_engine_url`| The url to ETEngine that should be used when you use the `local` option in the tools. | `http://localhost:3000/api/v3` |
|`local_model_url`| The url to ETModel that should be used when you use the `local` option in the tools. | `http://localhost:4000` |
| `csv_separator` | The separator your CSV files are using. Some European computers use ';' instead of ','. | , |

### Questions and remarks

If you have any questions and/or remarks, you may reach out to us by:

* Creating an [issue](https://github.com/quintel/scenario-tools/issues) on this repository and assign one of the Quintel members, e.g.:
  * [Roos de Kok](https://www.github.com/redekok)
  * [Michiel den Haan](https://www.github.com/michieldenhaan)
* Sending an e-mail to [info@quintel.com](mailto:info@quintel.com)
