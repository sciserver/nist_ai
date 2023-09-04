# MIT License

# Copyright (c) 2023 sciserver

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""This module contains functions for processing videos."""

import logging
import os

try:
    import ffmpeg  # ffmpeg-python
except ImportError:
    raise ImportError(
        "ffmpeg-python not installed."
        "Please install it using `pip install ffmpeg-python`"
    )


def extract_audio(
    video_path: str,
    audio_path: str,
    logger: logging.Logger = logging.getLogger(__name__),
    overwrite: bool = False,
) -> None:
    """Extracts audio from a video at `video_path` and saves it to `audio_path`.

    Args:
        video_path (str): Path to the video file.
        audio_path (str): Path to save the audio file.
        logger (logging.Logger, optional): Logger object.
        overwrite (bool, optional): Should overwrite the existing audio file.

    Returns:
        None

    Raises:
        FileNotFoundError: If `video_path` does not exist.
    """
    if not os.path.exists(video_path):
        msg = f"Video file not found at {video_path}"
        logger.error(msg)
        raise FileNotFoundError(msg)

    if os.path.exists(audio_path) and not overwrite:
        logger.info(f"Audio file already exists at {audio_path}. Skipping...")
        return

    logger.info(f"Extracting audio from {video_path} to {audio_path}...")

    stdout, stderr = (
        ffmpeg.input(video_path)
        .output(audio_path)
        .run(capture_stdout=True, capture_stderr=True)
    )
    logger.info("ffmpeg stdout:" + stdout.decode())
    logger.error("ffmpeg stderr:" + stderr.decode())

    return


def get_metadata(
    video_path: str,
    logger: logging.Logger = logging.getLogger(__name__),
) -> dict:
    """Extracts metadata from a video at `video_path`.

    Args:
        video_path (str): Path to the video file.
        logger (logging.Logger, optional): Logger object.

    Returns:
        dict: Dictionary containing the metadata.
    """
    if not os.path.exists(video_path):
        msg = f"Video file not found at {video_path}"
        logger.error(msg)
        raise FileNotFoundError(msg)

    logger.info(f"Extracting metadata from {video_path}...")

    return ffmpeg.probe(video_path)


def get_thumbnail(
    video_path: str,
    width: int,
    time: float,
) -> bytes:
    """Extracts a thumbnail from  `video_path` at `time`.

    Args:
        video_path (str): Path to the video file.
        width (int): Width of the thumbnail.
        time (float): Time in seconds to extract the thumbnail.

    Returns:
        bytes: Thumbnail image data.

    Raises:
        FileNotFoundError: If `video_path` does not exist.
    """
    out, _ = (
        ffmpeg.input(video_path, ss=time)
        .filter("scale", width, -1)
        .output("pipe:", format="image2", vcodec="png", vframes=1)
        .run(capture_stdout=True, capture_stderr=True)
    )
    return out


if __name__ == "__main__":
    logging.basicConfig(
        filename="test.log",
        filemode="a",
        format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
        level=logging.DEBUG,
    )

    logger = logging.getLogger("test")

    extract_audio("vid.mp4", "audio.mp3", logger)


def save_clip(
    video_path: str,
    start: float,
    end: float,
    output_path: str,
) -> None:
    """Extracts a clip from  `video_path`.

    This will overwrite the file at `output_path` if it already exists.

    Args:
        video_path (str): Path to the video file.
        start (float): Start time in seconds to extract the clip.
        end (float): End time in seconds to extract the clip.
        output_path (str): Path to save the clip file.

    Returns:
        None

    Raises:
        FileNotFoundError: If `video_path` does not exist.
        ValueError: If `start` is negative.
        ValueError: If `start` is greater than `end`.
        ValueError: If `end` - `start` is less than 1 second.
    """
    if not os.path.exists(video_path):
        FileNotFoundError(f"Video file not found at {video_path}")

    if start < 0:
        ValueError("Start time cannot be negative.")

    if start > end:
        ValueError("Start time cannot be greater than end time.")

    if end - start < 1:
        ValueError("Clip duration cannot be less than 1 second.")

    (
        ffmpeg.input(video_path, ss=start, to=end)
        .output(output_path)
        .run(overwrite_output=True, quiet=True)
    )
    return


def get_video_length(video_path: str) -> float:
    """Returns the length of the video at `video_path` in seconds.

    Args:
        video_path (str): Path to the video file.

    Returns:
        float: Length of the video in seconds. -1 if length cannot be determined.

    Raises:
        FileNotFoundError: If `video_path` does not exist.
    """
    if not os.path.exists(video_path):
        FileNotFoundError(f"Video file not found at {video_path}")

    metadata = ffmpeg.probe(video_path)
    return float(metadata.get("format", {}).get("duration", -1))
