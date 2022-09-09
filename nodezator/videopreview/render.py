### standard-library import

from pathlib import Path

from tempfile import TemporaryDirectory

from subprocess import run as run_subprocess

from shlex import split as split_like_shell


### third-party imports

from pygame import Rect, Surface

from pygame.image import load as load_image

from pygame.mixer import Sound


### local imports

from ..config import FFMPEG_AVAILABLE

from .constants import get_video_metadata

from ..surfsman.draw import draw_not_found_icon


### TODO review/refactor


def render_video_data(
    video_path,
    video_metadata_map,
    *,
    max_width=0,
    max_height=0,
    not_found_width=0,
    not_found_height=0,
):

    ### get metadata

    try:
        metadata = video_metadata_map[video_path]

    except KeyError:

        if FFMPEG_AVAILABLE and Path(video_path).is_file():

            metadata = video_metadata_map[video_path] = get_video_metadata(video_path)

            return get_frames(
                video_path,
                metadata,
                max_width,
                max_height,
            )

        else:

            surf = Surface((not_found_width, not_found_height)).convert()

            draw_not_found_icon(surf, (255, 0, 0))

            return [surf]

    else:

        return get_frames(
            video_path,
            metadata,
            max_width,
            max_height,
        )


def get_frames(video_path, metadata, max_width, max_height):
    """"""
    actual_width = int(metadata["width"])
    actual_height = int(metadata["height"])

    if not max_width:
        max_width = actual_width
    if not max_height:
        max_height = actual_height

    ### XXX using a formula would be quicker than
    ### Rect.fit()?
    final_width, final_height = (
        Rect(0, 0, actual_width, actual_height).fit(0, 0, max_width, max_height).size
    )

    ###
    fps = metadata["fps"]

    ###

    with TemporaryDirectory() as string_dir_path:

        dirpath = Path(string_dir_path)

        command_text = (
            f"ffmpeg -i {video_path!r} -s"
            f" {final_width}x{final_height}"
            f" -frames:v {fps * 3}"
            f' {dirpath / "img%04d.jpg"}'
        )

        try:
            run_subprocess(
                split_like_shell(command_text), capture_output=True, check=True
            )

        except Exception as err:
            raise

        else:

            frames = [load_image(str(path)) for path in sorted(dirpath.iterdir())]

    return frames
