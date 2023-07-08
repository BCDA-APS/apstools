import pytest
import pathlib

from .. import dm_setup


def test_util():
    test_bash_file = pathlib.Path(__file__)
    with pytest.raises(KeyError) as exc:
        dm_setup(test_bash_file)
    assert "DM_STATION_NAME" in str(exc.value)
