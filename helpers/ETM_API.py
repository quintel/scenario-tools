import sys
import io
import json
import pandas as pd
import requests

from contextlib import suppress
from json.decoder import JSONDecodeError

from helpers.file_helpers import get_folder
from helpers.helpers import exit, warn

class SessionWithUrlBase(requests.Session):
    """
    Helper class to store the base url.
    """

    def __init__(self, url_base=None, *args, **kwargs):
        super(SessionWithUrlBase, self).__init__(*args, **kwargs)
        self.url_base = url_base

    def request(self, method, url, **kwargs):
        modified_url = self.url_base + url

        return super(SessionWithUrlBase, self).request(
            method, modified_url, **kwargs)


class ETM_API(object):
    """
    Creates an object based on the ETM api by Quintel
    (see: https://energytransitionmodel.com/api). Each object is connected
    to a single scenario which is identified by the scenario_id. Via the API we
    can request key parameters as shown by the ETM and we can also change
    various input parameters.
    """

    def __init__(self, session, scenario_id=None):
        self.session = session
        self.id = scenario_id


    def return_gqueries(self, p):
        """
        Extracts information from object p by first converting to JSON and
        then to a pandas dataframe.
        """
        return pd.DataFrame.from_dict(p.json()["gqueries"], orient="index")


    def get_scenario(self, scenario_id, detailed=False):
        """
        Obtain a basic description of the scenario by providing the API session
        ID. Using the detailed=true option, a more elaborate description is
        obtained, as well as an overview of all the modified inputs.
        """
        response = self.session.get(f"/scenarios/{scenario_id}", params={"detailed": detailed})
        self.handle_response(response)

        return response.json()


    def get_scenario_settings(self, scenario_id):
        """
        Get an overview of all the modified inputs.
        """
        return self.get_scenario(scenario_id, True)['user_values']


    def create_new_scenario(self, scenario):
        """
        Create a new scenario in the ETM. The id is saved so we can
        continue from the new scenario later on.
        """
        post_data = {
            "scenario": scenario.create_params_as_json()
        }
        response = self.session.post("/scenarios", json=post_data, headers={'Connection': 'close'})
        self.handle_response(response)
        self.id = response.json()['id']


    def update_scenario_properties(self, scenario):
        """
        Update scenario properties such as title and description
        """
        print(" Setting scenario title, description and protected status")

        put_data = {
            "scenario": scenario.properties_as_json()
        }
        response = self.session.put(f"/scenarios/{self.id}", json=put_data,
                             headers={'Connection': 'close'})

        self.handle_response(response)


    def change_inputs(self, user_values, short_name):
        """
        Change inputs to ETM according to dictionary user_values. Also the
        metrics are updated by passing a gquery via gquery_metrics
        """
        put_data = {"scenario": {"user_values": user_values}}
        response = self.session.put(f'/scenarios/{self.id}', json=put_data,
                             headers={'Connection': 'close'})

        self.handle_response(response, fail_info=f"Error for scenario {short_name}")


    def change_heat_network_order(self, heat_network_order):
        """
        Change heat network order to ETM according to object heat_network_order.
        """
        put_data = {"heat_network_order": {"order": heat_network_order}}

        response = self.session.put(f'/scenarios/{self.id}/heat_network_order',
                             json=put_data, headers={'Connection': 'close'})

        self.handle_response(response)


    def get_query_results(self, query_list):
        """
        Perform gqueries on the ETM.
        """
        put_data = {"detailed": True, "gqueries": query_list}
        response = self.session.put(f'/scenarios/{self.id}', json=put_data,
                             headers={'Connection': 'close'})

        self.handle_response(
            response,
            fail_info="Error retrieving queries. Please check your queries.csv.\n"
        )

        return self.return_gqueries(response)


    def get_data_download(self, download_name, hourly=False):
        """
        Collect a data download from the ETM. A data download is
        a set of data predefined by the ETM.
        """
        suffix = f'curves/{download_name}' if hourly else download_name
        response = self.session.get(f"/scenarios/{self.id}/{suffix}")
        self.handle_data_download_response(response, download_name)

        return pd.read_csv(io.StringIO(response.content.decode('utf-8')))


    def export_scenario_data_downloads(self, short_name, download_dict):
        """
        Export data downloads to CSV files.
        """
        path = get_folder('output_file_folder') / short_name
        path.mkdir(parents=True, exist_ok=True)

        self._get_and_write_downloads(download_dict['annual_data'], short_name, path)
        self._get_and_write_downloads(download_dict['hourly_data'], short_name, path, hourly=True)


    def upload_custom_curve(self, curve_key, curve_data, curve_file_name):
        """
        Upload custom curve to ETM
        """
        curve_string = '\n'.join(str(e) for e in curve_data)
        put_data = {'file': (curve_file_name, curve_string)}

        response = self.session.put(f'/scenarios/{self.id}/custom_curves/{curve_key}',
                             files=put_data, headers={'Connection': 'close'})

        self.handle_response(response)


    def initialise_scenario(self, scenario):
        if not scenario.id:
            self.create_new_scenario(scenario)
            scenario.id = self.id
        else:
            self.id = scenario.id


    def update_scenario(self, scenario, curve_file_dict):
        self.update_scenario_properties(scenario)

        self._check_and_update_user_values(scenario)
        self._check_and_update_heat_network(scenario)
        self._check_and_update_curves(scenario, curve_file_dict)
        self._check_and_update_heat_demand(scenario)

        if scenario.flexibility_order:
            warn(" Flexibility order is no longer supported")


    def query_scenario(self, scenario, query_list, download_dict):
        """
        Collect queries and data downloads
        """
        if query_list:
            print(" Collecting query data")
            scenario.query_results = self.get_query_results(query_list)

        if download_dict:
            print(" Collecting data downloads")
            self.export_scenario_data_downloads(scenario.short_name,
                                                download_dict)


    def handle_response(self, response, fail_info=''):
        '''
        Lets sucessful responses through, prints errors and exits when response is bad
        '''
        if response.ok:
            return

        if response.status_code == 404:
            fail_info += 'Scenario was not found.'

        if fail_info: print(fail_info)

        with suppress(JSONDecodeError):
            print(json.dumps(response.json(), indent=4, sort_keys=True))

        sys.exit(1)


    def handle_data_download_response(self, response, download_name):
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            exit("Something went wrong retrieving a data download. "
                  "Check your data_downloads.csv!\n", err=err)

        if response.text.startswith('<!DOCTYPE html>'):
            exit(f'Download "{download_name}" is not available for scenarios '
                    'with Merit turned off. Aborting...\n')


    def _get_and_write_downloads(self, download_names, short_name, path, hourly=False):
        '''Downloads and writes all requested files to the output folder'''
        for download in download_names:
            self.get_data_download(download, hourly=hourly).to_csv(
                path / f"{short_name}_{download}.csv", index=False, header=True)


    def _check_and_update_user_values(self, scenario):
        '''Checks if user values should be updated, and updates them'''
        if not scenario.user_values: return

        print(" Setting sliders")
        self.change_inputs(scenario.user_values, scenario.short_name)


    def _check_and_update_heat_network(self, scenario):
        '''Checks if heat network should be updated, and updates it'''
        if not scenario.heat_network_order: return

        print(" Setting heat network order")
        self.change_heat_network_order(scenario.heat_network_order)


    def _check_and_update_curves(self, scenario, curve_file_dict):
        '''Checks if curve files should be updated, and uploads them'''
        if not scenario.curve_file: return

        print(" Uploading custom curves:")
        for curve in curve_file_dict[scenario.curve_file].curves:
            print(f"  - {curve.key}")
            self.upload_custom_curve(curve.key, curve.data,
                                        scenario.curve_file)


    def _check_and_update_heat_demand(self, scenario):
        '''Checks if heat demand should be updated, and updates it'''
        if not scenario.heat_demand or not scenario.heat_demand_curves: return

        print(' Generating and uploading 15 heat demand curves, this may take a while:')
        for curve in scenario.heat_demand_curves:
            curve.to_csv(scenario.heat_demand)
            splitted = curve.key.split('_')
            print(f"  - Generated {' '.join(splitted[1:-1])} {splitted[-1]} insulation")
            self.upload_custom_curve(f'weather/{curve.key}', curve.data, curve.key)
            print(f"  - Uploaded curve")
