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

"""This module contains functions for processing audio data."""

import dataclasses as dc
import itertools
import logging
import os
import string
from typing import Any

import pandas as pd

import job_config as jc


def transcribe_audio_whisper(
    audio_file_path: str,
    whisper_config: jc.WhisperConfig,
    logger: logging.Logger = logging.getLogger(__name__),
) -> list[dict[str, Any]]:
    """Transcribes audio using Whisper.

    Args:
        audio_file_path (str): Path to the audio file.
        whisper_config (WhisperConfig): Whisper configuration.
        logger (logging.Logger, optional): Logger object. Defaults to logging.getLogger(__name__).

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: Transcription data with columns: "word", "start", "end", "probability".

    Raises:
        ImportError: If `whisper` is not installed.
        FileNotFoundError: If `audio_file_path` does not exist.
    """
    logger.info(f"Transcribing audio using Whisper {whisper_config}")

    try:
        import whisper
    except ImportError:
        msg = "whisper not installed. Please install it using `pip install -U openai-whisper`"
        logger.error(msg)
        raise ImportError(msg)

    if not os.path.exists(audio_file_path):
        msg = f"File not found at {audio_file_path}"
        logger.error(msg)
        raise FileNotFoundError(msg)

    model = whisper.load_model(
        whisper_config.model_name,
        download_root=whisper_config.download_location,
    )

    # `transcribe` returns a dict with the following keys:
    # - "text": str
    # - "language": str
    # - "segments": list[dict]
    # We only the "segments" which is list of dictionaries with the following keys:
    # - "id": int
    # - "seek": float
    # - "start": float
    # - "end": float
    # - "text": str
    # - "tokens": list[int]
    # - "temperature": float
    # - "avg_logprob": float
    # - "compression_ratio": float
    # - "no_speech_prob": float
    # - "words": list[dict]
    # We need the words and their timestamps/scores which are in "words" and have the following keys:
    # - "word": str
    # - "start": float
    # - "end": float
    # - "probability": float
    transcription: dict[str, Any] = model.transcribe(
        audio_file_path, word_timestamps=True, **whisper_config.transcribe_kwargs
    )
    
    
    keep_keys = ["start", "end", "text", "no_speech_prob"]
    text_segments = list(map(
        lambda segment: dict(list(filter(lambda item: item[0] in keep_keys, segment.items()))),
        transcription["segments"],
    ))
    
    # Some of the words have whitespace at the beginning and end. Strip it.
    # Also remove punctuation except for apstrohpes.
    keep_punc = "'"
    remove_punc = string.punctuation.replace(keep_punc, "")
    remove_punc_table = str.maketrans("", "", remove_punc + string.whitespace)
    
    text_segments = []
    for segment in transcription["segments"]:
        filtered_segment = dict(list(filter(
            lambda item: item[0] in keep_keys, 
            segment.items()
        )))
        filtered_segment["words"] =  list(map(
            lambda d: {
                k: v.translate(remove_punc_table) if k == "word" else v
                for k, v in d.items()
            },
            segment["words"],
        ))
        text_segments.append(filtered_segment)
    
    

    # TODO: add some length checks here
#     words = list(
#         itertools.chain.from_iterable(
#             list(map(lambda v: v["words"], transcription["segments"]))
#         )
#     )

#     # Some of the words have whitespace at the beginning and end. Strip it.
#     # Also remove punctuation except for apstrohpes.
#     keep_punc = "'"
#     remove_punc = string.punctuation.replace(keep_punc, "")
#     remove_punc_table = str.maketrans("", "", remove_punc + string.whitespace)
#     words_stripped = list(
#         map(
#             lambda d: {
#                 k: v.translate(remove_punc_table) if k == "word" else v
#                 for k, v in d.items()
#             },
#             words,
#         )
#     )

    return text_segments


def transcribe_audio(
    audio_file_path: str,
    model_config: jc.WhisperConfig,
    logger: logging.Logger = logging.getLogger(__name__),
) -> pd.DataFrame:
    if type(model_config) == jc.WhisperConfig:
        return transcribe_audio_whisper(audio_file_path, model_config, logger=logger)
    else:
        raise ValueError(f"Invalid model config {model_config}")


if __name__ == "__main__":
    print(
        transcribe_audio_whisper(
            "sample_data/audio.mp3",
            jc.WhisperConfig(
                model_name="tiny.en",
                download_location=".",
            ),
        )
    )
