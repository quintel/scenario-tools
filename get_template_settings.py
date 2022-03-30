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

    templates.to_csv()
