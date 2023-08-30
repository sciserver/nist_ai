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

"""This module contains helper functions and classes."""

import hashlib
import logging
import os

# https://stackoverflow.com/a/39215961/2691018
class StreamToLogger:
    """This class redirects write calss to a logger."""

    def __init__(self, logger: logging.Logger, level: int | str) -> "StreamToLogger":
        self.logger = logger
        self.level = level
        self.linebuf = ""

    def write(self, buf: str) -> None:
        for line in buf.rstrip().splitlines():
            self.logger.log(self.level, line.rstrip())

    def flush(self) -> None:
        pass


import sys

# https://stackoverflow.com/a/54955536
from contextlib import contextmanager


@contextmanager
def stdout_redirector(stdout: StreamToLogger, stderr: StreamToLogger):
    """This function redirects stdout and stderr to a logger using"""

    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = stdout
    sys.stderr = stderr
    try:
        yield
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


def get_checksum(
    file_name: str,
    logger: logging.Logger = logging.getLogger(__name__),
) -> str:
    """Returns the checksum of a file.

    Args:
        file_name (str): Path to the file.
        logger (logging.Logger, optional): Logger object. Defaults to logging.getLogger(__name__).

    Returns:
        str: Checksum of the file.

    Raises:
        FileNotFoundError: If `file_name` does not exist.
    """

    if not os.path.exists(file_name):
        msg = f"File not found at {file_name}"
        logger.error(msg)
        raise FileNotFoundError(msg)

    with open(file_name, "rb") as file_to_check:
        data = file_to_check.read()
        return hashlib.md5(data).hexdigest()
