"""Facility for storing/retrieving known node packs."""

### standard library imports

from sys import executable

from pathlib import Path


### local imports

from .userprefsman.main import KNOWN_PACKS_FILE

from .ourstdlibs.pyl import load_pyl, save_pyl


LOCAL_REFS_KEY = "local_node_packs"
INSTALLED_REFS_KEY = "sys_executable_to_installed_node_packs"


def get_known_node_packs():
    """Return list with custom-formatted references to known node packs."""

    try:
        known_packs_data = load_pyl(KNOWN_PACKS_FILE)

    except FileNotFoundError:

        known_packs_data = {
            LOCAL_REFS_KEY: [],
            INSTALLED_REFS_KEY: {},
        }

        save_pyl(known_packs_data, KNOWN_PACKS_FILE)

    installed_packs_refs = sorted(
        f"installed : {item}"
        for item in known_packs_data[INSTALLED_REFS_KEY].get(executable, [])
    )

    local_packs_refs = sorted(
        (f"local : {item}" for item in known_packs_data[LOCAL_REFS_KEY]),
        key=lambda string: Path(string.split(":")[1]).name,
    )

    return local_packs_refs + installed_packs_refs


def store_node_pack_reference(node_pack_ref):
    """Store node pack reference in map.

    Parameters
    ==========
    node_pack_ref (str or pathlib.Path instance)
        represents reference of node pack to be stored.
    """
    ### if file with known packs data doesn't exist,
    ### create it yourself

    try:
        known_packs_data = load_pyl(KNOWN_PACKS_FILE)

    except FileNotFoundError:

        known_packs_data = {
            LOCAL_REFS_KEY: [],
            INSTALLED_REFS_KEY: {},
        }

    ### define item and list wherein to add it

    if isinstance(node_pack_ref, str):
        item = node_pack_ref
        the_list = known_packs_data[INSTALLED_REFS_KEY].setdefault(executable, [])

    else:
        item = str(node_pack_ref)
        the_list = known_packs_data[LOCAL_REFS_KEY]

    ### if item not on the list, store it and save the data

    if item not in the_list:
        the_list.append(item)
        save_pyl(known_packs_data, KNOWN_PACKS_FILE)
