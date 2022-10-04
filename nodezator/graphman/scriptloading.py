"""Facility for callable retrieval from scripts.

We load modules and retrieve a specific callable object
from each of them, which is aliased as 'main', gathering
all the retrieved callables in a map.

Each callable represents a different kind of node.
"""

### standard library imports

from sys import modules

from pathlib import Path

from importlib import import_module

from collections import namedtuple

from types import MappingProxyType

from itertools import chain

from inspect import signature

from contextlib import contextmanager


### local imports

from ..config import APP_REFS

from ..knownpacks import store_node_pack_reference

from ..appinfo import (
    NODE_SCRIPT_NAME,
    NODE_DEF_VAR_NAMES,
    NODE_CATEGORY_METADATA_FILENAME,
)

from ..ourstdlibs.pyl import load_pyl

from ..ourstdlibs.importutils import temporary_sys_path_visibility

from .exception import NodeScriptsError

from ..colorsman.colors import NODE_CATEGORY_COLORS


### XXX idea: make it possible to reload individual node
### scripts (you can use the category + script_dir to reach
### to it directly; such information can be easily retrieved
### from the dict in APP_REFS.node_def_map);
###
### think about the implications of that operation in
### dependencies like nodespaces (in the file) and node
### groups (in the available operations) which use the
### reloaded node scripts (since we assume the reason for
### reloading it is that fact that it changed, and probably
### the dependencies must take it into account, since a new
### module_obj is generated);
###
### edit: thinking about it, this might not be needed,
### since, even if the objects generated don't have the
### same id (from id()), the callable will still have the
### same id attribute

### XXX
###
### I believe errors in the node scripts and also other
### problems, like a missing 'nodes_directory' field in
### the native file (or even a 'nodes_directory' which
### points to a folder with no node scripts) can all be
### solved from a common "design point":
###
### the node editor could have a "data view" mode,
### where crucial parts of the native file data could be
### exposed so that such kind of problems
### could be addressed, or at least leave the
### app in standby while the user goes where
### lies the problems and solve them (for instance,
### fixing a node script if it has an error in it,
### etc.); the ability to reload a node script is
### also appreciated, as discussed in the
### graphman/scriptloading.py module already mentioned;
###
### edit1: as of now, some poka-yoke checks were implemented
### to guide the user through eventual issues they may
### have with the nodes directory, until a more elegant
### solution can be properly designed and scheduled for
### implementation;
###
### edit2: though the poka-yoke checks were meant to be
### temporary until we come up with a better solution, this
### doesn't mean they are not a solution good enough
### (a better solution may in fact not even exist, or be
### too complex to be worth the time required to
### implement/teach it, or not even be needed);


@contextmanager
def no_context(node_pack_parent):
    """Do nothing on entering/exiting context."""
    yield


