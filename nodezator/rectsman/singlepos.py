"""Class extension for rectsman.main.RectsManager class."""

### standard library import
from operator import attrgetter


### third-party import
from pygame import Rect


### class definition


class PositionSingleRectsMethods:
    """Methods to position individual rects."""

    ### XXX snap_rects_ip method:
    ### which one from list below would be faster for
    ### offsetting?
    ### - rect.move;
    ### - Vector2;
    ### - map(operator.add, zip(pos, offset))
    ###
    ### edit: this may not be relevant anymore, since
    ### using rect.move allows me to work with coordinates
    ### like 'bottom', 'left', etc., instead of just
    ### their combinations ('topleft', 'bottomleft', etc.),
    ### thus being more versatile;

    ### XXX maybe create new partial methods from the
    ### one below to perform common operations easily;
    ###
    ### for instance:
    ###
    ### - rectsman_instance.topright_to_topleft_ip();
    ### - rectsman_instance.bottomright_to_bottomleft_ip();
    ### - (and so on...).
    ###
    ### also, could this perhaps be created
    ### programatically? for instance, maybe this
    ### could work?:
    ###
    ### for pos_name_a, pos_name_b in combinations(
    ###   'topleft',
    ###   'topright',
    ###   'midtop',
    ###   (and so on...)
    ### ):
    ###
    ###    functools.partialmethod(
    ###                snap_rects_ip,
    ###                pos_name_a,
    ###                pos_name_b
    ###              )
    ###
    ### probably I would work if it is in the module level
    ### after the class definition, since the "for loop"
    ### would affect the class def namespace if it was in
    ### the class def body;

    def snap_rects_ip(
        self,
        retrieve_pos_from="topright",
        assign_pos_to="topleft",
        offset_pos_by=(0, 0),
    ):
        """Align rects relative to each other.

        Usage
        =====

        Use to reposition each rect in relation to the
        other. Works by retrieving the position of one rect,
        applying an offset (which default to no offset at
        all) and assigning the position to the next rect.

        Parameters
        ==========

        retrieve_pos_from (string)
            name of pygame.Rect attribute from which to
            retrieve position information in one rect in
            order to assign such position information to
            the next rect.
        assign_pos_to (string)
            name of pygame.Rect attribute to which assign
            the position information retrieved from the
            previoius rect.
        offset_pos_by (tuple/list with 02 integers)
            represent an offset to be applied to the
            retrieved position.
        """
        for rect in self._get_all_rects():

            try:
                setattr(rect, assign_pos_to, pos)
            except NameError:
                pass

            pos = getattr(
                rect.move(offset_pos_by),
                retrieve_pos_from,
            )

    ### TODO docstring, comment and doctests functions below

    def snap_rects_intermittently_ip(
        self,
        ### interval limit
        dimension_name,  # either 'width' or 'height'
        dimension_unit,  # either 'rects' or 'pixels'
        max_dimension_value,  # positive integer
        ### rect positioning
        retrieve_pos_from="topright",
        assign_pos_to="topleft",
        offset_pos_by=(0, 0),
        ### intermittent rect positioning
        intermittent_pos_from="bottomleft",
        intermittent_pos_to="topleft",
        intermittent_offset_by=(0, 0),
    ):
        """Like snap_rects_ip, but changes intermittently."""
        backed_up_topleft = self.topleft

        if max_dimension_value <= 0:

            raise ValueError(
                """
                    'max_dimension_value' must be a
                    positive integer.
                    """
            )

        rects = [rect for rect in self._get_all_rects()]
        ###

        if dimension_unit == "pixels":

            largest_rect = max(rects, key=attrgetter(dimension_name))

            largest_dimension = getattr(largest_rect, dimension_name)

            if largest_dimension > max_dimension_value:

                raise ValueError(
                    f"""
                    the rects can't be constrained to
                    the {max_dimension_value} {dimension_name}
                    in pixels because the cell exceeds that
                    measurement.
                  """
                )

        temp_rect_list = []

        temp_rectsman = self.__class__(temp_rect_list.__iter__)

        get_limit = get_limit_func(dimension_name, dimension_unit)

        next_rect_pos = (0, 0)

        for rect in rects:

            setattr(rect, assign_pos_to, next_rect_pos)

            temp_rect_list.append(rect)

            if get_limit(temp_rect_list) > max_dimension_value:

                temp_rect_list.pop()

                intermittent_pos = getattr(
                    temp_rectsman.move(intermittent_offset_by),
                    intermittent_pos_from,
                )

                temp_rect_list.clear()
                temp_rect_list.append(rect)

                setattr(
                    rect,
                    intermittent_pos_to,
                    intermittent_pos,
                )

            next_rect_pos = getattr(
                rect.move(offset_pos_by),
                retrieve_pos_from,
            )

        self.topleft = backed_up_topleft

    def lay_rects_like_table_ip(
        self,
        ### table boundary limit
        dimension_name,
        dimension_unit,
        max_dimension_value,
        ### cell/row positioning
        intercell_pos_from="topright",
        intercell_pos_to="topleft",
        interrow_pos_from="bottomleft",
        interrow_pos_to="topleft",
        ### cell to rect positioning
        cell_pos_from="center",
        rect_pos_to="center",
        cell_padding=0,
    ):
        """Align rects as if they were inside table cells.

        Parameters
        ==========
        """
        ### backup our topleft
        backed_up_topleft = self.topleft

        ###

        if max_dimension_value <= 0:

            raise ValueError(
                """
                    'max_dimension_value' must be a
                    positive integer.
                    """
            )

        ###
        rects = [rect for rect in self._get_all_rects()]

        ###
        quantity = len(rects)

        ###

        largest_width = max(rect.width for rect in rects)
        largest_height = max(rect.height for rect in rects)

        ###

        inflation_amount = cell_padding * 2

        single_cell_rect = Rect(0, 0, largest_width, largest_height).inflate(
            inflation_amount, inflation_amount
        )

        ###

        if dimension_unit == "pixels":

            largest_dimension = getattr(single_cell_rect, dimension_name)

            if largest_dimension > max_dimension_value:

                raise ValueError(
                    f"""
                    the table can't be constrained to
                    the {max_dimension_value}
                    {dimension_name} in pixels
                    because the cell exceeds that
                    measurement.
                  """
                )

        ### (what is quicker: copying or instantiating each
        ### rect?)

        cell_rects = [single_cell_rect.copy() for rect in rects]

        ###

        row_cells = []
        row_rectsman = self.__class__(row_cells.__iter__)

        row_breaking_limit = max_dimension_value

        get_limit = get_limit_func(dimension_name, dimension_unit)

        ###

        next_cell_pos = (0, 0)

        rects.reverse()

        while cell_rects:

            ## obtain and position a cell rect

            cell_rect = cell_rects.pop()

            setattr(cell_rect, intercell_pos_to, next_cell_pos)

            ## append it in a row of cells
            row_cells.append(cell_rect)

            ## break row if limit was surpassed

            if get_limit(row_cells) > row_breaking_limit:

                row_cells.pop()

                row_pos = getattr(row_rectsman, interrow_pos_from)

                row_cells.clear()

                row_cells.append(cell_rect)

                setattr(row_rectsman, interrow_pos_to, row_pos)

            ## obtain a rect and position it relative to
            ## the cell rect

            rect_pos = getattr(cell_rect, cell_pos_from)
            setattr(rects.pop(), rect_pos_to, rect_pos)

            ## obtain pos for next cell

            next_cell_pos = getattr(cell_rect, intercell_pos_from)

        ### restore our topleft
        self.topleft = backed_up_topleft

    def snap_rects_to_points_ip(
        self,
        attributes_names,
        points,
    ):
        ###
        backed_up_topleft = self.topleft

        ###
        for rect, attr_name, point in zip(
            self._get_all_rects(),
            attributes_names,
            points,
        ):
            setattr(rect, attr_name, point)

        self.topleft = backed_up_topleft


### small utility functions


def get_total_width(rects):
    return max(rect.right for rect in rects) - min(rect.left for rect in rects)


def get_total_height(rects):

    return max(rect.bottom for rect in rects) - min(rect.top for rect in rects)


def get_limit_func(dimension_name, dimension_unit):

    return (
        (get_total_width if dimension_name == "width" else get_total_height)
        if dimension_unit == "pixels"
        else len
    )
