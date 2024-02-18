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
from logging import DEBUG
from logging import FileHandler
from logging import Formatter
from logging import StreamHandler
from logging.handlers import RotatingFileHandler


def file_log_handler(
    file_name_base,
    maxBytes=0,
    backupCount=0,
    log_path=None,
    level=None,
):
    """
    Record logging output to a file.

    PARAMETERS

    file_name_base : *str*
        Part of the name to store the log file. Full name is
        ``f"<log_path>/{file_name_base}.log"`` in present working directory.
    log_path : *str*
        Part of the name to store the log file. Full name is
        ``f"<log_path>/{file_name_base}.log"`` in present working directory.
        default: (the present working directory)/LOG_DIR_BASE
    level : *int*
        Threshold for reporting messages with this logger. Logging messages
        which are less severe than ``level`` will be ignored.
        default: 10 (``logging.DEBUG`` or ``DEBUG``)
        see: https://docs.python.org/3/library/logging.html#levels
    maxBytes : (optional) *int*
        Log file *rollover* begins whenever the current log file is nearly
        *maxBytes* in length.  A new file is written when the current line will
        push the current file beyond this limit.
        default: 0
    backupCount : (optional) *int*
        When *backupCount* is non-zero, the system will keep up to *backupCount*
        numbered log files (with added extensions `.1`, '.2`, ...).  The current
        log file always has no numbered extension.  The previous log file is the
        one with the lowest extension number.
        default: 0

    .. note::  When either ``maxBytes`` or ``backupCount`` are zero,
        log file rollover never occurs, so you generally want to set
        ``backupCount`` to at least 1, and have a non-zero ``maxBytes``.
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


def get_log_path():
    """
    Return a path to `./.logs`. Create directory if it does not exist.
    """
    path = pathlib.Path().cwd() / ".logs"
    if not path.exists():
        path.mkdir()
    return path


def setup_IPython_console_logging(logger=None, filename="ipython_console.log", log_path=None):
    """
    Record all input (``In``) and output (``Out``) from IPython console.

    PARAMETERS

    logger
        *object*:
        Instance of ``logging.Logger``.
    filename
        *str*:
        Name of the log file.
        (default: ``ipython_console.log``)
    log_path : *str*
        Directory to store the log file. Full name is
        ``f"<log_path>/{file_name_base}.log"``.
        default: (the present working directory)/LOG_DIR_BASE
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


def stream_log_handler(formatter=None, level="INFO"):
    """
    Record logging output to a stream (such as the console).

    PARAMETERS

    formatter
        *object*:
        Instance of ``logging.Formatter``.
    level
        *str*:
        Name of the logging level to report.
        (default: ``INFO``)
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
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2024, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
