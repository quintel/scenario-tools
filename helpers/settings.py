import yaml

class Settings:
    '''Singleton class containing the settings from settings.yml'''
    class __Settings:
        def __init__(self, settings):
            self.settings = settings


        @classmethod
        def load(cls):
            with open('config/settings.yml', 'r') as f:
                doc = yaml.load(f, Loader=yaml.FullLoader)
            return cls(doc)


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
