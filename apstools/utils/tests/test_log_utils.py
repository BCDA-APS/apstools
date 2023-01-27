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


def test_file_log_handler(tempdir):
    pathlib.os.chdir(tempdir)
    handler = file_log_handler("my_log_file")
    assert isinstance(handler, logging.Handler)

    log_path = get_log_path()
    assert log_path.exists()

    logfile = log_path / "my_log_file.log"
    assert logfile.exists()

    # TODO: more tests


def test_stream_log_handler():
    handler = stream_log_handler()
    assert isinstance(handler, logging.Handler)
    # TODO: more tests


def test_setup_IPython_console_logging(tempdir):
    pathlib.os.chdir(tempdir)
    setup_IPython_console_logging()

    log_path = get_log_path()
    assert log_path.exists()

    # unit tests do not run IPython so no logfile exists.
    logfile = log_path / "ipython_console.log"
    assert not logfile.exists()
