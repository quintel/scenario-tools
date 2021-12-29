from helpers.settings import Settings

def test_settings_loaded():
    assert Settings.get('local_engine_url') is not None
    assert Settings.get('bullshit') is None


def test_add_setting():
    Settings.add('new_setting', 'my_value')

    assert Settings.get('new_setting') == 'my_value'
