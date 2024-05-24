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
        template.add_custom_curves(API_template.get_custom_curves())
        print(template.custom_curves)
        template.custom_curves.to_csv(f"data/output/{template.title}_curves.csv", index=False)

        #TODO: Orders: combine in 1 CSV output

        # Heat network order
        # heat_levels = ['ht', 'mt', 'lt']
        # for l in heat_levels:
        #     template.add_heat_network_orders(API_template.get_heat_network_order(subtype=l), subtype=l)
        # df = template.get_heat_network_orders_csv(heat_levels)
        # df.to_csv(f'data/output/heat_network_orders.csv')

        # Hydrogen supply and demand order
        # hydrogen_types = ['supply', 'demand']
        # for t in hydrogen_types:
        #     template.add_hydrogen_orders(API_template.get_hydrogen_orders(subtype=t), subtype=t)
        # df = template.get_hydrogen_orders_csv(hydrogen_types)
        # df.to_csv(f'data/output/hydrogen_orders.csv')


        # Forecast storage order
        # template.add_forecasting_storage_order(API_template.get_forecast_storage_order())
        # df = template.get_forecasting_storage_order_csv()
        # df.to_csv(f'data/output/forecasting_storage_order.csv')


        # households_space_heating_producer_order order
        # template.add_households_space_heating_producer_order(API_template.get_households_space_heating_producer_order())
        # df = template.get_households_space_heating_producer_order_csv()
        # df.to_csv(f'data/output/households_space_heating_producer_order.csv')


    # templates.to_csv()
