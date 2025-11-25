"""
Test the APS Data Management utility functions.
"""

import pathlib
import tempfile
import uuid
from contextlib import nullcontext as does_not_raise

import pytest

from .. import aps_data_management as adm
from .. import dm_setup
from .. import dm_source_environ


@pytest.fixture()
def tmpfile():
    tempdir = pathlib.Path(tempfile.mkdtemp())
    yield tempdir / f"file_{str(uuid.uuid4())[:7]}"


def make_bash_file(contents):
    # TODO: remove tempdir after test
    tempdir = pathlib.Path(tempfile.mkdtemp())
    filename = tempdir / f"file_{str(uuid.uuid4())[:7]}"
    with open(filename, "w") as f:
        f.write(contents)
    return str(filename)


@pytest.mark.parametrize(
    "filename, fail, context",
    [
        pytest.param(
            "/does/not/exist",
            False,
            does_not_raise(),
            id="non-existing file name, fail=False",
        ),
        pytest.param(
            "/no/such/file",
            True,
            pytest.raises(
                FileExistsError,
                match="filename='/no/such/file' does not exist.",
            ),
            id="non-existing file name, fail=True",
        ),
        pytest.param(
            __file__,  # This Python file does not have the env vars.
            False,
            pytest.raises(
                KeyError,
                match="No environment variable definitions found",
            ),
            id="file that has no 'export' statements",
        ),
        pytest.param(
            None,
            False,
            pytest.raises(
                ValueError,
                match="'None' not allowed for 'filename'.",
            ),
            id="filename is 'None'",
        ),
        pytest.param(
            make_bash_file("export EXAMPLE=example\n"),
            False,
            pytest.raises(KeyError, match="DM_STATION_NAME"),
            id="export EXAMPLE=example\n",
        ),
        pytest.param(
            make_bash_file("export DM_STATION_NAME=apstools_test\n"),
            False,
            does_not_raise(),
            id="minimum content required to pass",
        ),
    ],
)
def test_dm_setup_raises_new(filename, fail, context):
    with context:
        # reset, to be safe
        adm.DM_ENV_SOURCED = False
        assert not adm.DM_ENV_SOURCED

        dm_setup(filename, fail=fail)


@pytest.mark.parametrize(
    "filename, sourced, context",
    [
        pytest.param(
            "/no/such/file",
            False,
            pytest.raises(ValueError, match="file is undefined"),
            id="file still does not exist",
        ),
        pytest.param(
            make_bash_file("export DM_STATION_NAME=apstools_test\n"),
            True,
            does_not_raise(),
            id="minimum required content",
        ),
    ],
)
def test_dm_source_environ_raises(filename, sourced, context):
    with context:
        # reset, to be safe
        adm.DM_ENV_SOURCED = False
        assert not adm.DM_ENV_SOURCED

        dm_setup(filename, fail=False)
        dm_source_environ()

    assert adm.DM_ENV_SOURCED == sourced
