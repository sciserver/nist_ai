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

import contextlib
import hashlib
import logging
import os
import sys
import time
from typing import Union


# https://stackoverflow.com/a/39215961/2691018
class StreamToLogger:
    """This class redirects write class to a logger."""

    def __init__(
        self, logger: logging.Logger, level: Union[int, str]
    ) -> "StreamToLogger":
        """This class redirects write class to a logger.

        Args:
            logger (logging.Logger): The logger instance to use for logging
            level (Union[int, str]): The logging level to use

        Returns:
            StreamToLogger: The StreamToLogger instance
        """
        self.logger = logger
        self.level = level
        self.linebuf = ""

    def write(self, buf: str) -> None:
        """Writes to the logger.

        Args:
            buf (str): The string to write to the logger

        Returns:
            None
        """
        for line in buf.rstrip().splitlines():
            self.logger.log(self.level, line.rstrip())

    def flush(self) -> None:
        """Flushes the logger.

        Returns:
            None
        """
        pass


# https://stackoverflow.com/a/54955536
@contextlib.contextmanager
def stdout_redirector(stdout: StreamToLogger, stderr: StreamToLogger):
    """This function redirects stdout and stderr to a logger using."""
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = stdout
    sys.stderr = stderr
    try:
        yield
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


class LogTime:
    """A context manager class for logging code timings and errors.

    This class will log the time it takes to run some code along with any
    exceptions that occur within in the context. Timings are logged at the INFO
    level and errors are logged at the FATAL level.

    Example:
    >>> import logging
    >>> logger = logging.getLogger("example")
    >>>
    >>> with LogTime(logger, "Calculating Sum"):
    >>>     a = 2 + 2

    The log file will look something like (depending on your formatting):
    >>> Starting Calculating Sum
    >>> Completed in 7.62939453125e-06 seconds
    """

    def __init__(self, logger: logging.Logger, task_str: str):
        """A context manager class for logging code timings and errors.

        Args:
            logger (logging.Logger): The logger instance to use for logging
            task_str (str): The string describing the section of code being run

        """
        self.logger = logger
        self.task_str = task_str

    def __enter__(self):
        """Logs the start of the task."""
        self.logger.info(f"Starting {self.task_str}")
        self.start = time.time()

    def __exit__(self, exc_type, exc_value, traceback):
        """Logs the end of the task and any exceptions that occurred."""
        if exc_type is None:
            self.logger.info(f"Completed in {time.time() - self.start} seconds")
        else:
            self.logger.fatal(f"{exc_type}\n{exc_value}\n{traceback}")


def get_checksum(
    file_name: str,
    logger: logging.Logger = logging.getLogger(__name__),
) -> str:
    """Returns the checksum of a file.

    Args:
        file_name (str): Path to the file.
        logger (logging.Logger, optional): Logger object.

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
