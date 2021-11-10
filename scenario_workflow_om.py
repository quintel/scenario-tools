import os
import sys

import openpyxl

import get_present_settings
import get_template_settings
import scenario_from_csv


def call():
    get_area()
    get_templates()
    create_scenario()


def get_area():
    """
    1) Copy-paste areas.csv from Excel into the data/input directory
    2) Get present settings for area and copy-paste those back into Excel
    """

    # Copy-paste area into the areas.csv file in the data/input directory

    # Get present settings
    get_present_settings.call()

    # Based on area name find the present settings file

    # Copy-paste present settings into the Excel (sheet "Startwaarden")


def get_templates():
    """
    1) Copy-paste template_settings.csv from Excel into the data/input directory
    2) Get template settings and copy-paste those back into Excel
    """

    # Copy-paste template_settings.csv file into the data/input directory

    # Get template settings
    get_template_settings.call()

    # Based on template name, create new or update existing sheets in the Excel


def create_scenario():
    """
    """

    # Copy-paste scenario_list.csv and scenario_settings.csv from Excel into
    # the data/input directory

    # Create scenario
    scenario_from_csv.call()

    # Copy-paste scenario_list.csv back into Excel


if __name__ == "__main__":
    call()
