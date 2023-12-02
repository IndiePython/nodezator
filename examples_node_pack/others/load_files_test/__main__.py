"""Facility for testing loading files within node script folder.

Each node scripts sits in its own folder, which is called
the node's script folder. The node script must not use
code/resources from other node's script directory.
That is, all the nodes must be self-contained,
independent from each other.

In this example we present how to load files from within
the node script directory. This way, your node script may
grow indefinitelly in its own directory, having as many
files as you want, so that you can extend/improve your node
locally.

By keeping all the local resources your node needs in its
own folder, you ensure the nodes are independent from each
other, and can thus be mantained separately, without
concerning yourself with dependencies.
"""
from pathlib import Path


### getting the node script location (we call it the
### node script directory)
node_script_dir = Path(__file__).parent


### loading data from text files

## from current location

filepath00 = node_script_dir / "file00.txt"
with open(str(filepath00), "r", encoding="utf-8") as f:
    text00_contents = f.read()

## from subdirectory

filepath01 = (
  node_script_dir / "txt_dir" / "another.txt"
)
with open(str(filepath01), "r", encoding="utf-8") as f:
    text01_contents = f.read()


### now we can use the data anywhere we want in our
### function; we'll use them as the default values
### for our parameters:

def file_loading_test(
      text_a=text00_contents, text_b=text01_contents
    ) -> str:
    """Concatenate strings."""
    return text_a + text_b

### callable used must always be aliased as 'main'
main_callable = file_loading_test
