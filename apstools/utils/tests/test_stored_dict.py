"""
Test the utils.stored_dict module.
"""

import pathlib
import sys
import tempfile
import time
import uuid
from contextlib import nullcontext as does_not_raise

import pytest
import yaml

from .. import StoredDict

STOREDDICT_SYNC_LOOP_PERIOD = 0.005
LUFTPAUSE_DELAY = 4 * STOREDDICT_SYNC_LOOP_PERIOD


def file_splitlines(filename) -> list:
    """Cautious file handling (as needed for Windows)."""
    with open(filename) as f:
        buffer = f.read().splitlines()
    return buffer


def load_config_yaml(path) -> dict:
    """Load YAMLfile."""
    iconfig = yaml.load(open(path).read(), yaml.Loader)
    return iconfig


def luftpause(delay=LUFTPAUSE_DELAY):
    """A brief wait for content to flush to storage."""
    time.sleep(max(0, delay))


@pytest.fixture
def md_file():
    """Provide a temporary file (deleted on close)."""
    with tempfile.NamedTemporaryFile(
        prefix=".re_md_",
        suffix=".yml",
        delete=False,
    ) as tfile:
        path = pathlib.Path(tfile.name)
        assert path.exists(), f"temporary file: {path}"
        yield path
        tfile.close()
        path.unlink()


def test_StoredDict(md_file):
    """Test the StoredDict class."""
    assert md_file.exists()
    assert len(file_splitlines(md_file)) == 0  # empty

    sdict = StoredDict(md_file, delay=LUFTPAUSE_DELAY, title="unit testing")
    assert sdict is not None
    assert len(sdict) == 0
    assert sdict._delay == LUFTPAUSE_DELAY
    assert sdict._title == "unit testing"
    assert len(file_splitlines(md_file)) == 0  # still empty
    assert sdict._sync_key == f"sync_agent_{id(sdict):x}"
    assert not sdict.sync_in_progress

    # Write an empty dictionary.
    sdict.flush()
    luftpause()
    buf = file_splitlines(md_file)
    assert len(buf) == 4, f"{buf=}"
    assert buf[-1] == "{}"  # The empty dict.
    assert buf[0].startswith("# ")
    assert buf[1].startswith("# ")
    assert "unit testing" in buf[0]

    # Add a new {key: value} pair.
    assert not sdict.sync_in_progress
    sdict["a"] = 1
    assert sdict.sync_in_progress
    sdict.flush()
    assert time.time() >= sdict._sync_deadline
    luftpause()
    assert not sdict.sync_in_progress
    assert len(file_splitlines(md_file)) == 4

    # Change the only value.
    sdict["a"] = 2
    sdict.flush()
    luftpause()
    assert len(file_splitlines(md_file)) == 4  # Still.

    # Add another key.
    sdict["bee"] = "bumble"
    sdict.flush()
    luftpause()
    assert len(file_splitlines(md_file)) == 5

    # Test _delayed_sync_to_storage.
    sdict["bee"] = "queen"
    md = load_config_yaml(md_file)
    assert len(md) == 2  # a & bee
    assert "a" in md
    assert md["bee"] == "bumble"  # The old value.

    time.sleep(sdict._delay / 2)
    # Still not written ...
    assert load_config_yaml(md_file)["bee"] == "bumble"

    time.sleep(sdict._delay)
    # Should be written by now.
    assert load_config_yaml(md_file)["bee"] == "queen"

    del sdict["bee"]  # __delitem__
    assert "bee" not in sdict  # __getitem__


def test_atexit(md_file):
    """Verify the file is written on program exit."""
    assert len(file_splitlines(md_file)) == 0

    key = str(uuid.uuid4())

    with pytest.raises(SystemExit) as context:
        assert len(file_splitlines(md_file)) == 0  # empty
        d = StoredDict(md_file, delay=LUFTPAUSE_DELAY)
        d.update({"a": 1, "uuid": key})
        assert len(file_splitlines(md_file)) == 0
        sys.exit(0)

    assert context.type is SystemExit

    luftpause(0.2)
    assert md_file.exists()
    lines = file_splitlines(md_file)
    assert len(lines) == 5
    assert lines[-1] == f"uuid: {key}"


def test_delitem(md_file):
    """__delitem__"""
    assert len(file_splitlines(md_file)) == 0  # empty
    d = StoredDict(md_file, delay=LUFTPAUSE_DELAY)
    assert len(file_splitlines(md_file)) == 0

    d[0] = 1
    d.flush()
    luftpause()
    lines = file_splitlines(md_file)
    assert len(lines) == 4
    assert lines[-1] == "0: 1"

    del d[0]
    d.flush()
    luftpause()
    lines = file_splitlines(md_file)
    assert len(lines) == 4
    assert lines[-1] == "{}"


def test_popitem(md_file):
    assert len(file_splitlines(md_file)) == 0  # empty
    d = StoredDict(md_file, delay=LUFTPAUSE_DELAY)
    assert len(file_splitlines(md_file)) == 0

    d.update({"a": 1, "b": "two"})
    d.flush()
    luftpause()
    lines = file_splitlines(md_file)
    assert len(lines) == 5
    assert lines[-1] == "b: two"

    assert d.pop("b") == "two"
    d.flush()
    luftpause()
    lines = file_splitlines(md_file)
    assert len(lines) == 4
    assert lines[-1] == "a: 1"


def test_popitem_empty_dict(md_file):
    """Can't popitem from empty dict."""
    sdict = StoredDict(md_file, delay=0.2, title="unit testing")
    with pytest.raises(KeyError) as reason:
        sdict.popitem()
    assert "dictionary is empty" in str(reason), f"{reason=}"


def test_repr(md_file):
    """__repr__"""
    sdict = StoredDict(md_file, delay=0.1, title="unit testing")
    sdict["a"] = 1
    assert repr(sdict) == "<StoredDict {'a': 1}>"
    assert str(sdict) == "<StoredDict {'a': 1}>"


@pytest.mark.parametrize(
    "md, xcept, text",
    [
        [{"a": 1}, None, str(None)],  # int value is ok
        [{"a": 2.2}, None, str(None)],  # float value is ok
        [{"a": "3"}, None, str(None)],  # str value is ok
        [{"a": [4, 5, 6]}, None, str(None)],  # list value is ok
        [{"a": {"bb": [4, 5, 6]}}, None, str(None)],  # nested value is ok
        [{1: 1}, None, str(None)],  # int key is ok
        [{"a": object()}, TypeError, "not JSON serializable"],
        [{object(): 1}, TypeError, "keys must be str, int, float, "],
        [{"a": [4, object(), 6]}, TypeError, "not JSON serializable"],
        [{"a": {object(): [4, 5, 6]}}, TypeError, "keys must be str, int, "],
    ],
)
def test_set_exceptions(md, xcept, text, md_file):
    """Cases that might raise an exception."""
    sdict = StoredDict(md_file, delay=0.2, title="unit testing")
    context = does_not_raise() if xcept is None else pytest.raises(xcept)
    with context as reason:
        sdict.update(md)
        sdict.flush()
    assert text in str(reason), f"{reason=}"
