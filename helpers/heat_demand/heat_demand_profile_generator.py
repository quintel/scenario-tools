'''Module that generates heat demand profiles'''

from .house import House
from .config import insulation_config
from helpers.Curves import Curve

import helpers.heat_demand.smoothing as smoothing

# General constants
HOURS = 8760
HOURS_PER_DAY = 24

def generate_profiles(temp, irr):
    '''
    Generates profiles for the heat demand of the five house types for three
    insulation types, resulting in 5 * 3 = 15 profiles. These profiles can be used to upload to
    the ETM.

    Params:
        temp (np.array | pd.Series): Outside temperature curve of length 8760
        irr (np.array | pd.Series): Solar irradiation curve of length 8760

    Returns:
        generator (Curve)
    '''
    irr = insulation_config.from_J_cm2_to_Kwh_m2(irr)

    for house_type in insulation_config.HOUSE_NAMES:
        for insulation_type in insulation_config.INSULATION_TYPES:
            curve_name = f'insulation_{house_type}_{insulation_type}'
            yield Curve(curve_name, heat_demand_curve(house_type, insulation_type, temp, irr))

def heat_demand_curve(house_type, insulation_type, temp, irr):
    '''
    Calculates the heat demand curve for a hous and insulation type

    Params:
        house_type (str): Type of house, e.g. apartments
        insulation_type (str): Level of insulation, e.g. low
        temp (np.array | pd.Series): Outside temperature curve of length 8760
        irr (np.array | pd.Series): Solar irradiation curve of length 8760

    Returns:
        np.array of length 8760 containing the heat demand curve
    '''
    house = House(house_type, insulation_type)
    return smoothe_and_aggregate(
        [heat_demand_at_hour(house, hour, temp, irr) for hour in range(HOURS)],
        insulation_type
    )


def heat_demand_at_hour(house, hour, temp, irr):
    '''
    Calculates the heat demand for the house type at the specified hour

    Params:
        house (House): The house the demand will be calculated for
        hour (int): The hour in the year
        temp (np.array): The temperature curve
        irr (np.array): The irradiation curve

    Returns:
        float value of heat demand
    '''
    # What is the wanted temperature inside?
    hour_of_the_day = hour % HOURS_PER_DAY # between 0 and 23

    return house.calculate_heat_demand(temp[hour], irr[hour], hour_of_the_day)

def smoothe_and_aggregate(curve, insulation_type):
    '''
    Smooth demand curve to turn individual household curves into average/aggregate
    curves of a whole neighbourhood
    '''
    return normalise(smoothing.calculate_smoothed_demand(curve, insulation_type))

def normalise(curve):
    '''Normalises a curve to 1/3600'''
    return curve / sum(curve) / 3600
