"""
Support for logging
+++++++++++++++++++++++++++++++++++++++

There is a guide describing :ref:`howto_session_logs`.

.. autosummary::

   ~file_log_handler
   ~get_log_path
   ~setup_IPython_console_logging
   ~stream_log_handler
"""

import pathlib
from logging import DEBUG, FileHandler, Formatter, Logger, StreamHandler
from logging.handlers import RotatingFileHandler
from typing import Optional, Union


def file_log_handler(
    file_name_base: str,
    maxBytes: int = 0,
    backupCount: int = 0,
    log_path: Optional[Union[str, pathlib.Path]] = None,
    level: Optional[int] = None,
) -> Union[FileHandler, RotatingFileHandler]:
    """
    Record logging output to a file.

    Parameters
    ----------
    file_name_base : str
        Part of the name to store the log file. Full name is
        ``f"<log_path>/{file_name_base}.log"`` in present working directory.
    maxBytes : int, optional
        Log file rollover begins whenever the current log file is nearly
        maxBytes in length. A new file is written when the current line will
        push the current file beyond this limit.
        Default: 0
    backupCount : int, optional
        When backupCount is non-zero, the system will keep up to backupCount
        numbered log files (with added extensions `.1`, '.2', ...). The current
        log file always has no numbered extension. The previous log file is the
        one with the lowest extension number.
        Default: 0
    log_path : Optional[Union[str, pathlib.Path]], optional
        Part of the name to store the log file. Full name is
        ``f"<log_path>/{file_name_base}.log"`` in present working directory.
        Default: (the present working directory)/LOG_DIR_BASE
    level : Optional[int], optional
        Threshold for reporting messages with this logger. Logging messages
        which are less severe than level will be ignored.
        Default: 10 (logging.DEBUG or DEBUG)
        See: https://docs.python.org/3/library/logging.html#levels

    Returns
    -------
    Union[FileHandler, RotatingFileHandler]
        Configured file handler for logging.

    Notes
    -----
    When either maxBytes or backupCount are zero, log file rollover never occurs,
    so you generally want to set backupCount to at least 1, and have a non-zero maxBytes.
    """
    log_path = log_path or get_log_path()
    log_file = log_path / f"{file_name_base}.log"
    level = level or DEBUG

    if maxBytes > 0 or backupCount > 0:
        handler = RotatingFileHandler(log_file, maxBytes=maxBytes, backupCount=backupCount)
    else:
        handler = FileHandler(log_file)

    handler.setLevel(level)

    formatter = Formatter(
        (
            "|%(asctime)s"
            "|%(levelname)s"
            "|%(process)d"
            "|%(name)s"
            "|%(module)s"
            "|%(lineno)d"
            "|%(threadName)s"
            "| - "
            "%(message)s"
        )
    )
    formatter.default_msec_format = "%s.%03d"
    handler.setFormatter(formatter)

    return handler


def get_log_path() -> pathlib.Path:
    """
    Return a path to `./.logs`. Create directory if it does not exist.

    Returns
    -------
    pathlib.Path
        Path to the logs directory.
    """
    path = pathlib.Path().cwd() / ".logs"
    if not path.exists():
        path.mkdir()
    return path


def setup_IPython_console_logging(
    logger: Optional[Logger] = None,
    filename: str = "ipython_console.log",
    log_path: Optional[Union[str, pathlib.Path]] = None,
) -> None:
    """
    Record all input (In) and output (Out) from IPython console.

    Parameters
    ----------
    logger : Optional[Logger], optional
        Instance of logging.Logger.
        Default: None
    filename : str, optional
        Name of the log file.
        Default: "ipython_console.log"
    log_path : Optional[Union[str, pathlib.Path]], optional
        Directory to store the log file. Full name is
        ``f"<log_path>/{file_name_base}.log"``.
        Default: (the present working directory)/LOG_DIR_BASE
    """
    try:
        from IPython import get_ipython

        # start logging console to file
        # https://ipython.org/ipython-doc/3/interactive/magics.html#magic-logstart
        _ipython = get_ipython()
        log_path = pathlib.Path(log_path or get_log_path())
        io_file = log_path / filename
        if _ipython is not None:
            _ipython.magic(f"logstart -o -t {io_file} rotate")
        if logger is not None:
            logger.info("Console logging: %s", io_file)
    except Exception as exc:
        if logger is not None:
            logger.exception("Could not setup console logging.")
        else:
            print(f"Could not setup console logging: {exc}")


def stream_log_handler(
    formatter: Optional[Formatter] = None,
    level: str = "INFO",
) -> StreamHandler:
    """
    Record logging output to a stream (such as the console).

    Parameters
    ----------
    formatter : Optional[Formatter], optional
        Instance of logging.Formatter.
        Default: None
    level : str, optional
        Name of the logging level to report.
        Default: "INFO"

    Returns
    -------
    StreamHandler
        Configured stream handler for logging.
    """
    handler = StreamHandler()

    # nice output format
    # https://docs.python.org/3/library/logging.html#logrecord-attributes
    if formatter is None:
        # fmt: off
        formatter = Formatter(
            (
                "%(levelname)-.1s"		# only first letter
                " %(asctime)s"
                " - "
                "%(message)s"
            ),
            datefmt="%a-%H:%M:%S"
        )
        # fmt: on
        formatter.default_msec_format = "%s.%03d"
    handler.setFormatter(formatter)
    handler.setLevel(level)

    return handler


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
