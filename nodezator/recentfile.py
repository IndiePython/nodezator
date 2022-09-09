"""Facility for storing/retrieving recent used filepaths."""

### standard library import
from pathlib import Path


### local imports

from .userprefsman.main import RECENT_FILES

from .ourstdlibs.pyl import load_pyl, save_pyl


def get_recent_files():
    """Return recent files list as path objects."""
    filter_recent_files()

    try:
        data = load_pyl(RECENT_FILES)

    except FileNotFoundError:

        data = []
        save_pyl(data, RECENT_FILES)

    else:
        data = list(map(Path, data))

    return data


### TODO in order to prevent repeating operations like
### loading the data from the RECENT_FILES json file,
### it would be better to merge the function below with
### the get_recent_files() function above;


def filter_recent_files():
    """Filter out unexistent files."""
    try:
        data = load_pyl(RECENT_FILES)

    except FileNotFoundError:

        data = []
        save_pyl(data, RECENT_FILES)
        return

    else:

        ### XXX in addition to filter out unexisting files,
        ### maybe also filter out files with the wrong
        ### extension

        ### gather non existent files

        removal_list = []

        for filepath in data:

            if Path(filepath).is_file():
                pass

            else:
                removal_list.append(filepath)

        ### remove them from filepath

        if removal_list:

            for item in removal_list:
                data.remove(item)

            save_pyl(data, RECENT_FILES)


def store_recent_file(path):
    """Verify if path is on recent files and add it.

    Parameters
    ==========
    path (pathlib.Path instance)
        represents path being stored as recent file.
    """
    ### if file with list of recent files don't exist,
    ### create the list yourself

    try:
        recent_paths = load_pyl(RECENT_FILES)
    except FileNotFoundError:
        recent_paths = []

    ### turn path into string
    str_path = str(path)

    ### remove path from list if it is already present

    try:
        recent_paths.remove(str_path)
    except ValueError:
        pass

    ### finally, insert path at the beginning of the list
    ### and save the list back in the path dedicated to
    ### the "recent files" json file

    recent_paths.insert(0, str(path))
    save_pyl(recent_paths, RECENT_FILES)
