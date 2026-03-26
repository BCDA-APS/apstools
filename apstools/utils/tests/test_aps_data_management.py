"""
Test the APS Data Management utility functions.
"""

import pathlib
import tempfile
import uuid
from contextlib import nullcontext as does_not_raise
from unittest import mock

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


RUN_UID = str(uuid.uuid4())


def make_mock_run(metadata):
    """Build a minimal mock run object that resembles a bluesky run."""
    mock_run = mock.MagicMock()
    mock_run.metadata = metadata
    mock_run.__iter__ = mock.Mock(return_value=iter([]))
    return mock_run


def make_mock_api(captured):
    """Build a mock DM dataset catalog API that records the dataset info."""

    def fake_add_experiment_dataset(info):
        captured.update(info)
        return info

    mock_api = mock.MagicMock()
    mock_api.addExperimentDataset.side_effect = fake_add_experiment_dataset
    return mock_api


_VALID_METADATA = {"start": {"uid": RUN_UID, "time": 0}}
_NO_START_METADATA = {}
_NO_UID_METADATA = {"start": {"time": 0}}


@pytest.mark.parametrize(
    "metadata, assertions, context",
    [
        pytest.param(
            _VALID_METADATA,
            {"bluesky_run_uid": RUN_UID},
            does_not_raise(),
            id="bluesky_run_uid contains the full uid",
        ),
        pytest.param(
            _VALID_METADATA,
            {"datasetName": f"run_uid8_{RUN_UID[:8]}"},
            does_not_raise(),
            id="datasetName retains the 8-character prefix",
        ),
        pytest.param(
            _NO_START_METADATA,
            {},
            pytest.raises(KeyError, match="'start'"),
            id="run metadata missing 'start' key raises KeyError",
        ),
        pytest.param(
            _NO_UID_METADATA,
            {},
            pytest.raises(KeyError, match="'uid'"),
            id="run metadata missing 'uid' key raises KeyError",
        ),
    ],
)
def test_share_bluesky_metadata_with_dm(metadata, assertions, context):
    """
    share_bluesky_metadata_with_dm() must include the full bluesky run uid.

    The ``bluesky_run_uid`` key in the dataset info must contain the complete
    uid string, not just a truncated version.  This is required so that a
    tiled server can filter by authenticated access using DM.  See issue #1150.
    """
    captured = {}
    mock_run = make_mock_run(metadata)
    mock_api = make_mock_api(captured)

    with context:
        with (
            mock.patch("apstools.utils.aps_data_management.dm_api_dataset_cat", return_value=mock_api),
            mock.patch.dict("sys.modules", {"dm": mock.MagicMock()}),
        ):
            adm.share_bluesky_metadata_with_dm("test_experiment", "test_workflow", mock_run)

        for key, expected in assertions.items():
            assert captured[key] == expected
