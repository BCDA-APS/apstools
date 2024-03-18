"""
Test the APS Data Management utility functions.
"""

import pytest
import pathlib
import tempfile
import uuid

from .. import dm_setup
from .. import dm_source_environ
from .. import aps_data_management as adm


@pytest.fixture()
def tmpfile():
    tempdir = pathlib.Path(tempfile.mkdtemp())
    yield tempdir / f"file_{str(uuid.uuid4())[:7]}"


def test_dm_setup_raises(tmpfile):
    # reset, to be safe
    adm.DM_ENV_SOURCED = False
    assert not adm.DM_ENV_SOURCED

    # Test with a non-existing file name.
    # tmpfile does not exist yet since nothing was written to it.
    with pytest.raises(FileExistsError) as exinfo:
        dm_setup(tmpfile)
    assert "does not exist" in str(exinfo)
    assert adm.DM_SETUP_FILE is None
    assert not adm.DM_ENV_SOURCED

    # Test with a file that has no 'export' statements.  This Python file, for example.
    with pytest.raises(KeyError) as exinfo:
        dm_setup(__file__)
    assert "No environment variable definitions found" in str(exinfo)
    assert adm.DM_SETUP_FILE == str(pathlib.Path(__file__))
    assert not adm.DM_ENV_SOURCED

    bash_script = tmpfile
    with open(bash_script, "w") as f:
        f.write("export EXAMPLE=example\n")
    with pytest.raises(KeyError) as exinfo:
        dm_setup(bash_script)
    assert adm.DM_ENV_SOURCED
    assert adm.DM_SETUP_FILE == tmpfile
    assert adm.environ.get("EXAMPLE") == "example"
    assert "DM_STATION_NAME" in str(exinfo)

    # Finally, call with a setup that does not raise an exception.
    # Adds the minimum required (to pass) 'export' statement.
    value = "apstools_test"
    with open(bash_script, "a") as f:
        f.write(f"export DM_STATION_NAME={value}\n")
    adm.DM_ENV_SOURCED = False
    assert not adm.DM_ENV_SOURCED
    dm_setup(bash_script)
    assert adm.DM_ENV_SOURCED
    assert adm.DM_SETUP_FILE == tmpfile
    assert adm.environ.get("DM_STATION_NAME") == value


def test_dm_source_environ_raises(tmpfile):
    # reset, to be safe
    adm.DM_ENV_SOURCED = False
    assert not adm.DM_ENV_SOURCED

    # tmpfile does not exist yet since nothing was written to it.
    with pytest.raises(FileExistsError) as exinfo:
        dm_setup(tmpfile)
    with pytest.raises(ValueError) as exinfo:
        dm_source_environ()
    assert not adm.DM_ENV_SOURCED
    assert "file is undefined" in str(exinfo)
