"""Facility with functions for initial positioning of file manager contents."""

### local imports

from .constants import (
    FILEMAN_WIDTH,
    DIR_PANEL_WIDTH,
    BKM_PANEL_WIDTH,
    FONT_HEIGHT,
)



def position_elements_and_get_height(fm):
    """Position objects from given file manager and return height.

    That is, the area occupied by the elements.

    Parameters
    ==========
    fm (fileman.main.FileManager instance)
    """

    fm.navigation_entry.rect.left = fm.navigation_entry_offset[0]
    fm.navigation_entry.rect.centery = fm.current_label_top + (FONT_HEIGHT//2) + 5

    fm.caption_label.rect.midleft = fm.caption_label_offset

    dp = fm.dir_panel

    dp.rect.right = FILEMAN_WIDTH - 5
    dp.rect.top = fm.panels_labels_top + FONT_HEIGHT + 10

    dp.path_objs.rect.topleft = dp.rect.move(1, 1).topleft

    bp = fm.bkm_panel

    bp.rect.right = dp.rect.left - 5
    bp.rect.top = dp.rect.top
    bp.bookmark_objs.rect.topleft = bp.rect.move(1, 1).topleft

    fm.selected_label.rect.topleft = bp.rect.move(0, 10).bottomleft

    sel_entry = fm.selection_entry
    sel_entry.rect.midleft = fm.selected_label.rect.move(5, 0).midright

    sbtn = fm.submit_button
    cbtn = fm.cancel_button

    sbtn.rect.topright = dp.rect.move(0, 5).bottomright
    cbtn.rect.topright = sbtn.rect.move(-10, 0).topleft

    height = sbtn.rect.bottom + 10

    return height
