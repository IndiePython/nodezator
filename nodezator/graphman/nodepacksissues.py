"""Operations to deal with node packs issues."""

### standard library imports

from pathlib import Path

from importlib import import_module


### local imports

from ..config import APP_REFS

from ..appinfo import NODE_SCRIPT_NAME

from .exception import (
    NodePackNotImportedError,
    NodePackNotFoundError,
    NodePackNotADirectoryError,
    NodePackLackingCategoryError,
    CategoryLackingScriptDirectoryError,
    ScriptDirectoryLackingScriptError,
)

from ..ourstdlibs.pyl import load_pyl


def get_formatted_local_node_packs(filepath):
    ### retrieve the contents of the node_packs field

    try:
        source_path = APP_REFS.source_path
    except AttributeError:
        data = load_pyl(filepath)
    else:
        if filepath == source_path:
            data = APP_REFS.data
        else:
            data = load_pyl(filepath)

    node_packs_paths = data.setdefault("node_packs", [])

    ### guarantee node packs paths is a list
    if not isinstance(node_packs_paths, list):
        node_packs_paths = [node_packs_paths]

    ### we turn items into pathlib.Path objects and return list
    return [Path(path) for path in node_packs_paths]


def get_formatted_installed_node_packs(filepath):
    ### retrieve the contents of the installed_node_packs field

    try:
        source_path = APP_REFS.source_path
    except AttributeError:
        data = load_pyl(filepath)
    else:
        if filepath == source_path:
            data = APP_REFS.data
        else:
            data = load_pyl(filepath)

    node_packs_names = data.setdefault("installed_node_packs", [])

    ### guarantee node packs names is a list
    if not isinstance(node_packs_names, list):
        node_packs_names = [node_packs_names]

    ### finally we return the list
    return node_packs_names


def check_local_node_packs(node_packs):
    """Raise error if issues are found in local node packs."""

    ### check whether node packs exist

    for path in node_packs:

        if not path.exists():

            raise NodePackNotFoundError(f"the '{path}' node pack path" " wasn't found")

    ### check whether node packs are directories

    for path in node_packs:

        if not path.is_dir():

            raise NodePackNotADirectoryError(
                f"the '{path}' node pack isn't a" " directory"
            )

    ### check whether each node pack has at least
    ### one script

    for node_pack in node_packs:

        category_folders = [
            path
            for path in node_pack.iterdir()
            if path.is_dir()
            if not path.name.startswith(".")
            if not path.name == "__pycache__"
        ]

        if not category_folders:

            raise NodePackLackingCategoryError(
                f"node pack '{node_pack}' must have at least 1 category"
            )

        for category_folder in category_folders:

            script_dirs = [
                path
                for path in category_folder.iterdir()
                if path.is_dir()
                if not path.name.startswith(".")
                if not path.name == "__pycache__"
            ]

            if not script_dirs:

                raise CategoryLackingScriptDirectoryError(
                    f"category dir '{category_folder}'"
                    " must have at least 1 script"
                    " directory"
                )

            for script_dir in script_dirs:

                script_file = script_dir / NODE_SCRIPT_NAME

                if not script_file.is_file():

                    raise ScriptDirectoryLackingScriptError(
                        node_pack,
                        category_folder,
                        script_dir,
                        script_file,
                    )


def check_installed_node_packs(node_packs):
    """Raise error if issues are found in installed node packs."""
    ### try importing each installed node pack while
    ### filling a map associating the node pack name with
    ### its path in the system

    node_pack_path_map = {}

    for name in node_packs:

        try:
            node_pack_module = import_module(name)

        except ModuleNotFoundError:
            raise NodePackNotImportedError(
                f"the '{name}' node pack,"
                " expected to be installed, could not be imported"
            )

        else:
            node_pack_path_map[name] = Path(node_pack_module.__path__[0])

    ### check whether each node pack has at least
    ### one script

    for name, node_pack in node_pack_path_map.items():

        category_folders = [
            path
            for path in node_pack.iterdir()
            if path.is_dir()
            if not path.name.startswith(".")
            if not path.name == "__pycache__"
        ]

        if not category_folders:

            raise NodePackLackingCategoryError(
                f"installed node pack '{name}' must have at least 1 category"
            )

        for category_folder in category_folders:

            script_dirs = [
                path
                for path in category_folder.iterdir()
                if path.is_dir()
                if not path.name.startswith(".")
                if not path.name == "__pycache__"
            ]

            if not script_dirs:

                raise CategoryLackingScriptDirectoryError(
                    f"category dir '{category_folder.name}'"
                    f" from installed node pack '{name}' must have at least 1 script"
                    " directory"
                )

            for script_dir in script_dirs:

                script_file = script_dir / NODE_SCRIPT_NAME

                if not script_file.is_file():

                    raise ScriptDirectoryLackingScriptError(
                        name,
                        category_folder,
                        script_dir,
                        script_file,
                    )
