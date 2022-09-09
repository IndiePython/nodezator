"""Facility for python literal loading/saving."""

### standard library imports

from ast import literal_eval

from pprint import pformat


def load_pyl(filepath):
    """Return python literal from file in filepath."""

    with open(str(filepath), mode="r", encoding="utf-8") as f:

        try:
            return literal_eval(f.read())

        except Exception as err:

            message = f"Error while trying to load {filepath}."

            raise Exception(message) from err


def save_pyl(
    python_literal,
    filepath,
    *,
    indent=2,
    width=80,
):
    """Save pretty-formatted python literal in filepath."""

    with open(str(filepath), mode="w", encoding="utf-8") as f:

        try:

            f.write(
                pformat(
                    python_literal,
                    indent=indent,
                    width=width,
                )
            )

        except Exception as err:

            message = f"Error while trying to save {filepath}."

            raise Exception(message) from err
