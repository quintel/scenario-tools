EXISTING_SCENARIOS = {
    '2030_klimaatakkoord': { 'id': '764454' },
    '2050_regionale_sturing': { 'id': '764455' },
    '2050_nationale_sturing': { 'id': '764457' },
    '2050_europese_sturing': { 'id': '764459' },
    '2050_internationale_sturing': { 'id': '764460' }
}

NEW_SCENARIOS = {
    '2030_klimaatakkoord': {
        'title': f"Systeemstudie Zuid-Holland 2030 v1",
        'area_code': 'PV28_zuid_holland',
        'short_name': 'Systeemstudie Zuid-Holland 2030 v1',
        'end_year': '2030',
        'description': 'Systeemstudie Zuid-Holland 2030 v1',
        'id': 764454,
        'user_values': {},
        'flexibility_order': [],
        'heat_network_order': []
    },
    '2050_regionale_sturing': {
        'title': f"Systeemstudie Zuid-Holland 2050 - regionale sturing v1",
        'area_code': 'PV28_zuid_holland',
        'short_name': '2050_regionale_sturing_v1',
        'end_year': '2050',
        'description': 'Systeemstudie Zuid-Holland 2050 - regionale sturing v1',
        'id': 764455,
        'user_values': {},
        'flexibility_order': [
            "power_to_heat_industry",
            "electric_vehicle",
            "power_to_gas",
            "export"],
        'heat_network_order': [
            "energy_heat_heatpump_water_water_electricity",
            "energy_heat_burner_wood_pellets",
            "energy_heat_network_storage",
            "energy_heat_burner_network_gas"]
    },
    '2050_nationale_sturing': {
        'title': f"Systeemstudie Zuid-Holland 2030 - nationale sturing v1",
        'area_code': 'PV28_zuid_holland',
        'short_name': '2050_nationale_sturing_v1',
        'end_year': '2050',
        'description': 'Systeemstudie Zuid-Holland 2030 - nationale sturing v1',
        'id': 764457,
        'user_values': {},
        'flexibility_order': [
            "power_to_heat_industry",
            "power_to_heat_district_heating_heatpump",
            "power_to_gas",
            "export"],
        'heat_network_order': [
            "energy_heat_burner_waste_mix",
            "energy_heat_heatpump_water_water_electricity",
            "energy_heat_burner_wood_pellets",
            "energy_heat_network_storage",
            "energy_heat_burner_network_gas"]
    },
    '2050_europese_sturing': {
        'title': f"Systeemstudie Zuid-Holland 2030 - europese sturing v1",
        'area_code': 'PV28_zuid_holland',
        'short_name': '2050_europese_sturing_v1',
        'end_year': '2050',
        'description': 'Systeemstudie Zuid-Holland 2030 - europese sturing v1',
        'id': 764459,
        'user_values': {},
        'flexibility_order': [
            "power_to_heat_industry",
            "power_to_heat_district_heating_boiler",
            "power_to_gas",
            "export"],
        'heat_network_order': [
            "energy_heat_burner_waste_mix",
            "energy_heat_heatpump_water_water_electricity",
            "energy_heat_burner_wood_pellets",
            "energy_heat_network_storage",
            "energy_heat_burner_network_gas",
            "energy_heat_burner_hydrogen"]
    },
    '2050_internationale_sturing': {
        'title': f"Systeemstudie Zuid-Holland 2030 - internationale sturing v1",
        'area_code': 'PV28_zuid_holland',
        'short_name': '2050_internationale_sturing_v1',
        'end_year': '2050',
        'description': 'Systeemstudie Zuid-Holland 2030 - internationale sturing v1',
        'id': 764460,
        'user_values': {},
        'flexibility_order': [
            "power_to_heat_industry",
            "electric_vehicle",
            "power_to_gas",
            "export"],
        'heat_network_order': [
            "energy_heat_burner_waste_mix",
            "energy_heat_heatpump_water_water_electricity",
            "energy_heat_burner_wood_pellets",
            "energy_heat_network_storage",
            "energy_heat_burner_hydrogen",
            "energy_heat_burner_network_gas"]
    },
}