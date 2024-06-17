
### local imports

from ..config import APP_REFS

from ..ourstdlibs.pyl import save_pyl

from ..dialog import create_and_show_dialog

from .main import USER_PREFS, CONFIG_FILEPATH

from .constants import TEST_SESSION_SETTINGS_KEY



def save_test_settings_if_needed(tests_report_data):

    if not APP_REFS.system_testing_set:
        return

    APP_REFS.system_testing_set = False

    test_session_settings = {
        'test_cases_ids': tuple(tests_report_data['requested_cases']),
        'playback_speed': tests_report_data['playback_speed'],
    }

    if (
        TEST_SESSION_SETTINGS_KEY not in USER_PREFS
        or test_session_settings != USER_PREFS[TEST_SESSION_SETTINGS_KEY]
    ):

        USER_PREFS[TEST_SESSION_SETTINGS_KEY] = test_session_settings

        try:
            save_pyl(USER_PREFS, CONFIG_FILEPATH)

        except Exception:

            create_and_show_dialog(
                "Something wen't wrong when trying to save test session"
                " settings (for reuse)."
            )
