"""
test issue #440: specwriter

# https://github.com/BCDA-APS/apstools/issues/440
"""

import pathlib
import tempfile
import zipfile

import intake
import numpy as np
import pytest

from .. import SpecWriterCallback
from ..spec_file_writer import _rebuild_scan_command

DATA_ARCHIVE = "440_specwriter_problem_run"
FULL_ZIP_FILE = pathlib.Path(__file__).parent / f"{DATA_ARCHIVE}.zip"


@pytest.fixture(scope="function")
def tempdir():
    tempdir = tempfile.mkdtemp()
    yield pathlib.Path(tempdir)


@pytest.fixture(scope="function")
def catalog():
    assert FULL_ZIP_FILE.exists()

    tempdir = pathlib.Path(tempfile.mkdtemp())
    assert tempdir.exists()

    with zipfile.ZipFile(FULL_ZIP_FILE, "r") as zip_ref:
        zip_ref.extractall(str(tempdir))

    catalog = tempdir / DATA_ARCHIVE / "catalog.yml"
    assert catalog.exists(), f"{catalog=}"

    yield catalog


def test_setup_comes_first(tempdir):
    assert tempdir.exists()
    assert FULL_ZIP_FILE.exists()

    with zipfile.ZipFile(FULL_ZIP_FILE, "r") as zip_ref:
        zip_ref.extractall(str(tempdir))

    catalog = tempdir / DATA_ARCHIVE / "catalog.yml"
    assert catalog.exists(), f"{catalog=}"


def test_confirm_run_exists(catalog):
    cat = intake.open_catalog(catalog)
    assert "packed_catalog" in cat

    cat = cat["packed_catalog"]
    assert len(cat) == 1
    assert "624e776a-a914-4a74-8841-babf1591fb29" in cat


def test_specwriter(tempdir, catalog):
    # https://github.com/BCDA-APS/apstools/issues/440
    # The problem does not appear when using data from the databroker.
    # Verify that is the case now.
    pathlib.os.chdir(tempdir)
    specfile = pathlib.Path("issue240.spec")
    if specfile.exists():
        specfile.unlink()  # remove existing file
    specwriter = SpecWriterCallback()
    specwriter.newfile(specfile)

    db = intake.open_catalog(catalog)["packed_catalog"].v1
    h = db[-1]
    for key, doc in db.get_documents(h):
        specwriter.receiver(key, doc)
        assert "relative_energy" not in doc
    assert specwriter.spec_filename.exists()

    with open(specwriter.spec_filename, "r") as f:
        line = ""
        while not line.startswith("#S 287"):
            line = f.readline()
        assert line.endswith("-0.05]})\n")

        # Next line should start with "#D "
        # The reported error had numbers from previous line (wrapped)
        line = f.readline()
        assert line.startswith("#D ")

    # The problem comes up if one of the arguments is a numpy.array.
    # So we must replay the document stream and modify the right
    # structure as it passes by.
    # This structure is in the start document, which is first.
    # Note: we don't have to write the whole SPEC file again,
    # just test if _rebuild_scan_command(start_doc) is one line.

    hh = db.get_documents(h)
    key, doc = next(hh)
    arr = doc["plan_args"]["qx_setup"]["relative_energy"]
    assert isinstance(arr, list)
    assert len(arr) == 183

    cmd = _rebuild_scan_command(doc)
    assert len(cmd.strip().splitlines()) == 1

    # Now, make it a numpy array and test again.
    arr = np.array(arr)
    assert isinstance(arr, np.ndarray)
    # modify the start doc
    doc["plan_args"]["qx_setup"]["relative_energy"] = arr
    cmd = _rebuild_scan_command(doc)  # FIXME: <-----
    assert len(cmd.strip().splitlines()) == 1
