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

import dataclasses as dc
import hashlib
import os
from enum import Enum
from typing import List, Optional, Union

VideoType = Enum("VideoType", ["GOPRO", "TRACK_ADDICT"])


@dc.dataclass
class WhisperConfig:
    model_name: str = "tiny.en"
    download_location: str = "."
    transcribe_kwargs: dict = dc.field(default_factory=dict)
    valid_model_names: List[str] = dc.field(
        init=False,
        default_factory=lambda: [
            "tiny",
            "tiny.en",
            "base",
            "base.en",
            "small",
            "small.en",
            "medium",
            "medium.en",
            "large",
        ],
    )

    def __post_init__(self):
        if not os.path.exists(self.download_location):
            os.makedirs(self.download_location, exist_ok=True)

        if self.model_name not in self.valid_model_names:
            msg = f"Invalid model name {self.model_name}. Valid model names are {self.valid_model_names}"
            raise ValueError(msg)


@dc.dataclass
class EndToEndConfig:
    transcription_config: Union[WhisperConfig, None]
    source_video_type: VideoType
    thumbnail_width: int = 300
