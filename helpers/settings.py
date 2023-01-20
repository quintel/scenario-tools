from pathlib import Path

import yaml

BASE_PATH = Path('config')

class Settings:
    '''Singleton class containing the settings from settings.yml'''
    class __Settings:
        def __init__(self, settings):
            self.settings = settings

        @classmethod
        def load(cls):
            return cls(
                cls.read_file(BASE_PATH / 'settings.yml') |
                cls.read_file(BASE_PATH / 'local.settings.yml')
            )

        @staticmethod
        def read_file(file: Path):
            if not file.exists(): return {}

            with open(file, 'r') as f:
                doc = yaml.load(f, Loader=yaml.FullLoader)

            return doc


    instance = None

    def __init__(self):
        if not Settings.instance:
            Settings.instance = Settings.__Settings.load()

    @classmethod
    def add(cls, setting, value):
        '''Add a setting, look out for overwriting!'''
        cls().instance.settings[setting] = value

    @classmethod
    def get(cls, setting):
        '''Will return the value for the requested setting'''
        return cls().instance.settings.get(setting, None)
