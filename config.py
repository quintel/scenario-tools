EXISTING_SCENARIOS = {
    'regionaal': { 'id': '754910' },
    'nationaal': { 'id': '754911' },
    'europees': { 'id': '754912' },
    'internationaal': { 'id': '754913' }
}

NEW_SCENARIOS = {
    '2030_example': {
        'title': f"Example scenario for TenneT (2030)",
        'area_code': 'nl',
        'short_name': 'NL_2030_example_TenneT',
        'end_year': '2030',
        'id': None,
        'user_values': {},
        'flexibility_order': [
        "household_batteries",
            "mv_batteries",
            "electric_vehicle",
            "opac",
            "pumped_storage",
            "power_to_gas",
            "power_to_heat_industry",
            "power_to_heat_district_heating_boiler",
            "power_to_heat_district_heating_heatpump",
            "power_to_kerosene",
            "export",
        ],
        'heat_network_order': [
            "energy_heat_burner_wood_pellets",
            "energy_heat_network_storage",
            "energy_heat_burner_waste_mix",
            "energy_heat_heatpump_water_water_electricity",
            "energy_heat_burner_coal",
            "energy_heat_burner_network_gas",
            "energy_heat_burner_crude_oil",
            "energy_heat_burner_hydrogen",
        ]
    },
    '2050_example': {
        'title': f"Example scenario for TenneT (2050)",
        'area_code': 'nl',
        'short_name': 'NL_2050_example_TenneT',
        'end_year': '2050',
        'id': None,
        'user_values': {},
        'flexibility_order': [],
        'heat_network_order': []
    }
}
