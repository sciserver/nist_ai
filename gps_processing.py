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

"""This module contains functions for processing GPS data."""

import logging
import os

import pandas as pd

import job_config as jc


# TODO: Maybe this should stream to file instead of loading everything into memory
#       and then we could also do a bulk import into the database
def parse_trackaddict_gps(
    gps_csv_path: str,
    logger: logging.Logger,
) -> pd.DataFrame:
    """Parses GPS data from a TrackAddict CSV file.

    The CSV file is expected to have the following columns:
    - Time
    - UTC Time
    - Latitude
    - Longitude
    - Altitude (m)
    - Speed (Km/h)

    The function returns a DataFrame with the following columns and types:
    - relative_time: float64
    - utc_time: float64
    - latitude: float64
    - longitude: float64
    - altitude_m: float32
    - speed_kmh: float32


    Args:
        gps_csv_path (str): Path to the CSV file.
        logger (logging.Logger): Logger object.

    Returns:
        pd.DataFrame: GPS data.

    Raises:
        FileNotFoundError: If `gps_csv_path` does not exist.
    """

    if not os.path.exists(gps_csv_path):
        msg = f"File not found at {gps_csv_path}"
        logger.error(msg)
        raise FileNotFoundError(msg)

    return pd.read_csv(
        gps_csv_path,
        engine="c",
        comment="#",
        dtype={
            "Time": "float64",
            "UTC Time": "float64",
            "Latitude": "float64",
            "Longitude": "float64",
            "Altitude (m)": "float32",
            "Speed (Km/h)": "float32",
        },
        usecols=[
            "Time",
            "UTC Time",
            "Latitude",
            "Longitude",
            "Altitude (m)",
            "Speed (Km/h)",
        ],
    ).rename(
        columns={
            "Time": "relative_time",
            "UTC Time": "utc_time",
            "Latitude": "latitude",
            "Longitude": "longitude",
            "Altitude (m)": "altitude_m",
            "Speed (Km/h)": "speed_kmh",
        }
    )


def parse_gps_file(
    gps_file_path: str,
    video_type: jc.VideoType,
    logger: logging.Logger = logging.getLogger(__name__),
) -> pd.DataFrame:
    if video_type == jc.VideoType.TRACK_ADDICT:
        return parse_trackaddict_gps(gps_file_path, logger)
    else:
        msg = f"Unsupported video type {video_type}"
        logger.error(msg)
        raise ValueError(msg)
