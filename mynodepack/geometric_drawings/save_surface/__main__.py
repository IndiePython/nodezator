
### third-party imports

from pygame import Surface

from pygame.image import save as save_surface


def _save_surface(
    surface:Surface,
    filepath:'image_path'='dummy_path',
) -> [{'name': 'None', 'type': None}]:
    """Save given surface on disk."""
    pass

main_callable = save_surface
signature_callable = _save_surface
third_party_import_text = 'from pygame.image import save as save_surface'
call_format = 'save_surface'
