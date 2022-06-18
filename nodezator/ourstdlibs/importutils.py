
### standard library imports

from sys import path

from pathlib import Path


def remove_import_visibility(dirpath):
    """Make it so it is not possible to import from path."""
    visible_paths = [Path(item).resolve() for item in path]

    resolved_dirpath = dirpath.resolve()

    indices_to_remove = [

      index
      for index, item in enumerate(visible_paths)
      if item.resolve() == resolved_dirpath

    ]

    indices_to_remove.reverse()

    for index in indices_to_remove: path.pop(index)

def grant_import_visibility(dirpath):
    """Make it so it is possible to import from path."""

    visible_paths = [Path(item).resolve() for item in path]

    resolved_dirpath = dirpath.resolve()

    if any(

      item.resolve() == resolved_dirpath
      for item in visible_paths

    ): return

    path.append(str(resolved_dirpath))
