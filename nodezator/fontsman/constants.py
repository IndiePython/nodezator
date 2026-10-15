"""Constants for fonts in the app."""

### local imports

from ..config import FONTS_DIR, LANGUAGES_SAMPLE_TEXT_FILEPATH

from ..ourstdlibs.pyl import load_pyl



### enc sans bold text

ENC_SANS_BOLD_FONT_HEIGHT = 17

ENC_SANS_BOLD_FONT_PATH = FONTS_DIR / 'encode_sans_semi_expanded_bold.ttf'


### fira mono bold text

FIRA_MONO_BOLD_FONT_HEIGHT = 20

FIRA_MONO_BOLD_FONT_PATH = FONTS_DIR / 'fira_mono_bold.ttf'


### nodezator icons font
ICON_FONT_PATH = FONTS_DIR / 'nodezator_icons.ttf'


### noto sans fonts (used for hyper text)

NOTO_SANS_FONT_HEIGHT = 22

NOTO_SANS_REGULAR_FONT_PATH = FONTS_DIR / 'noto_sans_regular.ttf'

NOTO_SANS_BOLD_FONT_PATH = FONTS_DIR / 'noto_sans_bold.ttf'

NOTO_SANS_ITALIC_FONT_PATH = FONTS_DIR / 'noto_sans_italic.ttf'

NOTO_SANS_MONO_MEDIUM_FONT_HEIGHT = 22

NOTO_SANS_MONO_MEDIUM_FONT_PATH = FONTS_DIR / 'noto_sans_mono_medium.ttf'


### sample text map

SAMPLE_TEXT_MAP = {
    locale.lower().replace('-', '_'): sample_text
    for locale, sample_text in load_pyl(LANGUAGES_SAMPLE_TEXT_FILEPATH).items()
}
