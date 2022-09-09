### local import
from .list import ListWidget


class SetWidget(ListWidget):
    def get(self):
        return set(super().get())
