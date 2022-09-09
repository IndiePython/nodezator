"""Constants for fonts in the app."""

### local import
from ..config import FONTS_DIR


### enc sans bold text

ENC_SANS_BOLD_FONT_HEIGHT = 17

ENC_SANS_BOLD_FONT_PATH = str(FONTS_DIR / "enc_sans_sexp_bold_mplus_1p_2000em_med.ttf")


### fira mono bold text

FIRA_MONO_BOLD_FONT_HEIGHT = 20

FIRA_MONO_BOLD_FONT_PATH = str(FONTS_DIR / "fira_mono_bold_mplus_1m_med.ttf")


### nodezator icons font
ICON_FONT_PATH = str(FONTS_DIR / "nodezator_icons.ttf")


### noto sans fonts (used for hyper text)

NOTO_SANS_FONT_HEIGHT = 22

NOTO_SANS_REGULAR_FONT_PATH = str(FONTS_DIR / "noto_sans_regular.ttf")

NOTO_SANS_BOLD_FONT_PATH = str(FONTS_DIR / "noto_sans_bold.ttf")

NOTO_SANS_ITALIC_FONT_PATH = str(FONTS_DIR / "noto_sans_italic.ttf")

NOTO_SANS_MONO_MEDIUM_FONT_HEIGHT = 22

NOTO_SANS_MONO_MEDIUM_FONT_PATH = str(FONTS_DIR / "noto_sans_mono_medium.ttf")
