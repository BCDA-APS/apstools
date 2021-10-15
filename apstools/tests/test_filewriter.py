"""
unit tests for the filewriters
"""
import databroker
import h5py
import os
import pytest
import spec2nexus.spec
import tempfile

from ..filewriters import FileWriterCallbackBase
from ..filewriters import NEXUS_FILE_EXTENSION
from ..filewriters import NEXUS_RELEASE
from ..filewriters import NXWriter
from ..filewriters import NXWriterAPS
from ..filewriters import SpecWriterCallback

CATALOG = "usaxs_test"
COUNT = "555a604"  # <-- uid,  scan_id: 2
TUNE_AR = 103  # <-- scan_id,  uid: "3554003"
TUNE_MR = 108  # <-- scan_id,  uid: "2ffe4d8"


@pytest.fixture(scope="function")
def cat():
    cat = databroker.catalog[CATALOG]
    return cat


@pytest.fixture(scope="function")
def tempdir():
    tempdir = tempfile.mkdtemp()
    return tempdir


def to_string(text):
    """Make string comparisons consistent."""
    if isinstance(text, bytes):
        text = text.decode()
    return text


def write_stream(specwriter, stream):
    """write the doc stream to the file"""
    for tag, doc in stream:
        specwriter.receiver(tag, doc)


def test_catalog(cat):
    assert len(cat) == 10
    assert cat["99f"].metadata["start"]["scan_id"] == 2
    assert cat[110].metadata["start"]["uid"][:5] == "19965"


def test_replay(cat):
    run = cat.v1[COUNT]
    assert len(list(run.documents())) == 7
    di = iter(run.documents())
    key, doc = next(di)
    assert key == "start"
    key, doc = next(di)
    assert key == "descriptor"
    key, doc = next(di)
    assert key == "descriptor"
    key, doc = next(di)
    assert key == "event"
    key, doc = next(di)
    assert key == "event"
    key, doc = next(di)
    assert key == "event"
    key, doc = next(di)
    assert key == "stop"


def test_FileWriterCallbackBase(cat, capsys):
    callback = FileWriterCallbackBase()
    for uid in cat:
        run = cat.v1[uid]
        callback.clear()
        assert callback.uid is None
        assert callback.scanning is False

        for tag, doc in run.documents():
            callback.receiver(tag, doc)
            out, err = capsys.readouterr()
            if tag == "start":
                assert callback.scanning is True
            elif tag == "stop":
                # callback.writer called after stop document
                lines = out.splitlines()
                assert len(lines) > 0
                assert lines[0] == "print to console"
                assert lines[1].startswith("suggested file name: ")

        assert callback.plan_name == run["start"]["plan_name"]
        assert not callback.scanning
        assert callback.uid is not None
        assert callback.exit_status is not None
        assert callback.start_time is not None
        assert callback.stop_time is not None
        assert callback.stop_reason is not None
        assert callback.stop_time > callback.start_time
        assert len(callback.acquisitions) == len(callback.streams)
        assert callback.scan_id > 0


def test_NXWriterAPS(cat, tempdir):
    callback = NXWriterAPS()
    callback.file_path = tempdir

    run = cat.v1[TUNE_MR]
    for tag, doc in run.documents():
        callback.receiver(tag, doc)

    fname = callback.make_file_name()
    assert os.path.exists(fname)
    with h5py.File(fname, "r") as nxroot:
        assert "/entry/instrument/source" in nxroot
        nxsource = nxroot["/entry/instrument/source"]
        assert to_string(nxsource["name"][()]) == "Advanced Photon Source"
        assert nxsource["name"].attrs["short_name"] == "APS"
        assert to_string(nxsource["type"][()]) == "Synchrotron X-ray Source"
        assert to_string(nxsource["probe"][()]) == "x-ray"
        assert nxsource["energy"][()] == 6
        assert nxsource["energy"].attrs["units"] == "GeV"
        assert "/entry/instrument/undulator" in nxroot


def test_NXWriter_default_plot(cat, tempdir):
    callback = NXWriterAPS()
    callback.file_path = tempdir

    run = cat.v1[TUNE_MR]
    for tag, doc in run.documents():
        callback.receiver(tag, doc)

    fname = callback.make_file_name()
    assert os.path.exists(fname)
    with h5py.File(fname, "r") as nxroot:
        assert nxroot.attrs["default"] == "entry"
        assert nxroot["/entry"].attrs["default"] == "data"
        nxdata = nxroot["/entry/data"]
        signal = nxdata.attrs.get("signal")
        assert signal is not None
        assert signal in nxdata
        axes = nxdata.attrs.get("axes")
        assert axes is not None
        assert len(axes) == 1
        assert axes[0] in nxdata
        assert axes[0] != signal


