"""Facility for callable retrieval from scripts.

We load modules and retrieve a specific callable object
from each of them, which is aliased as 'main', gathering
all the retrieved callables in a map.

Each callable represents a different kind of node.
"""

### standard library imports

from pathlib import Path

from runpy import run_path

from collections import namedtuple

from types import MappingProxyType

from itertools import chain

from inspect import signature


### local imports

from config import APP_REFS

from appinfo import (
               NODE_SCRIPT_NAME,
               NODE_DEF_VAR_NAMES,
               NODE_CATEGORY_METADATA_FILENAME,
             )

from ourstdlibs.pyl import load_pyl

from ourstdlibs.importutils import (
                              remove_import_visibility,
                              grant_import_visibility,
                            )

from graphman.exception import NodeScriptsError

from colorsman.colors import NODE_CATEGORY_COLORS


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


### TODO review docstring;
###
### - add description of id_map;
### - I believe we don't store the script's text, as
###   said in the docstring, but rather the location
###   to that text (path); check and fix docstring if
###   needed;

def load_scripts(node_packs_paths):
    """Load modules and store specific data in dicts.

    Namely, the object called 'main', which must be
    a callable, and the module's text.

    Parameters
    ==========
    node_packs_paths (pathlib.Path or string)
        represents the path to the directory from where
        the scripts will be loaded in order to retrieve
        a callable called 'main' from each of them.
        Such callables are later used as specifications
        for nodes.

    How it works
    ============

    First, we retrieve references for a special dictionaries
    from the APP_REFS object imported from the config.py
    module. Then, we populate them with the proper data.
    """
    ### retrieve dictionary references

    node_def_map       = APP_REFS.node_def_map
    signature_map      = APP_REFS.signature_map
    id_map             = APP_REFS.id_map
    script_path_map    = APP_REFS.script_path_map
    category_path_map  = APP_REFS.category_path_map
    category_index_map = APP_REFS.category_index_map

    ### make sure node_packs_paths is a list of node packs

    if not isinstance(node_packs_paths, list):
        node_packs_paths = [node_packs_paths]

    ### if they aren't already, turn the node packs paths
    ### into pathlib.Path objects

    node_packs_paths = sorted(
      (Path(path) for path in node_packs_paths),
      key = get_path_name,
    )

    ### create lists to hold information about errors
    ### during script loading, if any

    scripts_not_loaded               = []
    scripts_missing_node_definition  = []
    not_actually_callables           = []
    callables_not_inspectable        = []

    ### define the number of existing node category
    ### colors
    no_of_colors = len(NODE_CATEGORY_COLORS)

    ### for each node pack path, gather the subfolders
    ### in the level below;
    ###
    ### such folders represent categories which hold
    ### more folders representing node scripts;

    for node_pack_path in node_packs_paths:

        ## check whether node pack folder name is
        ## a valid Python identifier, raising an
        ## error if not

        node_pack_name = node_pack_path.name

        if not node_pack_name.isidentifier():
            
            raise ValueError(
                     "Node pack name must be a valid"
                     " Python identifier; the node pack"
                    f"'{node_pack_name}' doesn't comply"
                  )

        ## retrieve the name of the node pack path
        ## as the name of the node pack
        node_pack_name = node_pack_path.name

        ## iterate over each subdirectory in the
        ## node pack, which represent categories

        category_folders = sorted(
          (
            item
            for item in node_pack_path.iterdir()
            if item.is_dir()
            if not item.name.startswith('.')
          ),
          key = get_path_name,
        )

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

              (color_index + 1) % no_of_colors
              if 'color_index' in locals()

              else 0

            )

            ## try loading the category metadata

            try: category_metadata = load_pyl(
                   category_folder
                   / NODE_CATEGORY_METADATA_FILENAME
                 )

            ## if it fails, just pass
            except Exception as err: pass

            ## otherwise, try obtaining the category
            ## color index from the metadata, unless it
            ## fails, in which case we pass

            else:
                
                try: color_index = (
                        int(
                          category_metadata[
                            'color_index'
                          ]
                        ) % no_of_colors
                     )

                except Exception: pass

            ## store the category index in the map using the
            ## category id
            category_index_map[category_id] = color_index

            ## iterate over the directories in the
            ## category folder

            subdirectories_iterator = (
              item
              for item in category_folder.iterdir()
              if item.is_dir()
              if not item.name.startswith('.')
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

                script_filepath = (
                  script_dir / NODE_SCRIPT_NAME
                )

                # remove app_dir from sys.path and append
                # scirpt_dir to it

                remove_import_visibility(APP_REFS.app_dir)
                grant_import_visibility(script_dir)

                # try executing the file from the path as a
                # python module, retrieving the resulting
                # namespace dictionary

                try: namespace_dict = run_path(
                                        str(script_filepath)
                                      )

                # if it fails, store data about the error
                # a custom error explaining the problem
                # then skip loading this script with a
                # "continue" statement

                except Exception as err:

                    scripts_not_loaded.append((
                                         script_filepath,
                                         str(err),
                                       ))

                    continue

                finally:

                    # remove script_dir from sys.path and
                    # append app_dir to it

                    remove_import_visibility(script_dir)

                    grant_import_visibility(
                      APP_REFS.app_dir
                    )

                # build dict with objects used to define
                # the node stored in special variables

                node_def_dict = {

                  var_name: namespace_dict[var_name]

                  for var_name in NODE_DEF_VAR_NAMES
                  if var_name in namespace_dict

                }

                # if we don't find a main callable to
                # define the node, we store data about
                # this problem and skip processing this
                # script with a "continue" statement

                try: main_callable = (
                       node_def_dict['main_callable']
                     )

                except KeyError:

                    scripts_missing_node_definition.append(
                      script_filepath
                    )

                    continue

                else:

                    signature_callable = (

                      node_def_dict.setdefault(
                                      'signature_callable',
                                      main_callable

                                    )
                    )


                # if callables aren't indeed callable,
                # we store data about this error and skip
                # processing this script with a "continue"
                # statement

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

                    continue

                # check whether object is inspectable
                # or not by attempting to get a
                # signature from it

                try: signature_obj = signature(
                                       signature_callable
                                     )

                # if not, store data about the error and
                # skip processing this script with a
                # "continue" statement

                except Exception as err:
                    
                    callables_not_inspectable.append(

                      (
                        signature_callable.__name__,
                        script_filepath,
                      )

                    )

                    continue

                # otherwise, just store the signature in
                # a special map, using the signature obj
                # as the key
                else: signature_map[
                        signature_callable
                      ] = signature_obj


                # define id for script and associate it
                # with the signature callable in the proper
                # map

                script_id = (
                  node_pack_name,
                  category_name,
                  script_dir.name,
                )

                id_map[signature_callable] = script_id

                # store the node definition object in the
                # proper map with the id we created
                node_def_map[script_id] = node_def_dict

                ## also store the script's path
                script_path_map[script_id] = (
                  script_filepath
                )

    ### if any errors were found during script loading,
    ### report them by raising a custom exception

    if any(
         chain(
           scripts_not_loaded,
           scripts_missing_node_definition,
           not_actually_callables,
           callables_not_inspectable,
         )
    ):
        
        raise NodeScriptsError(
                scripts_not_loaded,
                scripts_missing_node_definition,
                not_actually_callables,
                callables_not_inspectable,
              )

### small utility
def get_path_name(item): return Path(item).name
