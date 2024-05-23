# external modules
import sys

# project modules
from helpers.ETM_API import ETM_API, SessionWithUrlBase
from helpers.helpers import process_arguments
from helpers.Template import TemplateCollection

if __name__ == "__main__":

    base_url, model_url, query_only_mode = process_arguments(sys.argv)

    session = SessionWithUrlBase(base_url)

    print("Opening CSV file(s):")
    templates = TemplateCollection.from_csv()

    for template in templates:
        print(f"\nProcessing scenario template \"{template.title}\"..")
        API_template = ETM_API(session, template)
        template.add_user_values(API_template.get_scenario_settings())

        #TODO: Add getting curves

        #TODO: Add getting orders: heat_network_order
        template.add_heat_network_order(API_template.get_heat_network_order())
        # print(template.heat_network_order)
        

    templates.to_csv()
