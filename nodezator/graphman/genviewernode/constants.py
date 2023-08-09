
### standard library imports
from inspect import signature, getsource


### local imports

from .nodedefs import viewastext

from .nodedefs import viewasmonotext

from .nodedefs import viewpythonsource

from .nodedefs import viewsurface



GENVIEWER_IDS_TO_CALLABLES_MAP = {
    "view_as_text": viewastext.view_as_text,
    "view_as_monotext": viewasmonotext.view_as_monotext,
    "view_python_source": viewpythonsource.view_python_source,
    "view_surface": viewsurface.view_surface,
}

GENVIEWER_IDS_TO_MODULES_MAP = {
    "view_as_text": viewastext,
    "view_as_monotext": viewasmonotext,
    "view_python_source": viewpythonsource,
    "view_surface": viewsurface,
}


GENVIEWER_IDS_TO_SIGNATURES_MAP = {
    genviewer_id: signature(callable_obj)
    for genviewer_id, callable_obj in GENVIEWER_IDS_TO_CALLABLES_MAP.items()
}


GENVIEWER_IDS_TO_3RDLIB_IMPORT_MAP = {
    "view_surface": [
        "from pygame import Surface",
        "from pygame.math import Vector2",
        "from pygame.transform import scale as scale_surface",
        "from pygame.transform import smoothscale as smoothscale_surface",
    ],
}


GENVIEWER_IDS_TO_SOURCE_VIEW_TEXT = {

    genviewer_id: getsource(module_obj)
    for genviewer_id, module_obj in GENVIEWER_IDS_TO_MODULES_MAP.items()

}

###

GENVIEWER_IDS_TO_PYTHON_SOURCE = {
    genviewer_id: getsource(callable_obj)
    for genviewer_id, callable_obj in GENVIEWER_IDS_TO_CALLABLES_MAP.items()
}
