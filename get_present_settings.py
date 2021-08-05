# external modules
import sys

# project modules
from helpers.ETM_API import ETM_API, SessionWithUrlBase
from helpers.helpers import (process_arguments,
                             generate_area_list)

from helpers.file_helpers import export_present_settings

if __name__ == "__main__":

    base_url, model_url, query_only_mode = process_arguments(sys.argv)

    session = SessionWithUrlBase(base_url)

    print("Opening CSV file(s):")
    areas = generate_area_list()

    for area_code in areas:
        print(f"\nProcessing area \"{area_code}\"..")
        API_area = ETM_API(session)
        API_area.create_new_scenario(
            f"Empty scenario for {area_code}",
            area_code,
            2050)
        present_settings = API_area.get_inputs()
        export_present_settings(area_code, present_settings)
