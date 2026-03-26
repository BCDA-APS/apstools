"""
Session-scoped pytest fixtures providing test data catalogs.

Catalogs are loaded from compressed JSON snapshots in resources/ using
``databroker.temp().v2``, avoiding the fragile ``databroker-unpack`` /
msgpack / intake YAML approach.  See issue #1131.
"""

import gzip
import json
import pathlib

import databroker
import pytest

RESOURCES = pathlib.Path(__file__).parent.parent / "resources"


def _load_catalog(path: pathlib.Path):
    """Load a catalog from a gzipped JSON snapshot into a temp databroker."""
    with gzip.open(path, "rt", encoding="utf-8") as f:
        data = json.load(f)
    cat = databroker.temp().v2
    for entry in data:
        cat.v1.insert(*entry)
    return cat


@pytest.fixture(scope="session")
def apstools_cat():
    """Session-scoped catalog loaded from apstools_test.json.gz (53 runs)."""
    return _load_catalog(RESOURCES / "apstools_test.json.gz")


@pytest.fixture(scope="session")
def usaxs_cat():
    """Session-scoped catalog loaded from usaxs_test.json.gz (10 runs)."""
    return _load_catalog(RESOURCES / "usaxs_test.json.gz")
