"""Scale widgets creation for the colors editor class."""

### local imports

from ....imagesman.cache import IMAGE_SURFS_DB

from ....classes2d.collections import List2D

from ....our3rdlibs.scale import Scale


def setup_scales(self):
    """Create and set up scale widgets.

    Function meant to be injected in the ColorsEditor
    class. Handles the creation of scale widgets.
    """
    ### create special list to store scales, storing it
    ### in its own attribute as well as referencing it
    ### locally
    scales = self.scales = List2D()

    ### define a starting position from where to position
    ### the scales
    x, y = self.rect.move(144, 225).topleft

    ### define a vertical padding (space between the scale
    ### widgets)
    vertical_padding = 10

    ### get an image whose subsurfaces represent scales

    scales_surf = IMAGE_SURFS_DB["colors_editor_scale_images.png"][{"use_alpha": False}]

    ### using the surface we just got, create a map whose
    ### keys are names of scales and the values are surfaces
    ### representing that scales;
    ###
    ### the surfaces are subsurfaces of the image mentioned
    ### above;
    ###
    ### since the subsurfaces representing scales are
    ### stack one on top of the other, and all scales have
    ### the same height of 32 pixels, we use indices
    ### representing the top coordinate of the rect
    ### containing the subsurface, and multiply such
    ### index by 32 to obtain the actual value of the top/y
    ### coordinate

    scale_name_to_surf = {
        scale_name: scales_surf.subsurface((0, top_index * 32, 370, 32))
        for scale_name, top_index in (
            ("Hue", 0),
            ("Lightness", 1),
            ("Saturation", 2),
            ("Value", 1),
            ("Red", 3),
            ("Green", 4),
            ("Blue", 5),
            ("Alpha", 6),
        )
    }

    ### define data for each scale; we'll iterate over
    ### such data in the next block to create each scale

    scale_data = (
        ("Hue", 0, 360, self.update_from_hls),
        ("Lightness", 50, 100, self.update_from_hls),
        ("Saturation", 100, 100, self.update_from_hls),
        ("Value", 100, 100, self.update_from_hsv),
        ("Red", 255, 255, self.update_from_rgb),
        ("Green", 0, 255, self.update_from_rgb),
        ("Blue", 0, 255, self.update_from_rgb),
        ("Alpha", 255, 255, self.update_from_alpha),
    )

    ### iterate over the data defined previously to create
    ### and store scales

    for name, initial_value, max_value, command in scale_data:

        ### instantiate scale (it is also positioned in
        ### this step)

        scale = Scale(
            value=initial_value,
            scale_surf=scale_name_to_surf[name],
            max_value=max_value,
            name=name,
            coordinates_value=(x, y),
            command=command,
        )

        ### store scale
        scales.append(scale)

        ### update the y coordinates to be assigned to
        ### the next scale

        y = (
            ## the current value of y
            y
            ## plus the height of the scale
            + scale.rect.height
            ## plus the vertical padding
            + vertical_padding
        )

    ### create a map to store specific groupings of scales
    ### (notice the alpha scale isn't grouped with any
    ### other scale, because it operates independently
    ### from all the others)

    self.scale_map = {
        "hls": scales[:3],
        "hsv": [scales[i] for i in (0, 2, 3)],
        "rgb": scales[4:7],
        "alpha": scales[7],
    }
