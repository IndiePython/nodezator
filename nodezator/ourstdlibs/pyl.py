"""Facility for python literal loading/saving."""

### standard library imports

from ast import literal_eval

from pprint import pformat



def load_pyl(filepath):
    """Return python literal from file in filepath."""

    with open(
      str(filepath), mode='r', encoding='utf-8'
    ) as f:

        return literal_eval(f.read())

def save_pyl(

      python_literal,
      filepath,

      *,

      indent =   2,

      # arbitrary large value, since .pyl is used mostly to
      # store data and shouldn't be read by humans often;
      width  = 300,

    ):
    """Save pretty-formatted python literal in filepath."""
    with open(
      str(filepath), mode='w', encoding='utf-8'
    ) as f:

        f.write(

            pformat(

              python_literal,

              indent = indent,
              width  = width,

            )

          )
