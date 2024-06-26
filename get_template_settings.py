# external modules
import sys

# project modules
from helpers.ETM_API import ETM_API, SessionWithUrlBase
from helpers.helpers import process_arguments, print_bold
from helpers.Template import TemplateCollection

if __name__ == "__main__":

    base_url, _,_,complete_mode = process_arguments(sys.argv)

    session = SessionWithUrlBase(base_url)

    print("Opening CSV file(s):")
    templates = TemplateCollection.from_csv()
    print(f"\nProcessing {len(templates.collection)} scenarios..")
    if complete_mode:
        print_bold("\n'Complete' mode is enabled. Scenario "
                   "user values, balanced values, custom orders and "
                   "custom curves will be obtained.")
    else:
        print_bold("\nScenario user value settings will be obtained")
    
    for index, template in enumerate(templates, start=1):
        print(f"\nProcessing scenario template \"{template.title}\" ({index} of {len(templates.collection)} scenarios)")
        API_template = ETM_API(session, template)
        template.add_user_values(API_template.get_scenario_settings())
        
        if complete_mode:
            template.add_balanced_values(API_template.get_scenario_settings(settings_type='balanced_values'))

            print('Obtaining heat network orders')
            template.add_heat_network_orders(API_template.get_heat_network_orders(template.heat_orders))
        
            print("Obtaining custom curve CSVs")
            template.add_custom_curves(API_template.get_custom_curves())
            template.custom_curves_to_csv()

            print("Obtaining custom orders CSVs")
            template.add_custom_orders(API_template.get_custom_orders(template.custom_orders))
            template.custom_orders_to_csv()
    
    templates.to_csv('template_settings')

    if complete_mode:
        # Set to false to obtain balanced values
        templates.to_csv('template_settings_balanced_values', user_values=False)
        templates.heat_network_orders_to_csv()
    
    print("\nDone!")
