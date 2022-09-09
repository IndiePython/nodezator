### standard library import
from pathlib import Path


class UnattainableFontHeight(ValueError):
    def __init__(self, font_path, desired_height):

        ### create a string representing a message with
        ### information about the font whose desired height
        ### couldn't be achieved

        message = (
            f"couldn't get text of height {desired_height}"
            f" from {Path(font_path).name} font file"
        )

        ### initialize superclass with custom message
        super().__init__(message)
