### standard library imports

from sys import path

from pathlib import Path

from contextlib import contextmanager


@contextmanager
def temporary_sys_path_visibility(dirpath):

    resolved_dirpath = dirpath.resolve()
    visible_paths = [Path(item).resolve() for item in path]

    dirpath_already_on_sys_path = any(
        item.resolve() == resolved_dirpath for item in visible_paths
    )

    if not dirpath_already_on_sys_path:
        string_dirpath = str(resolved_dirpath)
        path.append(string_dirpath)

    try:
        yield

    finally:

        if not dirpath_already_on_sys_path:

            indices_to_remove = [
                index for index, item in enumerate(path) if string_dirpath == item
            ]

            indices_to_remove.reverse()

            for index in indices_to_remove:
                path.pop(index)
