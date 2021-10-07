#! /usr/bin/env python3

### standard library imports

from argparse import ArgumentParser

from io import StringIO

from contextlib import redirect_stdout


### third-party import

with redirect_stdout(StringIO()):
    import pygame as pg


def main():
    """Execute app."""
    ### received filepath is ignored for now
    ### (we do nothing with it)
    _ = filepath_from_parsed_arguments()

    ###

    pg.init()

    pg.display.set_caption("Nodezator", "NDZ")

    screen = pg.display.set_mode((400, 400), 0, 32)

    screen.fill((200, 200, 200))

    screen_top_text = "Press <ESCAPE> to exit"

    text_surf = pg.font.Font(None, 28).render(
                                         screen_top_text,
                                         True,
                                         (20, 20, 20)
                                       )

    screen.blit(text_surf, (10, 10))

    running = True

    while running:
        
        ### event processing

        for event in pg.event.get():
            
            if event.type == pg.QUIT:

                running = False

            elif event.type == pg.KEYUP:

                if event.key == pg.K_ESCAPE:

                    running = False

        ### drawing
        pg.display.update()

    pg.quit()

def filepath_from_parsed_arguments():
    """Parse and return arguments."""

    description = """Future python node editor

    Release date: until 2021-12-01

    For now only a dummy message appears when executed.
    """

    parser = ArgumentParser(
               description="Future python node editor"
             )

    parser.add_argument(
             'filepath',
             type=str,
             nargs='?',
             default="",
             help="file to be opened."
           )

    return parser.parse_args().filepath

if __name__ == '__main__':
    main()
