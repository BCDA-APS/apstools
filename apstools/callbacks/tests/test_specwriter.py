import pathlib
from contextlib import nullcontext as does_not_raise

import pytest
from bluesky import RunEngine
from bluesky import plans as bp
from ophyd import SoftPositioner

from ..callback_base import FileWriterCallbackBase
from ..spec_file_writer import SpecWriterCallback
from ..spec_file_writer import SpecWriterCallback2

DATA_ISSUE_1083 = """
#F spec.dat
#E 1746668725.1978145
#D Wed May 07 20:45:25 2025
#C Bluesky  user = prjemian  host = zap
#O0
#o0
#C Wed May 07 20:45:26 2025.  num_events_primary = 0
#C Wed May 07 20:45:26 2025.  exit_status = fail
"""


@pytest.mark.parametrize("callback", [SpecWriterCallback, SpecWriterCallback2])
def test_filename_defined(callback: FileWriterCallbackBase):
    """Test that default file name is not 'None'."""
    specwriter: FileWriterCallbackBase = callback()
    assert specwriter is not None
    assert specwriter.spec_filename is not None


def test_issue_1059(tempdir: pytest.fixture):
    """
    AttributeError: 'SpecWriterCallback2' object has no attribute 'data_labels'
    """
    data_file: pathlib.Path = tempdir / "issue_1059.dat"
    sig: SoftPositioner = SoftPositioner(name="sig", init_pos=0)

    documents: list = []

    def doc_collector(*args) -> None:
        nonlocal documents

        documents.append(args)

    with does_not_raise() as exinfo:
        specwriter: FileWriterCallbackBase = SpecWriterCallback2()
        specwriter.newfile(data_file)
        assert hasattr(specwriter, "data_labels")

        RE: RunEngine = RunEngine()
        RE.subscribe(specwriter.receiver)

        assert len(documents) == 0
        num_counts: int = 5
        RE(bp.count([sig], num=num_counts), doc_collector)
        assert len(documents) == 3 + num_counts  # start, descriptor, n events, stop

    assert exinfo is None


def test_issue_1083(tempdir: pytest.fixture):
    """
    ValueError raised on open data file to append & the file contains no runs.

    ``ValueError: max() arg is an empty sequence``
    """
    data_file = tempdir / "issue_1083.dat"

    with open(data_file, "w") as f:
        f.write(f"{DATA_ISSUE_1083.strip()}\n")
    assert data_file.exists()

    with does_not_raise() as exinfo:
        specwriter: FileWriterCallbackBase = SpecWriterCallback2()
        specwriter.newfile(data_file)
    assert exinfo is None