def test_NXWriter_make_file_name(tempdir):
    import datetime
    import dateutil.tz

    callback = NXWriter()

    assert callback.file_path is None
    assert callback.scan_id is None
    assert callback.start_time is None
    assert callback.uid is None

    with pytest.raises(TypeError) as exinfo:
        callback.make_file_name()
    assert (
        "an integer is required (got type NoneType)"
        in str(exinfo.value)
    )
    callback.start_time = 1000  # 1969-12-31T18:16:40

    with pytest.raises(TypeError) as exinfo:
        callback.make_file_name()
    assert (
        "unsupported format string passed to NoneType.__format__"
        ==
        str(exinfo.value)
    )
    callback.scan_id = 9876

    with pytest.raises(TypeError) as exinfo:
        callback.make_file_name()
    assert "'NoneType' object is not subscriptable" == str(exinfo.value)
    callback.uid = "012345678901234567890123456789"

    fname = callback.make_file_name()
    # https://github.com/BCDA-APS/apstools/issues/345
    tz_aps = dateutil.tz.gettz("America/Chicago")
    tz_local = dateutil.tz.tzlocal()
    # datetime at the APS: 1969-12-31-18:16:40"
    dt = datetime.datetime.fromtimestamp(callback.start_time, tz_aps)
    # datetime on the local python test workstation
    dt_local = dt.astimezone(tz_local)
    # render `expected` in local time zone
    expected = dt_local.strftime("%Y%m%d-%H%M%S")
    expected += f"-S{9876:05d}"
    expected += "-0123456"
    expected += f".{NEXUS_FILE_EXTENSION}"
    assert os.path.split(fname)[-1] == expected
    assert os.path.dirname(fname) == os.getcwd()

    callback.file_path = tempdir
    fname = callback.make_file_name()
    assert os.path.dirname(fname) == tempdir


def test_NXWriter_receiver_battery(cat, tempdir):
    callback = NXWriter()
    assert callback.nexus_release == NEXUS_RELEASE
    assert callback.file_extension == NEXUS_FILE_EXTENSION

    for uid in cat:
        run = cat.v1[uid]
        callback.clear()
        callback.file_path = tempdir
        assert callback.uid is None
        assert not callback.scanning

        for tag, doc in run.documents():
            callback.receiver(tag, doc)

        fname = callback.make_file_name()
        assert os.path.exists(fname)
        with h5py.File(fname, "r") as nxroot:
            assert nxroot.attrs["NeXus_version"] == NEXUS_RELEASE
            assert nxroot.attrs["creator"] == callback.__class__.__name__

            assert "/entry" in nxroot
            nxentry = nxroot["/entry"]
            assert to_string(nxentry["entry_identifier"][()]) == to_string(callback.uid)
            assert to_string(nxentry["plan_name"][()]) == to_string(callback.plan_name)

            assert "instrument/bluesky" in nxentry
            bluesky_group = nxentry["instrument/bluesky"]
            assert "metadata" in bluesky_group
            assert "streams" in bluesky_group
            assert len(bluesky_group["streams"]) == len(callback.streams)

            assert "/entry/instrument/undulator" not in nxroot


def test_SpecWriterCallback_writer_default_name(cat, tempdir):
    specwriter = SpecWriterCallback()
    path = os.path.abspath(os.path.dirname(specwriter.spec_filename))
    assert path != tempdir  # "default file not in tempdir"
    assert path == os.path.abspath(os.getcwd())  # "default file to go in pwd"

    # change the directory
    specwriter.spec_filename = os.path.join(
        tempdir, specwriter.spec_filename
    )

    assert not os.path.exists(specwriter.spec_filename)  # "data file not created yet"
    write_stream(specwriter, cat.v1[TUNE_MR].documents())
    assert os.path.exists(specwriter.spec_filename)  # "data file created"

    sdf = spec2nexus.spec.SpecDataFile(specwriter.spec_filename)
    assert len(sdf.headers) == 1
    assert len(sdf.scans) == 1

    # check that the #N line is written properly (issue #203)
    scans = sdf.getScanNumbers()
    assert 108 not in scans
    assert str(108) in scans
    scan = sdf.getScan(108)
    assert scan.N[0] == len(scan.L)

    assert scan.header.raw.find("\n#O0 \n") > 0
    assert scan.header.raw.find("\n#o0 \n") > 0
    assert len(scan.header.O) == 1
    assert len(scan.header.O[0]) == 0
    assert len(scan.header.o) == 1
    assert len(scan.header.o[0]) == 0

    assert scan.raw.find("\n#P0 \n") > 0
    assert len(scan.P) == 1
    assert len(scan.P[0]) == 0
    assert len(scan.positioner) == 0


def test_SpecWriterCallback_writer_filename(cat, tempdir):
    testfile = os.path.join(tempdir, "tune_mr.dat")
    if os.path.exists(testfile):
        os.remove(testfile)
    specwriter = SpecWriterCallback(filename=testfile)

    assert isinstance(specwriter, SpecWriterCallback)
    assert specwriter.spec_filename == testfile

    assert not os.path.exists(testfile)
    write_stream(specwriter, cat.v1[TUNE_MR].documents())
    assert os.path.exists(testfile)


