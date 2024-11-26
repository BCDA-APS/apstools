"""Test the utils.statistics module."""

import pathlib

import h5py
import pytest

from ..statistics import array_statistics

DATA_PATH = pathlib.Path(__file__).parent / "data"


def get_x_y_data(path):
    """
    Read ordered pairs from file.

    The header of the file (in comments) can contain key=value comments which
    represent keys in the result from 'array_statistics()'.  Each such key found
    will be tested.

    EXAMPLE::

        #    min_x = 1.0
        #    max_x = 11.0
        #    min_y = 0.0
        #    max_y = 50.0
        #    n = 11
        #    x_at_max_y = 7.0
        #    centroid = 7.5
        #    fwhm = 1.1774100225154747
        #    sigma = 0.5
        #    variance = 0.25

    """
    buf = open(path).read()
    advice, comments, data = {}, [], []
    for line in buf.strip().splitlines():
        if line.strip().startswith("#"):
            comments.append(line)
            if "=" in line:
                key, value = line.strip().lstrip("#").split("=")
                advice[key.strip()] = value.strip()
        elif line.strip() == "":
            continue
        else:
            data += list(map(float, line.split()))

    return {
        "advice": advice,
        "comments": comments,
        "file": path.name,
        "x": data[0::2],
        "y": data[1::2],
    }


def ok_sample_data():
    for fname in DATA_PATH.glob("ok_x_y_*.txt"):
        if fname.is_file():
            data = get_x_y_data(fname)
            if data is not None:
                yield data


@pytest.mark.parametrize("data", ok_sample_data())
def test_array_statistics(data):
    assert DATA_PATH.exists()
    assert data is not None
    assert isinstance(data, dict)

    stats = array_statistics(data["x"], data["y"])
    assert stats is not None
    unknown = object()
    for key, expected in data["advice"].items():
        received = stats.get(key, unknown)
        assert f"{received}" == expected, f"{key=} {expected=} {stats=} {data['file']=!r}"
