from ..spec_file_writer import SpecWriterCallback2


def test_filename_defined():
    """Test that default file name is not 'None'."""
    specwriter = SpecWriterCallback2()
    assert specwriter is not None
    assert specwriter.spec_filename is not None
