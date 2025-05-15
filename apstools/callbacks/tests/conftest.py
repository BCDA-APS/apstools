import pathlib
import tempfile

import pytest


@pytest.fixture()
def tempdir():
    """Temporary directory for testing."""
    tempdir = tempfile.mkdtemp()
    path = pathlib.Path(tempdir)
    yield path

    # empty tempdir, then delete it
    for f in path.iterdir():
        if f.is_file():
            f.unlink()
    path.rmdir()
