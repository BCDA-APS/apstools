"""
test issue #440: specwriter
"""

from apstools.filewriters import SpecWriterCallback
from apstools.filewriters import _rebuild_scan_command
import intake

# import pytest
import numpy as np

# import numpy.testing
import os
import zipfile


DATA_ARCHIVE = "440_specwriter_problem_run.zip"

PATH = os.path.dirname(__file__)
FULL_ZIP_FILE = os.path.join(PATH, DATA_ARCHIVE)

TMP_CATALOG = os.path.join(
    "/tmp", DATA_ARCHIVE.split(".")[0], "catalog.yml"
)


def test_setup_comes_first():
    assert os.path.exists(FULL_ZIP_FILE)

    with zipfile.ZipFile(FULL_ZIP_FILE, "r") as zip_ref:
        zip_ref.extractall("/tmp")

    assert os.path.exists(TMP_CATALOG)


def test_confirm_run_exists():
    assert os.path.exists(TMP_CATALOG)

    cat = intake.open_catalog(TMP_CATALOG)
    assert "packed_catalog" in cat

    cat = cat["packed_catalog"]
    assert len(cat) == 1
    assert "624e776a-a914-4a74-8841-babf1591fb29" in cat


def test_specwriter():
    # The problem does not appear when using data from the databroker.
    # Verify that is the case now.
    os.chdir("/tmp")
    specfile = "issue240.spec"
    if os.path.exists(specfile):
        os.remove(specfile)
    specwriter = SpecWriterCallback()
    specwriter.newfile(specfile)
    db = intake.open_catalog(TMP_CATALOG)["packed_catalog"].v1
    h = db[-1]
    for key, doc in db.get_documents(h):
        specwriter.receiver(key, doc)
        assert "relative_energy" not in doc
    assert os.path.exists(specwriter.spec_filename)

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
