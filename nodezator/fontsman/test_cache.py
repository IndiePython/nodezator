from unittest import TestCase

import pygame

from .cache import get_font, FontsDatabase, FontsMap
from .constants import NOTO_SANS_MONO_MEDIUM_FONT_PATH, NOTO_SANS_MONO_MEDIUM_FONT_HEIGHT
from .exception import UnattainableFontHeight


class TestFontsDatabase(TestCase):
    def setUp(self) -> None:
        pygame.font.init()

    def test_get_font(self):
        path = NOTO_SANS_MONO_MEDIUM_FONT_PATH
        height = NOTO_SANS_MONO_MEDIUM_FONT_HEIGHT

        font = get_font(path, height)

        self.assertIsInstance(font, pygame.font.Font)

    def test_get_font_too_large_raises(self):
        path = NOTO_SANS_MONO_MEDIUM_FONT_PATH
        height = 65536

        with self.assertRaises(UnattainableFontHeight):
            get_font(path, height)

    def test_get_font_too_small_raises(self):
        path = NOTO_SANS_MONO_MEDIUM_FONT_PATH
        height = 1

        with self.assertRaises(UnattainableFontHeight):
            get_font(path, height)

    def test_fonts_db_returns(self):
        db = FontsDatabase()
        path = NOTO_SANS_MONO_MEDIUM_FONT_PATH
        height = NOTO_SANS_MONO_MEDIUM_FONT_HEIGHT

        font = db[path][height]

        self.assertIsInstance(font, pygame.font.Font)

    def test_fonts_map_stores(self):
        path = NOTO_SANS_MONO_MEDIUM_FONT_PATH
        height1 = NOTO_SANS_MONO_MEDIUM_FONT_HEIGHT
        height2 = height1 + 2

        m = FontsMap(path)

        font1_get1 = m[height1]
        font1_get2 = m[height1]

        self.assertIs(font1_get1, font1_get2)

        font2_get1 = m[height2]
        font2_get2 = m[height2]
        self.assertIs(font2_get1, font2_get2)

    def test_fonts_database_stores(self):
        db = FontsDatabase()
        path = NOTO_SANS_MONO_MEDIUM_FONT_PATH
        height = NOTO_SANS_MONO_MEDIUM_FONT_HEIGHT

        font1 = db[path][height]

        self.assertEqual(len(db), 1)

        font2 = db[path][height]

        self.assertIs(font1, font2)
        self.assertEqual(len(db), 1)
