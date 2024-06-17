
from pathlib import Path


here = Path(__file__).parent

for path in here.iterdir():

    if path.name.startswith('stc') and path.suffix.lower() == '.py':
        exec(f'from . import {path.stem}')

#from . import (
    #stc0000,
    #stc0001,
    #stc0002,
#)
