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

"""This module contains the code for end-to-end video processing."""

import dataclasses as dc
import json
import logging
import os

import audio_processing as ap
import gps_processing as gp
import job_config as jc
import repository as repo
import utils
import video_processing as vp


def process_video(
    video_path: str,
    audio_path: str,
    gps_path: str,
    repository: repo.Repository,
    job_config: jc.EndToEndConfig,
    logger: logging.Logger,
) -> None:
    """Processes a video file and loads it into a repository.

    The steps to processing a video are:

    1. Extract the audio from the video.
    2. Transcribe the audio.
    3. Extract the GPS data from the video.
    4. Load the video, audio, and GPS data into the repository.

    Args:
        video_path (str): Path to the video file.
        logger (logging.Logger): Logger object.
    """
    logger.info(f"Processing video: {video_path}")

    # Extract the audio from the video
    vp.extract_audio(video_path, audio_path, logger=logger)
    video_metadata = vp.get_metadata(video_path, logger=logger)

    # transcribe the audio
    # transcript is a dataframe with the columns:
    # - word: str
    # - start: float
    # - end: float
    # - probablity: float
    word_segments = ap.transcribe_audio(
        audio_path, job_config.transcription_config, logger=logger
    )

    # Extract the GPS data from the video
    # gps_data is a dataframe with the columns:
    # - relative_time: float64
    # - utc_time: float
    # - latitude: float
    # - longitude: float
    # - altitude_m: float
    # - speed_kmh: float
    gps_data = gp.extract_gps_data(
        gps_path, job_config.source_video_type, logger=logger
    )

    # Load the video, audio, and GPS data into the repository
    fname = lambda f: os.path.split(f)[-1]

    video_kwargs = dict(
        filename=fname(video_path),
        checksum=utils.get_checksum(video_path),
        gps_filename=fname(gps_path),
        metadata=json.dumps(video_metadata),
    )

    audio_kwargs = dict(
        filename=fname(audio_path),
        checksum=utils.get_checksum(audio_path),
    )

    transcription_kwargs = dict(
        config=json.dumps(dc.asdict(job_config.transcription_config)),
    )

    word_segmentation_kwargs = word_segments.to_dict(orientation="list")

    gps_kwargs = gps_data.to_dict(orientation="list")

    repository.save_data(
        video_kwargs=video_kwargs,
        audio_kwargs=audio_kwargs,
        transcription_kwargs=transcription_kwargs,
        word_segmentation_kwargs=word_segmentation_kwargs,
        gps_kwargs=gps_kwargs,
    )
