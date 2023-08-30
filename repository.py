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

import pandas as pd

import job_config as jc


class BaseRepository:
    def get_video_location(self, video_id: int) -> str:
        raise NotImplementedError

    def get_audio_location(self, audio_id: int) -> str:
        raise NotImplementedError

    def add_entry(
        self,
        job_config: jc.EndToEndConfig,
        video_path: str,
        audio_path: str,
        transcript: pd.DataFrame,
        gps_data: pd.DataFrame,
    ) -> None:
        """Adds an entry to the repository.

        Args:
            job_config (jc.EndToEndConfig): Job configuration.
            video_path (str): Path to the video file.
            audio_path (str): Path to the audio file.
            transcript (pd.DataFrame): Transcript data with columns: "word", "start", "end", "probability".
            gps_data (pd.DataFrame): GPS data with columns: "relative_time", "utc_time", "latitude", "longitude", "altitude_m", "speed_kmh".
        """
        raise NotImplementedError
