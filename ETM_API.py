# system modules
import os
import sys

# external modules
import io
import json
import pandas as pd
import requests
import struct


class SessionWithUrlBase(requests.Session):
    """
    Helper class to store the base url. This allows us to only type the
    relevant additional information.
    from: https://stackoverflow.com/questions/42601812/python-requests-url-base-in-session
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
        p_json = p.json()
        p_gqueries = p_json["gqueries"]
        df = pd.DataFrame.from_dict(p_gqueries, orient="index")
        return df

    def get_data_download(self, download_name, hourly=False):
        if hourly:
            suffix = f'curves/{download_name}'
        else:
            suffix = download_name

        file = self.session.get(f"/scenarios/{self.id}/{suffix}")
        try:
            file.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("Something went wrong retrieving a data download. "
                  "Check your data_downloads.csv!\n")
            raise SystemExit(err)

        df = pd.read_csv(io.StringIO(file.content.decode('utf-8')))
        return df

    def create_new_scenario(self, scenario_title, area_code, end_year):
        """
        Create a new scenario in the ETM. The id is saved so we can
        continue from the new scenario later on.
        """
        post_data = {
            "scenario":
            {
                "title": scenario_title,
                "area_code": area_code,
                "end_year": end_year
            }
        }
        p = self.session.post("/scenarios", json=post_data,
                              headers={'Connection': 'close'})

        if p.status_code != requests.codes.ok:
            print(json.dumps(p.json(), indent=4, sort_keys=True))
            sys.exit(1)

        df_scenario = pd.DataFrame.from_dict(p.json(), orient="index")
        self.id = df_scenario.loc["id"].values[0]

        pass

    def update_scenario_properties(self, scenario_title, description, protected):
        """
        Update scenario properties such as title and description
        """

        scenario_dict = {}

        if scenario_title:
            scenario_dict["title"] = scenario_title

        if description:
            scenario_dict["description"] = description

        if protected:
            scenario_dict["protected"] = protected

        put_data = {
            "scenario": scenario_dict
        }
        p = self.session.put(f"/scenarios/{self.id}", json=put_data,
                             headers={'Connection': 'close'})

        if p.status_code != requests.codes.ok:
            print(json.dumps(p.json(), indent=4, sort_keys=True))
            sys.exit(1)

        pass

    def get_query_results(self, query_list):
        """
        Perform a gquery on the the ETM model. query_list is a list of
        available ggueries.
        """
        put_data = {
            "detailed": True,
            "gqueries": query_list
        }

        p = self.session.put(f'/scenarios/{self.id}', json=put_data,
                             headers={'Connection': 'close'})

        if p.status_code != requests.codes.ok:
            print("Error retrieving queries. Please check your queries.csv.\n")
            print(json.dumps(p.json(), indent=4, sort_keys=True))
            sys.exit(1)
        else:
            self.query_results = self.return_gqueries(p)
            return self.query_results

    def change_inputs(self, user_values, short_name):
        """
        Change inputs to ETM according to dictionary user_values. Also the
        metrics are updated by passing a gquery via gquery_metrics
        """
        put_data = {
            "scenario":
            {
                "user_values": user_values
            },
            "detailed": True
        }
        p = self.session.put(f'/scenarios/{self.id}', json=put_data,
                             headers={'Connection': 'close'})

        if p.status_code != requests.codes.ok:
            print(f"Error for scenario {short_name}")
            print(json.dumps(p.json(), indent=4, sort_keys=True))
            sys.exit(1)

    def change_flexibility_order(self, flexibility_order):
        """
        Change flexibility order to ETM according to object flexibility_order.
        """
        put_data = {"flexibility_order": {"order": flexibility_order}}

        p = self.session.put(f'/scenarios/{self.id}/flexibility_order', json=put_data, headers={'Connection': 'close'})

        if p.status_code != requests.codes.ok:
            print(json.dumps(p.json(), indent=4, sort_keys=True))
            sys.exit(1)

    def change_heat_network_order(self, heat_network_order):
        """
        Change heat network order to ETM according to object heat_network_order.
        """
        put_data = {"heat_network_order": {"order": heat_network_order}}

        p = self.session.put(f'/scenarios/{self.id}/heat_network_order', json=put_data, headers={'Connection': 'close'})

        if p.status_code != requests.codes.ok:
            print(json.dumps(p.json(), indent=4, sort_keys=True))
            sys.exit(1)

    def upload_custom_curve(self, curve_key, curve_data, curve_name):
        """
        Upload custom curve to ETM
        """
        curve_string = '\n'.join(str(e) for e in curve_data)
        put_data = {'file': (curve_name, curve_string)}

        p = self.session.put(f'/scenarios/{self.id}/custom_curves/{curve_key}', files=put_data, headers={'Connection': 'close'})

        if p.status_code != requests.codes.ok:
            print(json.dumps(p.json(), indent=4, sort_keys=True))
            sys.exit(1)
