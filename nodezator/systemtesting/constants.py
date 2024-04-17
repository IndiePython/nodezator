
### local imports

from ..config import SYSTEM_TESTING_DATA_DIR

from ..ourstdlibs.pyl import load_pyl


TEST_ID_TO_TITLE = load_pyl(SYSTEM_TESTING_DATA_DIR / 'test_id_to_title.pyl')

ID_FORMAT_SPEC = '>04'
