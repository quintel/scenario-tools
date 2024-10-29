from helpers.file_helpers import read_csv

class InsulationConfig():
    INSULATION_TYPES = ["low", "medium", "high"]
    HOUSE_NAMES = [
        "terraced_houses", "semi_detached_houses", "apartments", "detached_houses"
        ]

    J_TO_KWH = 2.77778e-7
    CM2_TO_M2 = 1e-4

    # R-values used for nl2019 [m^2 K / W]
    R_VALUES = {
        "terraced_houses": {"low": 0.72608224, "medium": 0.95303516, "high": 2.20833951},
        "semi_detached_houses": {"low": 0.92629934, "medium": 1.20779267, "high": 2.90413756},
        "apartments": {"low": 0.96937942, "medium": 1.39716924, "high": 2.95000949},
        "detached_houses": {"low": 1.02227109, "medium": 1.2962618, "high": 3.10765405}
    }

    SURFACE_AREA = {
        "terraced_houses": 183,
        "semi_detached_houses": 279,
        "apartments": 187,
        "detached_houses": 405
    }

    # Fitting number used for nl2019
    BEHAVIOUR_FITTING_RESULTS = {
        "terraced_houses": {'low': 0.44224575, 'medium': 2.61042431, 'high': 0.59483274},
        "semi_detached_houses":  {'low': 1.57962902, 'medium': 4.43499574, 'high': 0.45485638},
        "apartments": {'low': -0.11691841, 'medium': 0.80467653, 'high': 2.78210071},
        "detached_houses": {'low': 3.34031291, 'medium': 7.76537119, 'high': 2.74614981}
    }

    def __init__(self):
        '''Config for all insulation data'''
        self.__set_heat_capacity_house()
        self.curve_keys = curve_keys = [
            f'insulation_{house}_{insulation}'
                for insulation in self.INSULATION_TYPES
                for house in self.HOUSE_NAMES
        ]

    def __set_heat_capacity_house(self):
        '''Calculate and set the heat capactity of the house in kWh / K'''
        # Material constants
        density_concrete = 2400.0 # kg / m**3 (https://en.wikipedia.org/wiki/Properties_of_concrete)
        specific_heat_capacity_concrete = 880.0 # J / kg K (https://www.designingbuildings.co.uk/wiki/Specific_heat_capacity)

        R_c = 0.76 # [m^2 K / W]
        width = 8.0 #m
        height = 4.0 #m
        wall_thickness = 0.025
        roof_area = width * width
        wall_area = width * height
        self.window_area = roof_area * 0.1

        surface_area = wall_area * 4 + roof_area # m^2 Assuming a square house with a flat roof for now
        kg_of_concrete = surface_area * wall_thickness * density_concrete # cubic meter of wall times the specific weight of concrete

        self.heat_capacity_house = specific_heat_capacity_concrete * self.J_TO_KWH * kg_of_concrete

    def get_r_values(self, house_type=None, setting=None):
        if house_type and setting:
            return self.R_VALUES[house_type][setting]
        if house_type:
            return self.R_VALUES[house_type]

        return self.R_VALUES

    def get_heat_capacity(self, house_type=None):
        '''How much energy does it take to heat the house one K? Same for all house types'''
        return self.heat_capacity_house

    def get_surface_area(self, house_type=None):
        if house_type:
            return self.SURFACE_AREA[house_type]

        return self.SURFACE_AREA

    def get_window_area(self, house_type=None):
        window_areas = {
            'terraced_houses': 6.08289109,
            'apartments': 5.53039382,
            'semi_detached_houses': 5.80327128,
            'detached_houses': 6.12774164
        }

        if house_type:
            return window_areas.get(house_type, self.window_area)

        return {house: self.window_area for house in self.HOUSE_NAMES}


    def get_behaviour(self, house_type=None, setting=None):
        if house_type and setting:
            return self.BEHAVIOUR_FITTING_RESULTS[house_type][setting]
        if house_type:
            return self.BEHAVIOUR_FITTING_RESULTS[house_type]

        return self.BEHAVIOUR_FITTING_RESULTS

    def from_J_cm2_to_Kwh_m2(self, curve):
        return curve * self.J_TO_KWH / self.CM2_TO_M2


insulation_config = InsulationConfig()
