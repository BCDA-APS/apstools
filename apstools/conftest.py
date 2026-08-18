"""
Session-scoped pytest fixtures providing test data catalogs.

Catalogs are loaded from compressed JSON snapshots in apstools/tests/ using
``databroker.temp().v2``, avoiding the fragile ``databroker-unpack`` /
msgpack / intake YAML approach.  See issue #1131.
"""

import gzip
import json
import pathlib

import databroker
import pytest

TEST_DATA = pathlib.Path(__file__).parent / "tests"


def _load_catalog(path: pathlib.Path):
    """Load a catalog from a gzipped JSON snapshot into a temp databroker."""
    with gzip.open(path, "rt", encoding="utf-8") as f:
        data = json.load(f)
    cat = databroker.temp().v2
    for entry in data:
        cat.v1.insert(*entry)

    # Flush any incomplete runs (such as no stop document) to storage.
    # RunRouter leaves their suitcase serializers open; close them so
    # their msgpack files are written before the catalog globs them.
    serializer = cat.v1._serializer  # event_model.RunRouter
    for callbacks in serializer._factory_cbs_by_start.values():
        for cb in callbacks:
            cb.close()
    cat.force_reload()

    return cat


@pytest.fixture(scope="session")
def apstools_cat():
    """Catalog loaded from apstools.json.gz (53 runs)."""
    return _load_catalog(TEST_DATA / "apstools.json.gz")


@pytest.fixture(scope="session")
def usaxs_cat():
    """Catalog loaded from usaxs.json.gz (10 runs)."""
    return _load_catalog(TEST_DATA / "usaxs.json.gz")
