"""Facility with operations for system testing case 0001."""

### standard library imports

from pathlib import Path

from zipfile import ZipFile

from ast import literal_eval

from tempfile import mkstemp


### local imports
from ...config import APP_REFS, SYSTEM_TESTING_DATA_DIR



TEMP_FILEPATH = []


def perform_setup(data):
    """"""

    with ZipFile(
        str(SYSTEM_TESTING_DATA_DIR / 'test_cases' / 'stc0001.zip'),
        mode='r',
    ) as archive:

        ###

        with archive.open('input_data.pyl', mode='r') as input_data_file:

            data.input_data = (
                literal_eval(input_data_file.read().decode(encoding='utf-8'))
            )

        ###

        with archive.open('file_to_load.ndz', mode='r') as file_to_load:
            ndz_text = file_to_load.read().decode(encoding='utf-8')

        temporary_filepath = Path(mkstemp(suffix='.ndz', text=True)[1])

        temporary_filepath.write_text(ndz_text, encoding='utf-8')

        data.filepath = temporary_filepath

        TEMP_FILEPATH.append(temporary_filepath)

def perform_assertions(result_map):
    """Confirm no objects remain on the loaded file.

    Parameters
    ==========
    result_map (dict)
        Used to store test results.
    """
    ### confirm no text boxes exist

    ## grab the text blocks
    text_blocks = APP_REFS.gm.text_blocks

    ## no items in APP_REFS.gm.text_blocks

    result_map[
        "There's no objects in APP_REFS.gm.text_blocks"
    ] = len(text_blocks) == 0


    ### confirm no nodes exist

    ## grab the nodes iterable
    nodes = APP_REFS.gm.nodes

    ## the "nodes" iterable must contain no items

    result_map[
        "There must be no items in APP_REFS.gm.nodes"
    ] = len(nodes) == 0


def perform_teardown():
    """"""
    TEMP_FILEPATH.pop().unlink()
