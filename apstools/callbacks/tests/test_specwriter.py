import pytest
from ..spec_file_writer import SpecWriterCallback
from ..spec_file_writer import SpecWriterCallback2


@pytest.mark.parametrize("callback", [SpecWriterCallback, SpecWriterCallback2])
def test_filename_defined(callback):
    """Test that default file name is not 'None'."""
    specwriter = callback()
    assert specwriter is not None
    assert specwriter.spec_filename is not None
