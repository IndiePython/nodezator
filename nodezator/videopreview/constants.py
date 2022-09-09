### standard library imports

from subprocess import run as run_subprocess

from ast import literal_eval

from shlex import split as split_like_shell


### local import
from ..ourstdlibs.mathutils import math_eval


def get_video_metadata(video_path):

    ### extract media data

    command_text = (
        "ffprobe -v error -select_streams v:0 -show_streams" f" {video_path!r}"
    )

    try:
        completed_process = run_subprocess(
            split_like_shell(command_text), capture_output=True
        )

    except Exception as err:
        raise

    video_stream = {}

    for line_text in completed_process.stdout.decode().splitlines():

        head, sep, tail = line_text.partition("=")

        if sep == "=":
            video_stream[head] = tail

    ###

    metadata = {}

    for key in ("width", "height"):
        metadata[key] = video_stream[key]

    metadata["fps"] = round(math_eval(video_stream["avg_frame_rate"]))

    ###
    return metadata
