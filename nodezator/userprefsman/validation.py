"""Facility for user preferences validation."""

### local import
from .constants import TEST_SESSION_SETTINGS_KEY



AVAILABLE_LANGUAGES = (
    "English",
    "Português do Brasil",
)


KEY_ERROR_FORMATTER = ("{!r} key not present in user preferences").format


def validate_prefs_data(prefs_data):
    """Raise exception if preferences data doesn't validate."""
    ### ensure preferences data is a dict

    if not isinstance(prefs_data, dict):
        raise TypeError("Preferences data must be a dictionary.")

    ### integers >= 0

    for key in (
        "USER_LOGGER_MAX_LINES",
        "CUSTOM_STDOUT_MAX_LINES",
        "NUMBER_OF_BACKUPS",
    ):

        if key not in prefs_data:
            raise KeyError(KEY_ERROR_FORMATTER(key))

        value = prefs_data[key]

        if not isinstance(value, int) or not value >= 0:
            raise TypeError(f"{repr(key)} key must be 'int' >= 0")

    ### available languages

    lang_key = "LANGUAGE"

    if lang_key not in prefs_data:
        raise KeyError(KEY_ERROR_FORMATTER(lang_key))

    lang_value = prefs_data[lang_key]

    if lang_value not in AVAILABLE_LANGUAGES:

        raise ValueError(
            f"value in {repr(lang_key)} key must be"
            " one of the following strings:"
            f" {AVAILABLE_LANGUAGES}"
        )

    ### test session data

    if TEST_SESSION_SETTINGS_KEY in prefs_data:
        validate_test_settings_data(prefs_data[TEST_SESSION_SETTINGS_KEY])


def validate_test_settings_data(test_settings_data):
    """Raise exception if test settings data doesn't validate."""

    key = TEST_SESSION_SETTINGS_KEY

    ### ensure test settings data is a dict

    if not isinstance(test_settings_data, dict):

        raise TypeError(
            f"Test settings data from '{key}' key in user preferences"
            " must be a dictionary."
        )

    ### ensure its contents validate as well

    for subkey in ('test_cases_ids', 'playback_speed'):

        if subkey not in test_settings_data:

            raise (

                KeyError

                (
                    f"'{subkey}' not present in '{key}' key"
                    " from user preferences"
                )

            )

        elif subkey == 'test_cases_ids':

            value = test_settings_data[subkey]

            if not isinstance(value, tuple):

                raise (

                    TypeError

                    (
                        f"'{subkey}' subkey from '{key}' key"
                        " in user preferences must hold a tuple."
                    )

                )

            elif (
                any(
                    not isinstance(item, int)
                    for item in value
                )
            ):

                raise (
                    TypeError
                    (
                        f"'{subkey}' subkey from '{key}' key"
                        " in user preferences must hold at least one item"
                        " and all items must be integers"
                    )
                )

        elif subkey == 'playback_speed':

            value = test_settings_data[subkey]

            if not isinstance(value, int):

                raise (

                    TypeError

                    (
                        f"'{subkey}' subkey from '{key}' key"
                        " in user preferences must hold an int."
                    )

                )

            elif value < 0:

                raise (

                    ValueError

                    (
                        f"'{subkey}' subkey from '{key}' key"
                        " in user preferences must hold an integer >= 0"
                    )

                )
