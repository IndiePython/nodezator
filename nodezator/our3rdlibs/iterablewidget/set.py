

### local import
from our3rdlibs.iterablewidget.list import ListWidget


class SetWidget(ListWidget):
    
    def get(self):
        return set(super().get())
