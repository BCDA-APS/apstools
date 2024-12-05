"""Test the utils.mmap_dict module."""

import pytest

from ..mmap_dict import MMap


def test_MMap():
    """Test basic operations.  Comments indicate method tested."""
    mmap = MMap()
    assert mmap is not None  # __init__
    assert len(mmap) == 0  # __len__
    assert "_db" in dir(mmap)  # __dir__

    mmap.update(a=1, b=2)
    assert len(mmap) == 2  # __len__

    mmap.clear()
    assert len(mmap) == 0  # __len__

    mmap = MMap(a=1, b=2, c="three")
    assert len(mmap) == 3  # __len__
    assert "a" in mmap  # __dict__
    assert "a" in dir(mmap)  # __dir__
    assert "a" in list(mmap)  # __dict__
    assert hasattr(mmap, "a")  # __getattr__
    assert "MMap(a=1, b=2, c='three')" == repr(mmap)  # __repr__
    assert "MMap(a=1, b=2, c='three')" == str(mmap)  # __str__

    mmap.clear()
    assert len(mmap) == 0

    mmap = MMap(a=1, b=2)
    assert mmap["a"] == 1  # __getitem__
    assert mmap.get("a") == 1  # __getitem__
    assert mmap.get("a", "default") == 1  # __getitem__
    assert mmap.get("unknown", "default") == "default"  # __getitem__
    mmap["a"] = "three"  # __setitem__
    assert mmap.a == "three"  # __getattr__
    assert mmap["a"] == "three"  # __getitem__

    for key in mmap:  # __iter__
        assert key in mmap._db, f"{key=!r}: {mmap._db=!r}"  # __dict__

    # Some keys conflict with known attributes, such as method names.
    with pytest.raises(KeyError) as reason:
        mmap["pop"] = "weasel"  # __setitem__
    assert "key='pop' is a reserved name." in str(reason)

    # No write access to dictionary keys as attributes.
    with pytest.raises(AttributeError) as reason:
        mmap.some_new_attribute = "new key"
    assert "Unknown: attribute='some_new_attribute'" in str(reason)
