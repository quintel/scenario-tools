import sys
import io
import json
import pandas as pd
import requests
from pathlib import Path


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
        p_json = p.json()
        p_gqueries = p_json["gqueries"]
        df = pd.DataFrame.from_dict(p_gqueries, orient="index")
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
            print(" Setting scenario title")
            scenario_dict["title"] = scenario_title

        if description:
            print(" Setting scenario description")
            scenario_dict["description"] = description

        if protected:
            print(f" Setting protected property to {protected}")
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

    def change_inputs(self, user_values, short_name):
        """
        Change inputs to ETM according to dictionary user_values. Also the
        metrics are updated by passing a gquery via gquery_metrics
        """
        put_data = {
            "scenario": {
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

        p = self.session.put(f'/scenarios/{self.id}/flexibility_order',
                             json=put_data, headers={'Connection': 'close'})

        if p.status_code != requests.codes.ok:
            print(json.dumps(p.json(), indent=4, sort_keys=True))
            sys.exit(1)

    def change_heat_network_order(self, heat_network_order):
        """
        Change heat network order to ETM according to object heat_network_order.
        """
        put_data = {"heat_network_order": {"order": heat_network_order}}

        p = self.session.put(f'/scenarios/{self.id}/heat_network_order',
                             json=put_data, headers={'Connection': 'close'})

        if p.status_code != requests.codes.ok:
            print(json.dumps(p.json(), indent=4, sort_keys=True))
            sys.exit(1)

    def get_query_results(self, query_list):
        """
        Perform gqueries on the ETM.
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

    def get_data_download(self, download_name, hourly=False):
        """
        Collect a data download from the ETM. A data download is
        a set of data predefined by the ETM.
        """
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

    def export_scenario_data_downloads(self, short_name, download_dict):
        """
        Export data downloads to CSV files.
        """
        root = Path(__file__).parents[1]
        output_path = root / Path(f"data/output/{short_name}")
        output_path.mkdir(parents=True, exist_ok=True)

        for download in download_dict["annual_data"]:
            df = self.get_data_download(download)
            df.to_csv(f"{output_path}/{download}.csv")

        for download in download_dict["hourly_data"]:
            df = self.get_data_download(download, hourly=True)
            df.to_csv(f"{output_path}/{download}.csv")

    def upload_custom_curve(self, curve_key, curve_data, curve_file_name):
        """
        Upload custom curve to ETM
        """
        curve_string = '\n'.join(str(e) for e in curve_data)
        put_data = {'file': (curve_file_name, curve_string)}

        p = self.session.put(f'/scenarios/{self.id}/custom_curves/{curve_key}',
                             files=put_data, headers={'Connection': 'close'})

        if p.status_code != requests.codes.ok:
            print(json.dumps(p.json(), indent=4, sort_keys=True))
            sys.exit(1)

    def initialise_scenario(self, scenario):
        if not scenario.id:
            self.create_new_scenario(
                scenario.title,
                scenario.area_code,
                scenario.end_year)

            scenario.id = self.id

        else:
            self.id = scenario.id

    def update_scenario(self, scenario, curve_file_dict):
        self.update_scenario_properties(
             scenario.title,
             scenario.description,
             scenario.protected)

        if scenario.user_values:
            print(" Setting sliders")
            self.change_inputs(scenario.user_values, scenario.short_name)

        if scenario.flexibility_order:
            print(" Setting flexibility order")
            self.change_flexibility_order(scenario.flexibility_order)

        if scenario.heat_network_order:
            print(" Setting heat network order")
            self.change_heat_network_order(scenario.heat_network_order)

        if scenario.curve_file:
            print(" Uploading custom curves:")
            for curve in curve_file_dict[scenario.curve_file].curves:
                print(f"  - {curve.key}")
                self.upload_custom_curve(curve.key, curve.data,
                                         scenario.curve_file)

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
