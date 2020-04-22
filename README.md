# ETM scenario tools

In this repository Python tools are provided to create and update ETM scenarios and export scenario outcomes using our [API](https://www.energytransitionmodel.com/api).

### Getting started

Make sure you have [Python 3](https://www.python.org/downloads/) and [pip3](https://pip.pypa.io/en/stable/installing/) installed. Then, install all required libraries by running the following command in your terminal (at the root of this repository):

```
pip3 install -r requirements.txt
```

### Scenario tools

The scenario tools are based on a [Python wrapper](https://github.com/quintel/third-party) for the [Energy Transition Model API](https://www.energytransitionmodel.com/api).

Currently, two tools are provided:
* `scenario_from_csv.py` - for creating a new or updating an existing ETM scenario based on a CSV-based list of input (or user) values.

* `data_export_to_csv.py` - to export outcomes for one or more scenarios to CSV-files.

<br>

#### `scenario_from_csv.py`

This script can be used to create new or update existing ETM scenarios.

<br>

**_1. Create a new scenario_**

In order to create one or more ETM scenarios, follow these steps:

**Step 1** - Update the `config.py` file. Add the scenario(s) to the object `NEW_SCENARIOS`. For each scenario several properties should be specified. Below you can find an example:

```
NEW_SCENARIOS = {
    'scenario_key': {
        'title': f"Example scenario (2030)",
        'area_code': 'nl',
        'short_name': '2030_example',
        'end_year': '2030',
        'id': None,
        'user_values': {},
        'flexibility_order': [
            "household_batteries",
            "mv_batteries",
            "electric_vehicle",
            "opac",
            "pumped_storage",
            "power_to_gas",
            "power_to_heat_industry",
            "power_to_heat_district_heating_boiler",
            "power_to_heat_district_heating_heatpump",
            "power_to_kerosene",
            "export",
        ],
        'heat_network_order': [
            "energy_heat_burner_wood_pellets",
            "energy_heat_network_storage",
            "energy_heat_burner_waste_mix",
            "energy_heat_heatpump_water_water_electricity",
            "energy_heat_burner_coal",
            "energy_heat_burner_network_gas",
            "energy_heat_burner_crude_oil",
            "energy_heat_burner_hydrogen",
        ]
    }
```

Some remarks:
  * The `scenario_key` should match the key that is used in the  `./data/input/user_values.csv` input file.
  * The `area_code` should refer to the [`area` attribute](https://github.com/quintel/etsource/blob/master/datasets/nl/nl.full.ad#L1) of an existing dataset on [ETSource](https://github.com/quintel/etsource/tree/master/datasets).
  * Make sure the `user_values` points to an empty object. This object will be updated based on the input data by running the script.
  * Make sure the `id` is set to `None`.
  * The [`flexibility_order`](https://pro.energytransitionmodel.com/scenario/flexibility/excess_electricity/order-of-flexibility-options) and [`heat_network_order`](https://pro.energytransitionmodel.com/scenario/supply/heat_merit/priority-of-dispatchable-heat-producers) can also be updated by changing the order of the options within the array.

**Step 2** - Update the `./data/input/user_values.csv` file. Some remarks:
  * The slider keys are listed in the first column (`input`).
  * The corresponding slider values for each scenario are listed in the columns right from the slider keys. The column header should refer to the `scenario_key` specified in the `config.py` file.

**Step 3** - Run the script from the root of the repository in your terminal:

```
python3 scenario_from_csv.py
```

The links to the newly created scenarios will be printed in your terminal.

**Note** - By default the scenarios are not protected. This can be changed [here](https://github.com/quintel/scenario-tools/blob/master/scenario_from_csv.py#L42) in the script, by setting `protected` to `True`.

<br>

**_2. Update an existing scenario_**

The process of updating existing scenarios is similar to the process of creating a new scenario:

**Step 1** - Update the `config.py` file. Specify the scenario properties in the `NEW_SCENARIOS` object. Make sure you set the `id` to the `api_session_id` of the existing scenario. The latter can be found by viewing the page source of an ETM scenario.

**Step 2** and **Step 3** - These steps are similar to the steps of creating a new scenario.

**Note** - Be aware of the fact that the scenario is updated by its `api_session_id`, not by its `saved_scenario_id`. If you want your scenario to be saved, this should be done manually in the ETM interface.

<br>

#### `data_export_to_csv.py`

This script can be used to export scenario outcomes to CSV files. When you have successfully created an ETM scenario, you might want to export the scenario outcomes. The ETM offers multiple [data exports](https://pro.energytransitionmodel.com/scenario/data/data_export/energy-flows):
* Energy flows
* Yearly energy demand per application
* Specifications heat and electricity production
* Hourly curves for electricity
* Hourly curves for household heat
* Hourly curves for gas
* Hourly curves for hydrogen
* Hourly curves for heat networks

Instead of exporting these manually through the ETM interface this script allows the user to export all desired data exports at once:

**Step 1** - Update the `config.py` file. Specify the scenarios in the `EXISTING_SCENARIOS` object. Below you can find an example:

```
EXISTING_SCENARIOS = {
    'scenario_key': { 'id': '754910' },
    'another_scenario_key': { 'id': '754911' }
}
```

Some remarks:
* The data exports will be grouped by scenario in a directory named `<id>_<scenario_key>`. These directories can be found in `./data/output`.

**Step 2** - Specify which scenario outcomes should be exported. This can be changed [here](https://github.com/quintel/scenario-tools/blob/master/data_export_to_csv.py#L129-L137) in the script, by commenting out lines of unwanted data exports.

**Step 3** - Run the script from the root of the repository in your terminal:

```
python3 data_export_to_csv.csv
```

The scenario outcomes will be exported to `./data/output`.

<br>

### Questions and/or remarks

If you have any questions and/or remarks, you may reach out to us by:
* Creating an [issue](https://github.com/quintel/scenario-tools/issues) on this repository and assign one of the QI members, e.g.:
  * [Roos de Kok](https://www.github.com/redekok)
* Sending an e-mail to [info@quintel.com](mailto:info@quintel.com)
