import io
import pandas as pd
import requests
import json

from contextlib import suppress
from json.decoder import JSONDecodeError

from helpers.helpers import exit, warn
from helpers.settings import Settings


class SessionWithUrlBase(requests.Session):
    """
    Helper class to store the base url.
    """

    def __init__(self, url_base=None, *args, **kwargs):
        super(SessionWithUrlBase, self).__init__(*args, **kwargs)
        self.url_base = url_base

        if Settings.get('proxy_servers'):
            self.proxies = Settings.get('proxy_servers')

    def request(self, method, url, headers={}, **kwargs):
        modified_url = self.url_base + url

        if Settings.get('personal_etm_token'):
            headers['Authorization'] = f"Bearer {Settings.get('personal_etm_token')}"

        return super(SessionWithUrlBase, self).request(
            method, modified_url, headers=headers, **kwargs)


class ETM_API(object):
    """
    Creates an object based on the ETM api by Quintel
    (see: https://energytransitionmodel.com/api). Each object is connected
    to a single scenario which is identified by the scenario.id. Via the API we
    can request key parameters as shown by the ETM and we can also change
    various input parameters.
    """

    def __init__(self, session, scenario=None):
        self.session = session
        self.scenario = scenario

        if self.scenario and not self.scenario.id:
            self.create_etm_scenario()


    def create_etm_scenario(self):
        """
        Create a new scenario in the ETM based on the Scenario. The id is saved
        so we can continue from the new scenario later on.
        """
        post_data = {
            "scenario": self.scenario.create_params_as_json()
        }
        response = self.session.post("/scenarios", json=post_data, headers={'Connection': 'close'})
        self.handle_response(response)
        self.scenario.id = response.json()['id']

        # Note: This behaviour is not yet part of ETE
        if not self.scenario.end_year == response.json()['end_year']:
            warn(f'Invalid end year {self.scenario.end_year} for scenario',
                f'{self.scenario.short_name} was changed to {response.json()["end_year"]}')
            self.scenario.end_year = response.json()['end_year']


    # GETTING -----------------------------------------------------------------


    def get_info(self, detailed=False):
        """
        Obtain a basic description of the scenario. Using the detailed=true option,
        a more elaborate description is obtained, as well as an overview of all
        the modified inputs.
        """
        response = self.session.get(f"/scenarios/{self.scenario.id}", params={"detailed": detailed})
        self.handle_response(response)

        return response.json()


    def get_scenario_settings(self, settings_type='user_values'):
        """
        Get an overview of all the modified inputs.
        """
        return self.get_info(detailed=True)[f'{settings_type}']


    def get_data_download(self, download_name, hourly=False):
        """
        Collect a data download from the ETM. A data download is
        a set of data predefined by the ETM.
        """
        suffix = f'curves/{download_name}' if hourly else download_name
        response = self.session.get(f"/scenarios/{self.scenario.id}/{suffix}")
        self.handle_data_download_response(response, download_name)

        return pd.read_csv(io.StringIO(response.content.decode('utf-8')))


    def query(self, query_list):
        """
        Perform gqueries on the ETM. Sets the results on the scenario. Returns a pd.DataFrame.
        """
        put_data = {"detailed": True, "gqueries": query_list}
        response = self.session.put(f'/scenarios/{self.scenario.id}', json=put_data,
                             headers={'Connection': 'close'})

        self.handle_response(
            response,
            fail_info="Error retrieving queries. Please check your queries file.\n"
        )

        self.scenario.query_results = pd.DataFrame.from_dict(response.json()["gqueries"],
            orient="index")

        return self.scenario.query_results


    def get_data_downloads(self, download_dict):
        """
        Downloads and yields (str, pd.DataFrame) tuples of the download name and data
        of all downloads specified in a dict(list).
        """
        yield from self._get_downloads(download_dict['annual_data'])
        yield from self._get_downloads(download_dict['hourly_data'], hourly=True)


    def get_custom_curves(self):
        '''
        Get custom curves attached to the scenario.
        Collects custom curves in one pd.DataFrame output.
        Internal curves (not visible in the frontend if uploaded) are included.
        '''
        response = self.session.get(f"/scenarios/{self.scenario.id}/custom_curves?include_internal=true")
        self.handle_response(
            response,
            fail_info="Error obtaining custom curves.\n")

        # Filter the curve keys attached to the scenario and create dataframe
        curves_data = json.loads(response.content)
        curves_attached = [curve['key'] for curve in curves_data if curve['attached']]
        df = pd.DataFrame()
        for curve in curves_attached:
            response = self.session.get(f"/scenarios/{self.scenario.id}/custom_curves/{curve}.csv")
            # Decode and obtain float values of curve
            decoded_response = response.content.decode('utf-8').split('\n')
            float_values = [float(value) for value in decoded_response]
            # Add curve to dataframe
            df[curve] = float_values

        return df


    def get_custom_orders(self, orders):
        '''
        Get custom orders for the scenario. Obtains custom orders in one
        string per order type. Returns pd.DataFrame with all custom orders.
        '''
        df = pd.DataFrame()
        for order in orders:
            response = self.session.get(f'/scenarios/{self.scenario.id}/{order}')
            self.handle_response(
                response,
                fail_info=f"Error in obtaining custom order for '{order}'")

            response_dict = json.loads(response.content.decode('utf-8'))
            order_string = " ".join(response_dict['order'])
            df[order] = [order_string]

        return df


    def get_heat_network_orders(self, heat_orders):
        """
        Get the scenario's heat network orders.
        """
        temperature_level = [order.split('_')[-1] for order in heat_orders]
        df = pd.DataFrame()
        for t in temperature_level:
            response = self.session.get(f"/scenarios/{self.scenario.id}/heat_network_order", params={"subtype": t})
            self.handle_response(
                response,
                fail_info=f"Error in obtaining heat network order for temperature level '{t}'"
            )
            response_dict = json.loads(response.content.decode('utf-8'))
            df[f'heat_network_order_{t}'] = [' '.join(response_dict['order'])]

        return df.transpose()


    # UPDATING ----------------------------------------------------------------


    def update(self, curve_file_dict):
        '''Updates everything at once'''
        self.update_properties()

        self._check_and_update_user_values()
        self._check_and_update_heat_network()
        self._check_and_update_curves(curve_file_dict)
        self._check_and_update_heat_demand(curve_file_dict)

        if self.scenario.flexibility_order:
            warn(" Flexibility order is no longer supported")


    def update_properties(self):
        """
        Update scenario properties such as title and description
        """
        print(" Setting scenario title, description and keep_compatible status")

        put_data = {
            "scenario": self.scenario.properties_as_json()
        }
        response = self.session.put(f"/scenarios/{self.scenario.id}", json=put_data,
                             headers={'Connection': 'close'})

        self.handle_response(response)


    def update_inputs(self):
        """
        Change inputs to ETM according to dictionary user_values. Also the
        metrics are updated by passing a gquery via gquery_metrics
        """
        put_data = {"scenario": {"user_values": self.scenario.user_values}}
        response = self.session.put(f'/scenarios/{self.scenario.id}', json=put_data,
                             headers={'Connection': 'close'})

        self.handle_response(response, fail_info=f"Error for scenario {self.scenario.short_name}")


    def update_heat_network_order(self):
        """
        Update the scenarios heat network orders in the ETM.
        """
        for network, order in self.scenario.heat_network_orders.items():
            put_data = {"order": order, "subtype": network}

            response = self.session.put(f'/scenarios/{self.scenario.id}/heat_network_order',
                                json=put_data, headers={'Connection': 'close'})

            self.handle_response(response)


    def upload_custom_curve(self, curve_key, curve_data, curve_file_name):
        """
        Upload custom curve to ETM
        """
        curve_string = '\n'.join(str(e) for e in curve_data)
        put_data = {'file': (curve_file_name, curve_string)}

        response = self.session.put(f'/scenarios/{self.scenario.id}/custom_curves/{curve_key}',
                             files=put_data, headers={'Connection': 'close'})

        self.handle_response(response)


    # RESPONSES ---------------------------------------------------------------


    def handle_response(self, response, fail_info=''):
        '''
        Lets sucessful responses through, prints errors and exits when response is bad
        '''
        if response.ok:
            return

        if response.status_code == 404:
            fail_info += f'Scenario {self.scenario.short_name} was not found.'

        if response.status_code == 403:
            fail_info += (
                "You don't have access to this scenario. " +
                "Please update your personal token (see the online docs)."
            )

        with suppress(JSONDecodeError):
            fail_info += '\n ' + ',\n '.join(response.json()['errors'])

        exit(fail_info)


    def handle_data_download_response(self, response, download_name):
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            exit("Something went wrong retrieving a data download. "
                  "Check your data_downloads.csv!\n", err=err)

        if response.text.startswith('<!DOCTYPE html>'):
            exit(f'Download "{download_name}" is not available for scenarios '
                    'with Merit turned off. Aborting...\n')


    #  PRIVATE ----------------------------------------------------------------


    def _get_downloads(self, download_names, hourly=False):
        '''Downloads and yields all requested files'''
        for download in download_names:
            yield (download, self.get_data_download(download, hourly=hourly))


    def _check_and_update_user_values(self):
        '''Checks if user values should be updated, and updates them'''
        if not self.scenario.user_values: return

        print(" Setting sliders")
        self.update_inputs()


    def _check_and_update_heat_network(self):
        '''Checks if heat network should be updated, and updates it'''
        if not self.scenario.heat_network_orders: return

        print(" Setting heat network order")
        self.update_heat_network_order()


    def _check_and_update_curves(self, curve_file_dict):
        '''Checks if curve files should be updated, and uploads them'''
        if not self.scenario.curve_file: return

        curves = curve_file_dict[self.scenario.curve_file].curves
        print(f" Uploading {len(curves)} custom curves:")
        for curve in curves:
            print(f"  - {curve.key}")
            self.upload_custom_curve(curve.key, curve.data, self.scenario.curve_file)


    def _check_and_update_heat_demand(self, curve_file_dict=None):
        '''Checks if heat demand should be updated, and updates it'''
        if not self.scenario.heat_demand or not self.scenario.heat_demand_curves:
            return

        print(' Generating and uploading weather curves, this may take a while:')
        if curve_file_dict:
            for curve_key, curve in curve_file_dict.items():

                if not curve.data.any():
                    print(f"Curve {curve_key} has no data to upload.") # Final check
                    continue
                # Upload each curve
                self.upload_custom_curve(f'weather/{curve.key}', curve.data, curve.key)
                print(f"  - Uploaded {curve_key}")
        else:
            for curve in self.scenario.heat_demand_curves:
                if not curve.data.any():
                    print(f"Curve {curve.key} has no data to upload.")
                    continue
                curve.to_csv(self.scenario.short_name)
                # Upload each curve
                self.upload_custom_curve(f'weather/{curve.key}', curve.data, curve.key)
                print(f"  - Uploaded {curve.key}")