def load_scripts(local_node_pack_dirs, installed_node_pack_names):
    """Load modules and store specific data in dicts.

    Namely, the object called 'main', which must be
    a callable, and the module's text.

    Parameters
    ==========
    local_node_pack_dirs (string or list of strings)
        represents a path or paths to directories
        from where we'll load the scripts and retrieve
        objects used to define nodes from them.
    installed_node_pack_names (string or list of strings)
        represents a name or names to packages that can
        be import and have their subpackages used to
        define nodes.

    How it works
    ============

    First, we retrieve references for special dictionaries
    from the APP_REFS object imported from the config.py
    module. Then, we populate them with the proper data.
    """
    ### create special dicts

    node_def_map = {}
    signature_map = {}
    script_path_map = {}
    category_path_map = {}
    category_index_map = {}

    ### make sure local_node_pack_dirs is a list

    if not isinstance(local_node_pack_dirs, list):
        local_node_pack_dirs = [local_node_pack_dirs]

    ### if they aren't already, turn the node packs
    ### directories into pathlib.Path objects

    local_node_pack_dirs = [Path(path) for path in local_node_pack_dirs]
    local_node_pack_dirs.sort(key=get_path_name)

    ### make sure installed_node_pack_names is a list

    if not isinstance(installed_node_pack_names, list):
        installed_node_pack_names = [installed_node_pack_names]

    ### concatenate both kinds of node packs
    all_node_packs = local_node_pack_dirs + installed_node_pack_names

    ### create lists to hold information about errors
    ### during script loading, if any

    installed_pack_not_imported = []
    scripts_not_loaded = []
    scripts_missing_node_definition = []
    not_actually_callables = []
    callables_not_inspectable = []

    ### define the number of existing node category
    ### colors
    no_of_colors = len(NODE_CATEGORY_COLORS)

    ### for each node pack path, gather the subfolders
    ### in the level below;
    ###
    ### such folders represent categories which hold
    ### more folders representing node scripts;

    for node_pack in all_node_packs:

        is_local = isinstance(node_pack, Path)

        if is_local:
            node_pack_name = node_pack.name
            node_pack_dir = node_pack

        else:
            node_pack_name = node_pack

            try:
                node_pack_dir = Path(import_module(node_pack).__path__[0])

            except ModuleNotFoundError:
                installed_pack_not_imported.append(
                    (
                        f"could not import '{node_pack}' node pack"
                        " (it is supposed to be installed)"
                    )
                )

                continue

        ## check whether node pack folder name is
        ## a valid Python identifier, raising an
        ## error if not

        if not node_pack_name.isidentifier():

            raise ValueError(
                "Node pack name must be a valid"
                " Python identifier; the node pack"
                f"'{node_pack_name}' doesn't comply"
            )

        ## retrieve the name of the node pack path
        ## as the name of the node pack
        node_pack_name = node_pack_dir.name

        ## obtain a list of all directories in the
        ## node pack (they represent categories)

        category_folders = sorted(
            (
                item
                for item in node_pack_dir.iterdir()
                if item.is_dir()
                if not item.name.startswith(".")
                if not item.name == "__pycache__"
            ),
            key=get_path_name,
        )

        ## reference the parent of the node pack folder,
        ## that is, the folder where the node pack
        ## directory is located
        node_pack_parent = node_pack_dir.parent

        ## pick a proper context wherein to execute the node pack loading
        context_to_enable = temporary_sys_path_visibility if is_local else no_context

        ## load scripts

        # create flag to indicate when all scripts loaded sucessfully
        loaded_scripts_successfully = True

        with context_to_enable(node_pack_parent):

            for category_folder in category_folders:

                ## check whether category folder name is
                ## a valid Python identifier, raising an
                ## error if not

                category_folder_name = category_folder.name

                if not category_folder_name.isidentifier():

                    raise ValueError(
                        "Category folder name must be a"
                        " valid Python identifier; the"
                        " category folder"
                        f" '{category_folder_name}'"
                        " doesn't comply"
                    )

                ## retrieve the name of the category
                ## folder to use as a category name
                category_name = category_folder.name

                ## with the node pack name it forms
                ## the category id in a 2-tuple
                category_id = (node_pack_name, category_name)

                ## store the category path in a special map
                ## holding category paths
                category_path_map[category_id] = category_folder

                ## define a default color index for the
                ## category

                color_index = (
                    (color_index + 1) % no_of_colors if "color_index" in locals() else 0
                )

                ## try loading the category metadata

                try:
                    category_metadata = load_pyl(
                        category_folder / NODE_CATEGORY_METADATA_FILENAME
                    )

                ## if it fails, just pass
                except Exception as err:
                    pass

                ## otherwise, try obtaining the category
                ## color index from the metadata, unless it
                ## fails, in which case we pass

                else:

                    try:
                        color_index = (
                            int(category_metadata["color_index"]) % no_of_colors
                        )

                    except Exception:
                        pass

                ## store the category index in the map using the
                ## category id
                category_index_map[category_id] = color_index

                ## iterate over the directories in the
                ## category folder

                subdirectories_iterator = (
                    item
                    for item in category_folder.iterdir()
                    if item.is_dir()
                    if not item.name.startswith(".")
                    if not item.name == "__pycache__"
                )

                for script_dir in subdirectories_iterator:

                    ## check whether script directory name is
                    ## a valid Python identifier, raising an
                    ## error if not

                    script_dir_name = script_dir.name

                    if not script_dir_name.isidentifier():

                        raise ValueError(
                            "Script folder name must be a"
                            " valid Python identifier;"
                            " the script folder"
                            f" '{script_dir_name}' doesn't"
                            " comply"
                        )

                    ## populate the module map

                    # put together the path to the script by
                    # combining a '__main__.py" file name with
                    # the script directory
                    script_filepath = script_dir / NODE_SCRIPT_NAME

                    # try importing the file from the path as a
                    # module, retrieving its namespace dictionary

                    try:
                        ### obtain the module name
                        ###
                        ### it will be in the format
                        ### "node_pack_dir.category_dir.node_script_dir.filename",
                        ### that is, the last 4 parts of the path linked by
                        ### dots ('.') minus the 03 characters at the end of the
                        ### path ('.py')
                        module_name = ".".join(script_filepath.parts[-4:])[:-3]

                        ### load the module and retrieve the namespace dictionary
                        namespace_dict = import_module(module_name).__dict__

                    # if it fails, store data about the error
                    # a custom error explaining the problem
                    # then turn off the flag that indicates all
                    # scripts were loaded succesfully and skip
                    # loading this script with a "continue" statement

                    except Exception as err:

                        scripts_not_loaded.append(
                            (
                                script_filepath,
                                str(err),
                            )
                        )

                        loaded_scripts_successfully = False
                        continue

                    # build dict with objects used to define
                    # the node stored in special variables

                    node_def_dict = {
                        var_name: namespace_dict[var_name]
                        for var_name in NODE_DEF_VAR_NAMES
                        if var_name in namespace_dict
                    }

                    # if we don't find a main callable to
                    # define the node, we store data about
                    # this problem, turn off the flag that indicates all
                    # scripts were loaded succesfully and skip
                    # processing this script with a "continue" statement

                    try:
                        main_callable = node_def_dict["main_callable"]

                    except KeyError:

                        scripts_missing_node_definition.append(script_filepath)

                        loaded_scripts_successfully = False
                        continue

                    else:

                        signature_callable = node_def_dict.setdefault(
                            "signature_callable", main_callable
                        )

                    # if callables aren't indeed callable,
                    # we store data about this problem, turn off the
                    # flag that indicates all scripts were loaded
                    # succesfully and skip processing this script with
                    # a "continue" statement

                    must_skip = False

                    for callable_obj in (
                        main_callable,
                        signature_callable,
                    ):

                        if not callable(callable_obj):

                            not_actually_callables.append(
                                (
                                    callable_obj.__name__,
                                    script_filepath,
                                )
                            )

                            must_skip = True
                            loaded_scripts_successfully = False

                    if must_skip:
                        continue

                    # check whether object is inspectable
                    # or not by attempting to get a
                    # signature from it

                    try:
                        signature_obj = signature(signature_callable)

                    # if not, store data about the error, turn off the
                    # flag that indicates all scripts were loaded
                    # succesfully and skip processing this script with
                    # a "continue" statement

                    except Exception as err:

                        callables_not_inspectable.append(
                            (
                                signature_callable.__name__,
                                script_filepath,
                            )
                        )

                        loaded_scripts_successfully = False
                        continue

                    # otherwise, just store the signature in
                    # a special map, using the signature obj
                    # as the key
                    else:
                        signature_map[signature_callable] = signature_obj

                    # define id for script and also store it
                    # in the node definition dict

                    script_id = (
                        node_pack_name,
                        category_name,
                        script_dir.name,
                    )

                    node_def_dict["script_id"] = script_id

                    # store the node definition object in the
                    # proper map with the id we created
                    node_def_map[script_id] = node_def_dict

                    ## also store the script's path
                    script_path_map[script_id] = script_filepath

        ### if your reach this point in the "for loop" without finding
        ### an error in one (or more) of your node scripts, it means the
        ### node pack was successfully loaded, so we store a reference to it as
        ### a known node pack

        if loaded_scripts_successfully:
            store_node_pack_reference(node_pack)

        ### remove imported modules from sys.modules so they are reloaded
        ### everytime a file is loaded/reloaded;
        ###
        ### this also prevents this error: suppose we have a local node pack
        ### called 'foo' and the user also wants to load an installed node
        ### pack with the same name; when the node packs were loaded, whichever
        ### pack was loaded first would shadow the second pack, causing
        ### unintended and harmful effects;
        ###
        ### also, standard and third-party libraries loaded within
        ### the node packs are not removed, making it so only the node packs
        ### are reloaded when needed, saving time

        module_keys = tuple(modules)

        keys_to_remove = [
            item for item in module_keys if item.split(".")[0] == node_pack_name
        ]

        for key in keys_to_remove:
            modules.pop(key)

    ### if any errors were found during script loading,
    ### report them by raising a custom exception

    if any(
        chain(
            installed_pack_not_imported,
            scripts_not_loaded,
            scripts_missing_node_definition,
            not_actually_callables,
            callables_not_inspectable,
        )
    ):

        raise NodeScriptsError(
            installed_pack_not_imported,
            scripts_not_loaded,
            scripts_missing_node_definition,
            not_actually_callables,
            callables_not_inspectable,
        )

    ### otherwise, update the corresponding dicts from
    ### the APP_REFS

    APP_REFS.node_def_map.clear()
    APP_REFS.node_def_map.update(node_def_map)
    node_def_map.clear()

    APP_REFS.signature_map.clear()
    APP_REFS.signature_map.update(signature_map)
    signature_map.clear()

    APP_REFS.script_path_map.clear()
    APP_REFS.script_path_map.update(script_path_map)
    script_path_map.clear()

    APP_REFS.category_path_map.clear()
    APP_REFS.category_path_map.update(category_path_map)
    category_path_map.clear()

    APP_REFS.category_index_map.clear()
    APP_REFS.category_index_map.update(category_index_map)
    category_index_map.clear()


### small utility
def get_path_name(item):
    return Path(item).name
