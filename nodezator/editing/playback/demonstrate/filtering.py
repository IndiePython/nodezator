
### local import
from .constants import DEMONSTRATIONS


def filter_demonstrations(self, filter_text):
    """Filter existing demonstrations based on text from search box."""
    ### if filter text is the same as the last one, return
    if filter_text == self.last_filter_text:
        return

    ### if there's filter text, filter items

    if filter_text:

        filtered_items = [
            item
            for item in DEMONSTRATIONS
            if item_matches_filter(item, filter_text)
        ]

        ###
        self.list_box.set_items(filtered_items)

    ### otherwise, restore all items
    else:
        self.list_box.set_items(DEMONSTRATIONS)

    ###
    self.last_filter_text = filter_text

def item_matches_filter(item, filter_text):
    return filter_text.lower() in item.lower()
