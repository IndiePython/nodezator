
### standard library import
from pathlib import Path


### local imports

from ..appinfo import TITLE, ABBREVIATED_TITLE

from .constants import PYGAME_CE_REQUIRED_MESSAGE



def display_dialog_and_quit(pygame_module):

    pg = pygame_module

    pg.init()

    ###
    data_dir = Path(__file__).parent.parent / 'data'

    ### set icon and caption for window

    pg.display.set_icon(pg.image.load(str(data_dir / "app_icon.png")))
    pg.display.set_caption(TITLE, ABBREVIATED_TITLE)

    ###

    screen = pg.display.set_mode((640, 220))

    screen.fill((70, 70, 90))
    screen_rect = screen.get_rect()
    blit_on_screen = screen.blit

    nodezator_logo = (
        pg.image.load(str(data_dir / 'images' / 'nodezator_logo.png'))
    ).convert_alpha()

    nodezator_logo_rect = nodezator_logo.get_rect().move(10, 30)
    blit_on_screen(nodezator_logo, nodezator_logo_rect)

    top = 30
    left = nodezator_logo_rect.move(10, 0).right
    width = screen_rect.width - left - 10

    blitting_area = pg.Rect(left, top, width, screen_rect.height-10)

    render_text = pg.font.Font(None, 24).render

    space_width, line_height = render_text(' ', True, 'black').get_size()

    topleft = blitting_area.topleft

    ###

    for line in PYGAME_CE_REQUIRED_MESSAGE.splitlines():

        for word in line.split():

            text_surf = render_text(word, True, 'white')
            text_rect = text_surf.get_rect().move(topleft)

            if not blitting_area.contains(text_rect):

                text_rect.left = blitting_area.left
                text_rect.top += line_height

            blit_on_screen(text_surf, text_rect)

            topleft = text_rect.move(space_width, 0).topright

        topleft = (
            blitting_area.left,
            topleft[1] + line_height
        )

    maintain_fps = pg.time.Clock().tick

    running = True

    while running:

        maintain_fps(24)

        for event in pg.event.get():

            if (
                event.type == pg.QUIT
                or (
                    event.type == pg.KEYDOWN
                    and event.key == pg.K_ESCAPE
                )
            ):

                running = False

        pg.display.update()

    pg.quit()
    quit()
