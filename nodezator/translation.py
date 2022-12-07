### standard library import
from collections import ChainMap


### local imports

from .config import DATA_DIR

from .userprefsman.main import USER_PREFS

from .ourstdlibs.pyl import load_pyl

from .ourstdlibs.treeutils import merge_nested_dicts

from .ourstdlibs.collections.nestedfromdict import NestedObjectFromDict


### first load English translation data; we use it as
### fallback in case a translation isn't found

lang_dirname = "en_us"

LANG_DEPENDENT_DATA_DIR = DATA_DIR / "locale" / "en_us"

DIALOGS_MAP = load_pyl(LANG_DEPENDENT_DATA_DIR / "dialogs_map.pyl")

STATUS_MESSAGES_MAP = load_pyl(LANG_DEPENDENT_DATA_DIR / "status_messages_map.pyl")

TRANSLATION_MAP = load_pyl(LANG_DEPENDENT_DATA_DIR / "translations_map.pyl")


### now, if the language chosen is 'English', we don't
### need to do further loading and processing of maps,
###
### if it isn't though, the "if block" below is executed
### and the maps for the chosen language are loaded and
### used as the first links in collections.ChainMap
### instances, using the english maps and the "fallback"
### links

if USER_PREFS["LANGUAGE"] != "English":

    lang_dirname = {
        "English": "en_us",
        "Português do Brasil": "pt_br",
    }[USER_PREFS["LANGUAGE"]]

    ###

    LANG_DEPENDENT_DATA_DIR = DATA_DIR / "locale" / lang_dirname

    ###

    DIALOGS_MAP = ChainMap(
        load_pyl(LANG_DEPENDENT_DATA_DIR / "dialogs_map.pyl"),
        DIALOGS_MAP,
    )

    ###

    STATUS_MESSAGES_MAP = ChainMap(
        load_pyl(LANG_DEPENDENT_DATA_DIR / "status_messages_map.pyl"),
        STATUS_MESSAGES_MAP,
    )

    ###

    TRANSLATION_MAP = merge_nested_dicts(
        load_pyl(LANG_DEPENDENT_DATA_DIR / "translations_map.pyl"),
        TRANSLATION_MAP,
    )

### finally, we convert the translations map into a
### special object instance which simply allows
### us to access the original map keys using dot notation
TRANSLATION_HOLDER = NestedObjectFromDict(TRANSLATION_MAP)
