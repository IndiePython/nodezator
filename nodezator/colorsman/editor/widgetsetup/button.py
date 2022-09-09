"""Button creation for the colors editor class."""

### standard library import
from functools import partial


### local imports

from ....ourstdlibs.collections.general import CallList

from ....ourstdlibs.behaviour import get_oblivious_callable

from ....textman.render import render_text

from ....surfsman.icon import render_layered_icon

from ....surfsman.draw import draw_depth_finish
from ....surfsman.render import render_rect, combine_surfaces

from ....classes2d.single import Object2D
from ....classes2d.collections import List2D

from ...colors import BLACK, WHITE, BUTTON_FG, BUTTON_BG, WINDOW_FG, WINDOW_BG

from .constants import (
    FONT_HEIGHT,
    TEXT_PADDING,
    ICON_HEIGHT,
    ICON_PADDING,
    ICON_BG_HEIGHT,
)

## widgets

from ....widget.checkbutton import CheckButton

from ....widget.optionmenu.main import OptionMenu

from ....widget.sortingbutton import SortingButton


def setup_buttons(self):
    """Create and set up buttons (and similar widgets).

    Function meant to be injected in the ColorsEditor
    class. Handles the creation of buttons and other
    widgets that work like ones.

    Not all widgets which work as buttons are created
    in this method. Entries, which also work as buttons,
    are later created in another method and stored in the
    same list as the buttons created here.
    """
    ### create a special list to hold buttons; the list is
    ### stored in its own attribute, as well as referenced
    ### locally
    buttons = self.buttons = List2D()

    ### now proceed creating and appending all different
    ### buttons

    buttons.extend(
        Object2D.from_surface(
            render_layered_icon(
                chars=[chr(ordinal)],
                dimension_name="height",
                dimension_value=ICON_HEIGHT,
                colors=[color],
                background_color=BUTTON_BG,
                background_width=ICON_BG_HEIGHT,
                background_height=ICON_BG_HEIGHT,
                rotation_degrees=rotation_degrees,
                flip_x=flip_x,
                depth_finish_thickness=1,
            )
        )
        for ordinal, color, rotation_degrees, flip_x in (
            (82, BUTTON_FG, 90, False),
            (82, BUTTON_FG, 90, True),
            (66, (204, 0, 0), 0, False),
            (78, (102, 255, 102), 0, False),
            (105, BUTTON_FG, 0, False),
        )
    )

    reverse_arrows = [
        render_layered_icon(
            chars=[chr(97)],
            dimension_name="height",
            dimension_value=ICON_HEIGHT,
            colors=[BUTTON_FG],
            background_width=ICON_BG_HEIGHT,
            background_height=ICON_BG_HEIGHT,
            offset_pos_by=(-ICON_PADDING, 0),
            rotation_degrees=rotation_degrees,
        )
        for rotation_degrees in (90, 90 * 3)
    ]

    buttons.append(
        Object2D.from_surface(
            combine_surfaces(
                reverse_arrows,
                retrieve_pos_from="center",
                assign_pos_to="center",
                background_color=BUTTON_BG,
            )
        )
    )

    draw_depth_finish(buttons[-1].image)

    ###

    shuffle_arrows = [
        render_layered_icon(
            chars=[chr(95)],
            dimension_name="height",
            dimension_value=ICON_HEIGHT,
            colors=[BUTTON_FG],
            offset_pos_by=(0, -1),
            background_width=ICON_BG_HEIGHT,
            background_height=ICON_BG_HEIGHT,
            flip_y=flip_y,
        )
        for flip_y in (False, True)
    ]

    buttons.append(
        Object2D.from_surface(
            combine_surfaces(
                shuffle_arrows,
                retrieve_pos_from="center",
                assign_pos_to="center",
                background_color=BUTTON_BG,
            )
        )
    )

    draw_depth_finish(buttons[-1].image)

    ###

    equal_surf = render_layered_icon(
        chars=[chr(164)],
        dimension_name="height",
        dimension_value=ICON_HEIGHT,
        colors=[BUTTON_FG],
        background_width=ICON_BG_HEIGHT,
        background_height=ICON_BG_HEIGHT,
    )

    equal_equal = combine_surfaces(
        [equal_surf, equal_surf], offset_pos_by=(-(ICON_PADDING * 3) // 2, 0)
    )

    x_surf = render_layered_icon(
        chars=[chr(126)],
        dimension_name="height",
        dimension_value=ICON_BG_HEIGHT // 2,
        colors=[(204, 0, 0)],
    )

    buttons.append(
        Object2D.from_surface(
            combine_surfaces(
                [equal_equal, x_surf],
                retrieve_pos_from="bottomright",
                assign_pos_to="bottomright",
                background_color=BUTTON_BG,
            )
        )
    )

    draw_depth_finish(buttons[-1].image)

    ###

    buttons.extend(
        Object2D.from_surface(
            render_text(
                text=text,
                font_height=FONT_HEIGHT,
                padding=TEXT_PADDING,
                depth_finish_thickness=1,
                foreground_color=BUTTON_FG,
                background_color=BUTTON_BG,
            )
        )
        for text in ("HTML colors", "Pygame colors", "Import", "Export", "Ok", "Cancel")
    )

    ### reference each button locally so we can configure
    ### them further ahead

    (
        move_left_button,
        move_right_button,
        remove_color_button,
        add_color_button,
        sort_colors_button,
        reverse_order_button,
        shuffle_button,
        remove_duplicates_button,
        html_colors_button,
        pygame_colors_button,
        import_colors_button,
        export_colors_button,
        ok_button,
        cancel_button,
    ) = buttons

    ### create additional objects to use as buttons

    ## an option menu to help when adding new colors
    ##
    ## the order of the options is somewhat arbitrary,
    ## but the choice of lightness as the selected value
    ## is due to the fact that we think it is more likely
    ## that someone may want to vary that property when
    ## creating new colors

    options = [
        "lightness",
        "saturation",
        "value",
        "hue",
        "red",
        "green",
        "blue",
        "alpha",
        "luma",
    ]

    color_add_option_menu = self.color_add_option_menu = OptionMenu(
        loop_holder=self,
        value=options[0],
        options=options,
        draw_on_window_resize=self.draw,
    )

    buttons.append(color_add_option_menu)

    ## a seq sorting button widget used to sort the
    ## properties used for sorting colors as desired
    ##
    ## the order of the available items are not relevant,
    ## since they are only taken into account when inserted
    ## in the list used as the 'value' argument

    available_items = {
        "hue",
        "saturation",
        "value",
        "red",
        "green",
        "blue",
        "alpha",
        "luma",
    }

    color_sorting_holder = self.color_sorting_holder = SortingButton(
        ## we use ["hue"] for the value because we think
        ## it is more likely that someone may want to sort
        ## the colors by that property, but we could have
        ## picked any other property or combination of
        ## properties we wanted
        value=["hue"],
        available_items=available_items,
    )

    buttons.append(color_sorting_holder)

    ## checkbutton to use as a flag so the user can specify
    ## whether to use alpha or not, accompanied by a label
    ## which will work as a button

    ## checkbutton

    alpha_checkbutton = self.alpha_checkbutton = CheckButton(
        value=False, size=18, name="use_alpha"
    )

    ## check button label

    on_mouse_click = alpha_checkbutton.toggle_value

    alpha_checkbutton_label = Object2D.from_surface(
        surface=render_text(
            text="Use alpha:",
            font_height=FONT_HEIGHT,
            padding=TEXT_PADDING,
            foreground_color=WINDOW_FG,
            background_color=WINDOW_BG,
        ),
        on_mouse_click=on_mouse_click,
    )

    ## store both as buttons

    buttons.extend((alpha_checkbutton, alpha_checkbutton_label))

    ## button to invoke the colors viewer, to visualize
    ## the current colors

    # viewer icon surface

    view_button_surf = render_layered_icon(
        chars=[chr(ordinal) for ordinal in (87, 88, 89)],
        dimension_name="height",
        dimension_value=22,
        colors=[BLACK, WHITE, (115, 40, 30)],
        background_width=27,
        background_height=27,
    )

    # button object with BUTTON_BG background
    view_button = Object2D.from_surface(
        render_rect(*view_button_surf.get_size(), color=BUTTON_BG)
    )

    # blit icon over button object's image
    view_button.image.blit(view_button_surf, (0, 0))

    # blit an outline around button object's image to
    # convey depth
    draw_depth_finish(view_button.image)

    # then store the button
    buttons.append(view_button)

    ### reference the colors panel locally, since we'll
    ### reference it so much futher ahead
    colors_panel = self.colors_panel

    ### now that all buttons are created, position each
    ### one and also assign a command to their
    ### 'on_mouse_release' attribute (except the
    ### checkbutton, which receives the command in its
    ### 'command' attribute)
    ###
    ### note that the commands assigned to
    ### 'on_mouse_release' are passed through
    ### get_oblivious_callable() before being assigned;
    ###
    ### this is done so the commands ignore the event
    ### object they receive when the buttons are clicked,
    ### because since they originally don't have any
    ### parameters, they would raise an exception when
    ### receiving the event as an argument
    ###
    ### (only commands which originally accept such event
    ### object wouldn't need this additional step)

    ## "move left" button

    move_left_button.rect.topleft = colors_panel.rect.move(85, 5).bottomleft

    move_left_button.on_mouse_release = get_oblivious_callable(
        colors_panel.widget_to_left
    )

    ## "move right" button

    move_right_button.rect.topleft = move_left_button.rect.move(5, 0).topright

    move_right_button.on_mouse_release = get_oblivious_callable(
        colors_panel.widget_to_right
    )

    ## "remove color" button

    remove_color_button.rect.topleft = move_right_button.rect.move(5, 0).topright

    remove_color_button.on_mouse_release = get_oblivious_callable(
        colors_panel.remove_color_widgets
    )

    ## "add color" button

    add_color_button.rect.topleft = remove_color_button.rect.move(5, 0).topright

    add_color_button.on_mouse_release = get_oblivious_callable(
        colors_panel.add_new_color_widget
    )

    ## "creation properties" option menu

    midleft = add_color_button.rect.move(5, 0).midright
    color_add_option_menu.rect.midleft = midleft

    ## sort button

    sort_colors_button.rect.midleft = color_add_option_menu.rect.move(20, 0).midright

    sort_colors_button.on_mouse_release = get_oblivious_callable(
        colors_panel.sort_colors
    )

    ## property sorting button

    midleft = sort_colors_button.rect.move(5, 0).midright
    color_sorting_holder.rect.midleft = midleft

    ## "reverse order" button

    reverse_order_button.rect.midleft = color_sorting_holder.rect.move(20, 0).midright

    reverse_order_button.on_mouse_release = get_oblivious_callable(
        colors_panel.reverse_color_order
    )

    ## shuffle button

    shuffle_button.rect.topleft = reverse_order_button.rect.move(5, 0).topright

    shuffle_button.on_mouse_release = get_oblivious_callable(
        colors_panel.shuffle_color_order
    )

    ## "remove duplicates" button

    remove_duplicates_button.rect.topleft = shuffle_button.rect.move(5, 0).topright

    remove_duplicates_button.on_mouse_release = get_oblivious_callable(
        colors_panel.remove_duplicated_colors
    )

    ## "html colors" button

    html_colors_button.rect.topleft = colors_panel.rect.move(25, 38).bottomleft

    html_colors_button.on_mouse_release = get_oblivious_callable(
        colors_panel.pick_html_colors
    )

    ## "pygame colors" button

    pygame_colors_button.rect.topleft = html_colors_button.rect.move(5, 0).topright

    pygame_colors_button.on_mouse_release = get_oblivious_callable(
        colors_panel.pick_pygame_colors
    )

    ## "import" button

    import_colors_button.rect.topleft = pygame_colors_button.rect.move(5, 0).topright

    import_colors_button.on_mouse_release = get_oblivious_callable(
        colors_panel.import_colors
    )

    ## "export" button

    export_colors_button.rect.topleft = import_colors_button.rect.move(5, 0).topright

    export_colors_button.on_mouse_release = get_oblivious_callable(
        colors_panel.export_colors
    )

    ## ok button

    bottomright = self.rect.move(-10, -10).bottomright
    ok_button.rect.bottomright = bottomright

    ok_button.on_mouse_release = get_oblivious_callable(self.exit_loop)

    ## cancel button
    ##
    ## since the cancel command is also of interest
    ## elsewhere, we store it in its own attribute as well

    bottomright = ok_button.rect.move(-10, 0).bottomleft
    cancel_button.rect.bottomright = bottomright

    self.cancel = CallList(
        [
            partial(setattr, self, "cancel_edition", True),
            self.exit_loop,
        ]
    )

    cancel_button.on_mouse_release = get_oblivious_callable(self.cancel)

    ## alpha checkbutton and its label (positioned relative
    ## to the alpha scale)

    # checkbutton

    midright = self.scale_map["alpha"].rect.move(-10, 0).midleft
    alpha_checkbutton.rect.midright = midright

    alpha_checkbutton.command = self.update_from_rgb_entry

    # checkbutton label

    alpha_checkbutton_label.rect.midright = alpha_checkbutton.rect.move(-2, -2).midleft

    ## view button

    midleft = remove_duplicates_button.rect.move(5, 0).midright
    view_button.rect.midleft = midleft

    view_button.on_mouse_release = get_oblivious_callable(colors_panel.view_colors)
