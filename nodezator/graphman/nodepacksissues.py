"""Operations to deal with node packs issues."""

### standard library import
from pathlib import Path


### local imports

from config import APP_REFS

from appinfo import NODE_SCRIPT_NAME

from graphman.exception import (
                        NodePackNotFoundError,
                        NodePackNotADirectoryError,
                        NodePackLackingCategoryError,
                        CategoryLackingScriptDirectoryError,
                        ScriptDirectoryLackingScriptError,
                      )


def get_formatted_current_node_packs():
    ### retrieve the contents of the node_packs field

    node_packs_paths = (
      APP_REFS.data.setdefault('node_packs', [])
    )

    ### guarantee node packs paths is a list
    if not isinstance(node_packs_paths, list):
        node_packs_paths = [node_packs_paths]

    ### we turn it into a pathlib.Path object

    return [
      Path(path) for path in node_packs_paths
    ]


def check_node_packs(node_packs):
    """Raise error if node packs issues are found."""

    ### check whether node packs exist

    for path in node_packs:

        if not path.exists():
            
            raise NodePackNotFoundError(
                    f"the '{path}' node pack path"
                     " wasn't found"
                  )

    ### check whether node packs are directories

    for path in node_packs:
        
        if not path.is_dir():

            raise NodePackNotADirectoryError(
                    f"the '{path}' node pack isn't a"
                     " directory"
                  )

    ### check whether each node pack has at least
    ### one script

    for node_pack in node_packs:

        category_folders = [

          path

          for path in node_pack.iterdir()

          if not path.name.startswith('.')
          if path.is_dir()

        ]

        if not category_folders:

            raise NodePackLackingCategoryError(
                    f"node pack '{node_pack}' must"
                     " have at least 1 category"
                  )

        for category_folder in category_folders:
            
            script_dirs = [

              path
              for path in category_folder.iterdir()

              if (
                not path.name.startswith('.')
                and path.is_dir()
              )

            ]

            if not script_dirs:

                raise CategoryLackingScriptDirectoryError(

                        f"category dir '{category_folder}'"
                         " must have at least 1 script"
                         " directory"

                      )

            for script_dir in script_dirs:
                
                script_file = (
                  script_dir / NODE_SCRIPT_NAME
                )

                if not script_file.is_file():

                    raise ScriptDirectoryLackingScriptError(
                            node_pack,
                            category_folder,
                            script_dir,
                            script_file,
                          )
