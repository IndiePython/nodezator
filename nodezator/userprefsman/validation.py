AVAILABLE_LANGUAGES = (
    "English",
    "Português do Brasil",
)


KEY_ERROR_FORMATTER = ("{!r} key not present in user preferences").format


def validate_prefs_dict(prefs_dict):
    """Raise exception if dict doesn't validate."""

    ### integers >= 0

    for key in (
        "USER_LOGGER_MAX_LINES",
        "CUSTOM_STDOUT_MAX_LINES",
        "NUMBER_OF_BACKUPS",
    ):

        if key not in prefs_dict:
            raise KeyError(KEY_ERROR_FORMATTER(key))

        value = prefs_dict[key]

        if not isinstance(value, int) or not value >= 0:

            raise TypeError(f"{repr(key)} key must be 'int' >= 0")

    ### available languages

    lang_key = "LANGUAGE"

    if lang_key not in prefs_dict:
        raise KeyError(KEY_ERROR_FORMATTER(lang_key))

    lang_value = prefs_dict[lang_key]

    if lang_value not in AVAILABLE_LANGUAGES:

        raise ValueError(
            f"value in {repr(lang_key)} key must be"
            " one of the following strings:"
            f" {AVAILABLE_LANGUAGES}"
        )
