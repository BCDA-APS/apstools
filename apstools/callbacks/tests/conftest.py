import pathlib
import tempfile

import pytest


@pytest.fixture()
def tempdir() -> pathlib.Path:
    """Temporary directory for testing."""
    tempdir: str = tempfile.mkdtemp()
    path: pathlib.Path = pathlib.Path(tempdir)
    yield path

    # empty tempdir, then delete it
    for f in path.iterdir():
        if f.is_file():
            f.unlink()
    path.rmdir()