def test_SpecWriterCallback_newfile_exists(cat, tempdir):
    testfile = os.path.join(tempdir, "tune_mr.dat")
    if os.path.exists(testfile):
        os.remove(testfile)
    specwriter = SpecWriterCallback(
        filename=testfile
    )

    from apstools.filewriters import SCAN_ID_RESET_VALUE

    assert SCAN_ID_RESET_VALUE == 0  # "default reset scan id"

    write_stream(specwriter, cat.v1[TUNE_MR].documents())
    assert os.path.exists(testfile)  # "data file created"

    raised = False
    try:
        specwriter.newfile(filename=testfile)
    except ValueError:
        raised = True
    finally:
        assert not raised  # "file exists"
    assert specwriter.reset_scan_id == 0  # "check scan id"

    class my_RunEngine:
        # duck type model *strictly* for testing *here*
        md = dict(scan_id=SCAN_ID_RESET_VALUE)

    RE = my_RunEngine()

    specwriter.scan_id = -5  # an unusual value for testing only
    RE.md["scan_id"] = -10  # an unusual value for testing only
    specwriter.newfile(filename=testfile, scan_id=None, RE=RE)
    assert specwriter.scan_id == 108  # "scan_id unchanged"
    assert RE.md["scan_id"] == 108  # "RE.md['scan_id'] unchanged"

    specwriter.scan_id = -5  # an unusual value for testing only
    RE.md["scan_id"] = -10  # an unusual value for testing only
    specwriter.newfile(filename=testfile, scan_id=False, RE=RE)
    assert specwriter.scan_id == 108  # "scan_id unchanged"
    assert RE.md["scan_id"] == 108  # "RE.md['scan_id'] unchanged"

    specwriter.scan_id = -5  # an unusual value for testing only
    RE.md["scan_id"] = -10  # an unusual value for testing only
    specwriter.newfile(filename=testfile, scan_id=True, RE=RE)
    assert specwriter.scan_id == 108  # "scan_id reset"
    assert RE.md["scan_id"] == 108  # "RE.md['scan_id'] reset"

    for n, s in {"0": 108, "108": 108, "110": 110}.items():
        specwriter.scan_id = -5  # an unusual value for testing only
        RE.md["scan_id"] = -10  # an unusual value for testing only
        specwriter.newfile(filename=testfile, scan_id=int(n), RE=RE)
        assert specwriter.scan_id == s
        assert RE.md["scan_id"] == s


def test_SpecWriterCallback__rebuild_scan_command(cat, tempdir):
    from apstools.filewriters import _rebuild_scan_command

    start_docs = []
    for tag, doc in cat.v1[TUNE_MR].documents():
        if tag == "start":
            start_docs.append(doc)
    assert len(start_docs) == 1  # "unique start doc found"

    doc = start_docs[0]
    expected = "108  tune_mr()"
    result = _rebuild_scan_command(doc)
    assert result == expected  # "rebuilt #S line"


def test_SpecWriterCallback_spec_comment(cat, tempdir):
    from apstools.filewriters import spec_comment

    # spec_comment(comment, doc=None, writer=None)
    testfile = os.path.join(tempdir, "spec_comment.dat")
    if os.path.exists(testfile):
        os.remove(testfile)
    specwriter = SpecWriterCallback(
        filename=testfile
    )

    for category in "buffered_comments comments".split():
        for k in "start stop descriptor event".split():
            o = getattr(specwriter, category)
            assert len(o[k]) == 0

    # insert comments with every document
    spec_comment(
        "TESTING: Should appear within start doc",
        doc=None,
        writer=specwriter,
    )

    for idx, document in enumerate(cat.v1[TUNE_MR].documents()):
        tag, doc = document
        msg = f"TESTING: document {idx+1}: '{tag}' %s specwriter.receiver"
        spec_comment(msg % "before", doc=tag, writer=specwriter)
        specwriter.receiver(tag, doc)
        if tag == "stop":
            # since stop doc was received, this appears in the next scan
            spec_comment(
                str(msg % "before") + " (appears at END of next scan)",
                doc=tag,
                writer=specwriter,
            )
        else:
            spec_comment(msg % "after", doc=tag, writer=specwriter)

    assert len(specwriter.buffered_comments["stop"]) == 1

    # since stop doc was received, this appears in the next scan
    spec_comment(
        "TESTING: Appears at END of next scan",
        doc="stop",
        writer=specwriter,
    )

    assert len(specwriter.buffered_comments["stop"]) == 2
    write_stream(specwriter, cat.v1[TUNE_AR].documents())

    for k in "start descriptor event".split():
        o = specwriter.buffered_comments
        assert len(o[k]) == 0
    expected = dict(start=2, stop=5, event=0, descriptor=0)
    for k, v in expected.items():
        assert len(specwriter.comments[k]) == v
