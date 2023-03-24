import logging
import pathlib
import tempfile

import pytest

from .. import file_log_handler
from .. import get_log_path
from .. import setup_IPython_console_logging
from .. import stream_log_handler


@pytest.fixture(scope="function")
def tempdir():
    tempdir = tempfile.mkdtemp()
    return tempdir


def test_get_log_path(tempdir):
    pathlib.os.chdir(tempdir)
    path = pathlib.Path() / ".logs"
    assert not path.exists()

    log_path = get_log_path()
    assert log_path.exists()


@pytest.mark.parametrize(
    "maxBytes, backupCount, log_path, level",
    [
        [0, 0, None, None],  # defaults
        [1_000_000, 9, None, None],  # training repo uses this
        [0, 9, None, None],
        [1_000_000, 0, None, None],
        [1_000_000, 0, None, "DEBUG"],
        [0, 0, "/tmp", None],
    ],
)
def test_file_log_handler(maxBytes, backupCount, log_path, level, tempdir):
    pathlib.os.chdir(tempdir)
    log_path = pathlib.Path(log_path or get_log_path())
    assert log_path.exists()

    handler = file_log_handler(
        "my_log_file",
        maxBytes=maxBytes,
        backupCount=backupCount,
        log_path=log_path,
        level=level,
    )
    assert isinstance(handler, logging.Handler)

    logfile = log_path / "my_log_file.log"
    assert logfile.exists()


@pytest.mark.parametrize(
    "formatter, level",
    [
        [None, "INFO"],  # defaults
        [None, "DEBUG"],
    ],
)
def test_stream_log_handler(formatter, level):
    handler = stream_log_handler(formatter=formatter, level=level)
    assert isinstance(handler, logging.Handler)
    # TODO: more tests


@pytest.mark.parametrize(
    "logger, filename, log_path",
    [
        [None, "ipython_console.log", None],  # defaults
        [None, "ipython_console.log", "/tmp"],
    ],
)
def test_setup_IPython_console_logging(logger, filename, log_path, tempdir):
    pathlib.os.chdir(tempdir)
    setup_IPython_console_logging(logger=logger, filename=filename, log_path=log_path)

    log_path = get_log_path()
    assert log_path.exists()

    # unit tests do not run IPython so no logfile exists.
    logfile = log_path / "ipython_console.log"
    assert not logfile.exists()
