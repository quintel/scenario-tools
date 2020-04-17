EXISTING_SCENARIOS = {
    'regionaal': { 'id': '754910' },
    'nationaal': { 'id': '754911' },
    'europees': { 'id': '754912' },
    'internationaal': { 'id': '754913' }
}

NEW_SCENARIOS = {
    'II3050 Regionaal - Solar PV en Warmtenet fix -': {
        'title': f"II3050 Regionaal - Solar PV en Warmtenet fix -",
        'area_code': 'nl',
        'short_name': 'NL_Regionaal_2050_fix',
        'end_year': '2050',
        'id': None,
        'user_values': {},
        'flexibility_order': [
            "mv_batteries",
            "household_batteries",
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
    'II3050 Nationaal - Solar PV en Warmtenet fix -': {
        'title': f"II3050 Nationaal - Solar PV en Warmtenet fix -",
        'area_code': 'nl',
        'short_name': 'NL_Nationaal_2050_fix',
        'end_year': '2050',
        'id': None,
        'user_values': {},
        'flexibility_order': [],
        'heat_network_order': []
    },
    'II3050 Europees - Solar PV en Warmtenet fix -': {
        'title': f"II3050 Europees - Solar PV en Warmtenet fix -",
        'area_code': 'nl',
        'short_name': 'NL_Europees_2050_fix',
        'end_year': '2050',
        'id': None,
        'user_values': {},
        'flexibility_order': [],
        'heat_network_order': []
    },
    'II3050 Internationaal - Solar PV en Warmtenet fix -': {
        'title': f"II3050 Internationaal - Solar PV en Warmtenet fix -",
        'area_code': 'nl',
        'short_name': 'NL_Internationaal_2050_fix',
        'end_year': '2050',
        'id': None,
        'user_values': {},
        'flexibility_order': [],
        'heat_network_order': []
    }
}
