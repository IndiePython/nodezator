"""Common icon surfaces for the file manager subpackage."""

### local imports

from ..surfsman.icon import render_layered_icon

from ..imagesman.cache import IMAGE_SURFS_DB

from ..colorsman.colors import BLACK, WHITE


FOLDER_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (33, 34)],
    dimension_name="height",
    dimension_value=20,
    colors=[BLACK, (30, 130, 70)],
    background_width=24,
    background_height=24,
)

FILE_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (35, 36)],
    dimension_name="height",
    dimension_value=20,
    colors=[BLACK, WHITE],
    background_width=24,
    background_height=24,
)

PDF_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (35, 36)],
    dimension_name="height",
    dimension_value=20,
    colors=[BLACK, (255, 0, 0)],
    background_width=24,
    background_height=24,
)


TEXT_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (37, 36)],
    dimension_name="height",
    dimension_value=20,
    colors=[BLACK, WHITE],
    background_width=24,
    background_height=24,
)

PYTHON_ICON = IMAGE_SURFS_DB["python_filemanager_icon.png"][{"use_alpha": True}]


IMAGE_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (38, 40, 41, 39)],
    dimension_name="height",
    dimension_value=20,
    colors=[BLACK, BLACK, WHITE, (30, 130, 70)],
    background_width=24,
    background_height=24,
)


AUDIO_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (38, 42, 43, 39)],
    dimension_name="height",
    dimension_value=20,
    colors=[BLACK, BLACK, WHITE, (30, 130, 70)],
    background_width=24,
    background_height=24,
)

VIDEO_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (44, 45)],
    dimension_name="height",
    dimension_value=20,
    colors=[BLACK, (30, 130, 70)],
    background_width=24,
    background_height=24,
)

FONT_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (38, 46, 47, 39)],
    dimension_name="height",
    dimension_value=20,
    colors=[BLACK, BLACK, WHITE, (30, 130, 70)],
    background_width=24,
    background_height=24,
)

NATIVE_FILE_ICON = render_layered_icon(
    chars=[chr(ordinal) for ordinal in (183, 184, 185)],
    dimension_name="width",
    dimension_value=22,
    colors=[BLACK, WHITE, (77, 77, 105)],
    background_width=24,
    background_height=24,
)
