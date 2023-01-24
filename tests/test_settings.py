from unittest.mock import patch
from pathlib import Path

from helpers.settings import Settings

def test_settings_loaded():
    assert Settings.get('local_engine_url') is not None
    assert Settings.get('bullshit') is None


def test_add_setting():
    Settings.add('new_setting', 'my_value')

    assert Settings.get('new_setting') == 'my_value'


def test_local_settings():
    # Hack the current settings away so we can patch the fixture
    Settings.instance = None

    with patch('helpers.settings.BASE_PATH', Path('tests/fixtures/config')):
        assert Settings.get('local_engine_url') is not None
        assert Settings.get('bullshit') is None

        # Only exists in local settings
        assert Settings.get('personal_etm_token') == "1234-5678-90"
