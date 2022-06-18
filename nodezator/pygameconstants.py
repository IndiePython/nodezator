"""App constants."""

### third-party imports

from pygame         import init as init_pygame
from pygame.key     import set_repeat
from pygame.time    import Clock
from pygame.image   import load as load_image
from pygame.display import set_mode, set_icon, set_caption

from pygame.mixer import pre_init as pre_init_mixer


### local imports
from appinfo import FULL_TITLE, ABBREVIATED_TITLE


### pygame mixer pre-initialization
pre_init_mixer(44100, -16, 2, 4096)

### pygame initialization
init_pygame()

### framerate-related constants/behaviour

_CLOCK       = Clock()
maintain_fps = _CLOCK.tick

FPS = 30

### set caption and icon for window

set_caption(FULL_TITLE, ABBREVIATED_TITLE)
set_icon(load_image('app_icon.png'))

### set key repeating (unit: milliseconds)
set_repeat(500, 30) # set_repeat(delay, interval)


### screen setup/constants

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
FLAG, DEPTH = 0, 32

### uncomment for no-frame mode
#
#from pygame import NOFRAME
#FLAG = NOFRAME
###############################

SCREEN = set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), FLAG, DEPTH)

blit_on_screen = SCREEN.blit

SCREEN_RECT = SCREEN.get_rect()
