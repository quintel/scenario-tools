# system modules
import sys

# external modules
import io
import json
import pandas as pd
import requests


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
    to a single scenario which is identified by the scenario_id. Via the api we
    can request key parameters as shown by the ETM and we can also change
    various input parameters.
    """

    def __init__(self, session, scenario_id=None):
        self.session = session
        self.scenario_id = scenario_id


    def return_gqueries(self,p):
        """
        Extracts information from object p by first converting to JSON and
        then to a pandas dataframe.
        """
        p_json = p.json()
        p_gqueries = p_json["gqueries"]
        df = pd.DataFrame.from_dict(p_gqueries, orient = "index")
        return df


    def get_energy_flows(self):
        """
        """
        energy_flows = self.session.get(f"/scenarios/{self.scenario_id}/energy_flow").content
        df = pd.read_csv(io.StringIO(energy_flows.decode('utf-8')))
        return df


    def get_application_demands(self):
        """
        """
        application_demands = self.session.get(f"/scenarios/{self.scenario_id}/application_demands").content
        df = pd.read_csv(io.StringIO(application_demands.decode('utf-8')))
        return df


    def get_production_parameters(self):
        """
        """
        production_parameters = self.session.get(f"/scenarios/{self.scenario_id}/production_parameters").content
        df = pd.read_csv(io.StringIO(production_parameters.decode('utf-8')))
        return df


    def get_hourly_electricity_curves(self):
        """
        """
        electricity_curves = self.session.get(f"/scenarios/{self.scenario_id}/curves/merit_order").content
        df = pd.read_csv(io.StringIO(electricity_curves.decode('utf-8')))
        return df


    def get_hourly_electricity_price_curve(self):
        """
        """
        electricity_price_curve = self.session.get(f"/scenarios/{self.scenario_id}/curves/electricity_price").content
        df = pd.read_csv(io.StringIO(electricity_price_curve.decode('utf-8')))
        return df


    def get_hourly_household_heat_curves(self):
        """
        """
        household_heat_curves = self.session.get(f"/scenarios/{self.scenario_id}/curves/household_heat").content
        df = pd.read_csv(io.StringIO(household_heat_curves.decode('utf-8')))
        return df


    def get_hourly_gas_curves(self):
        """
        Get data export for hourly network gas curves
        """
        network_gas_curves = self.session.get(f"/scenarios/{self.scenario_id}/curves/network_gas").content
        df = pd.read_csv(io.StringIO(network_gas_curves.decode('utf-8')))
        return df


    def get_hourly_hydrogen_curves(self):
        """
        Get data export for hourly hydrogen curves
        """
        hydrogen_curves = self.session.get(f"/scenarios/{self.scenario_id}/curves/hydrogen").content
        df = pd.read_csv(io.StringIO(hydrogen_curves.decode('utf-8')))
        return df


    def get_hourly_heat_network_curves(self):
        """
        Get data export for hourly heat network curves
        """
        heat_network_curves = self.session.get(f"/scenarios/{self.scenario_id}/curves/heat_network").content
        df = pd.read_csv(io.StringIO(heat_network_curves.decode('utf-8')))
        return df


    def get_scenario_templates(self):
        """
        Get dataframe of available templates within the ETM. From this, a
        scenario id can be extracted. Note that not all scenario ids seem
        to work.
        """
        r = self.session.get("/scenarios/templates")
        self.df_templates = pd.DataFrame.from_dict(r.json())
        pass


    def create_new_scenario(self, scenario_title, area_code, end_year):
        """
        Create a new scenario in the ETM. The scenario_id is saved so we can
        continue from the new scenario later on.
        """
        post_data = {
                     "scenario":
                               {
                               "title": scenario_title,
                               "area_code": area_code,
                               "end_year": end_year,
                               "protected": True
                               }
                     }
        p = self.session.post("/scenarios", json = post_data,
                                                headers={'Connection':'close'})
        df_scenario = pd.DataFrame.from_dict(p.json(), orient = "index")
        self.scenario_id = df_scenario.loc["id"].values[0]
        pass


    def reset_scenario(self):
        """
        Resets scenario with scenario_id
        """
        put_data = {"reset": True}
        p = self.session.put('/scenarios/' + self.scenario_id, json = put_data,
                                                headers={'Connection':'close'})
        self.current_metrics = self.return_gqueries(p)
        pass


    def get_inputs(self):
        """
        Get list of available inputs. Can be used to search parameter space?
        """
        p = self.session.get('/scenarios/' + self.scenario_id + "/inputs",
                                                headers={'Connection':'close'})
        p_json = p.json()
        self.df_inputs = pd.DataFrame.from_dict(p_json, orient = "index")

        pass


    def get_current_metrics(self, gquery_metrics):
        """
        Perform a gquery on the the ETM model. gquery_metrics is a list of
        available ggueries.
        """
        put_data = {
                   "detailed": True,
                   "gqueries": gquery_metrics
                   }

        p = self.session.put('/scenarios/' + self.scenario_id, json = put_data,
                                                headers={'Connection':'close'})
        self.current_metrics = self.return_gqueries(p)
        return self.current_metrics


    def change_inputs(self, user_values):
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
        p = self.session.put(f'/scenarios/{self.scenario_id}', json = put_data,
                                                headers={'Connection':'close'})

        if p.status_code != requests.codes.ok:
          print(json.dumps(p.json(), indent=4, sort_keys=True))
          sys.exit(1)
