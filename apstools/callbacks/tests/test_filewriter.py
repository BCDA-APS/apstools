"""
unit tests for the filewriters
"""

import pathlib
import tempfile

import databroker
import h5py
import numpy
import pytest
import spec2nexus.spec

from ...utils import replay
from .. import NEXUS_FILE_EXTENSION
from .. import NEXUS_RELEASE
from .. import NXWriter
from .. import NXWriterAPS
from .. import SpecWriterCallback
from ..callback_base import FileWriterCallbackBase

CATALOG = "usaxs_test"
TUNE_AR = 103  # <-- scan_id,  uid: "3554003"
TUNE_MR = 108  # <-- scan_id,  uid: "2ffe4d8"


@pytest.fixture(scope="function")
def cat():
    cat = databroker.catalog[CATALOG]
    return cat


@pytest.fixture(scope="function")
def tempdir():
    tempdir = tempfile.mkdtemp()
    return pathlib.Path(tempdir)


def to_string(text):
    """Make string comparisons consistent."""
    if isinstance(text, bytes):
        text = text.decode()
    return text


def write_stream(specwriter, stream):
    """write the doc stream to the file"""
    for tag, doc in stream:
        specwriter.receiver(tag, doc)


@pytest.mark.parametrize(
    "ref, md_tag, md_key, md_value",
    [
        ["99f", "start", "uid", "99fe9e07-6a44-4834-856f-e48432fb01e5"],
        ["99f", "start", "scan_id", 2],
        [2, "start", "uid", "555a6047-acd9-46a8-85b0-234986ae1323"],
        [2, "start", "scan_id", 2],
        [110, "start", "uid", "19965989-0a2a-44aa-aa06-c1248754e651"],
        ["19965989-0a2a-44aa-aa06-c1248754e651", "start", "scan_id", 110],
        ["19965989-0a2a", "start", "scan_id", 110],
        [103, "start", "plan_name", "tune_ar"],
        [108, "start", "plan_name", "tune_mr"],
        [110, "start", "plan_name", "Flyscan"],
    ],
)
def test_metadata_keys(ref, md_tag, md_key, md_value, cat):
    assert len(cat) == 10
    assert cat[ref].metadata[md_tag][md_key] == md_value


@pytest.mark.parametrize(
    "ref, tag_sequence",
    [
        ["555a604", ["start"] + ["descriptor"] * 2 + ["event"] * 3 + ["stop"]],
        [2, ["start"] + ["descriptor"] * 2 + ["event"] * 3 + ["stop"]],
        ["99f", ["start"] + ["descriptor"] * 2 + ["event"] * 33 + ["stop"]],
        [103, ["start"] + ["descriptor"] * 2 + ["event"] * 37 + ["stop"]],
        [108, ["start"] + ["descriptor"] * 2 + ["event"] * 33 + ["stop"]],
        [110, ["start"] + ["descriptor"] * 2 + ["event"] * 3 + ["stop"]],
    ],
)
def test_document_sequence(ref, tag_sequence, cat):
    run = cat.v1[ref]
    document_keys = [k for k, _ in run.documents()]
    assert len(document_keys) == len(tag_sequence), f"{document_keys=}"
    for tag, item in zip(tag_sequence, list(run.documents())):
        assert isinstance(item, (list, tuple))
        assert len(item) == 2
        assert item[0] == tag


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
    callback.file_path = str(tempdir)

    replay(cat.v1[TUNE_MR], callback.receiver)

    fname = pathlib.Path(callback.make_file_name())
    callback.wait_writer()

    assert fname.exists()
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
    callback.file_path = str(tempdir)

    replay(cat.v1[TUNE_MR], callback.receiver)

    fname = pathlib.Path(callback.make_file_name())
    callback.wait_writer()

    assert fname.exists()
    with h5py.File(fname, "r") as nxroot:
        assert nxroot is not None

        default_entry = nxroot.attrs.get("default")
        assert default_entry == "entry"
        assert default_entry in nxroot

        nxentry = nxroot[default_entry]
        assert nxentry is not None

        default_data = nxentry.attrs.get("default")
        assert default_data == "data"
        assert default_data in nxentry

        nxdata = nxentry[default_data]
        default_signal = nxdata.attrs.get("signal")
        assert default_signal is not None
        assert default_signal in nxdata

        signal = nxdata[default_signal]
        assert signal is not None
        assert isinstance(signal[()], numpy.ndarray)

        signal_shape = signal[()].shape
        assert len(signal_shape) > 0
        assert signal_shape[0] > 0

        default_axes = nxdata.attrs.get("axes")
        assert default_axes is not None
        assert isinstance(default_axes, numpy.ndarray)
        assert default_axes.dtype == "O"
        assert len(default_axes) > 0
        for axis_name in default_axes:
            assert axis_name != default_signal
            assert axis_name in nxdata

            axis = nxdata[axis_name]
            assert axis is not None
            assert isinstance(axis[()], numpy.ndarray)
            assert axis[()].shape == signal_shape


def test_NXWriter_make_file_name(tempdir):
    import datetime

    import dateutil.tz

    callback = NXWriter()

    assert callback.file_path is None
    assert callback.scan_id is None
    assert callback.start_time is None
    assert callback.uid is None

    with pytest.raises(TypeError) as exinfo:
        # error from f"-S{self.scan_id:05d}"
        callback.make_file_name()
    assert exinfo is not None
    assert "NoneType" in str(exinfo.value), f"{callback=} {exinfo=}"
    assert "an integer" in str(exinfo.value), f"{callback=} {exinfo=}"

    callback.start_time = 1000  # 1969-12-31T18:16:40
    with pytest.raises(TypeError) as exinfo:
        # error from datetime.datetime.fromtimestamp
        callback.make_file_name()
    expected = "unsupported format string passed to NoneType.__format__"
    assert expected == str(exinfo.value)

    callback.scan_id = 9876
    with pytest.raises(TypeError) as exinfo:
        callback.make_file_name()
    assert "'NoneType' object is not subscriptable" == str(exinfo.value)

    callback.uid = "012345678901234567890123456789"
    fname = pathlib.Path(callback.make_file_name())
    assert fname.parent == callback.file_path or pathlib.Path(".").absolute()

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
    assert fname.name == expected

    callback.file_path = str(tempdir)
    fname = pathlib.Path(callback.make_file_name())
    assert fname.parent == tempdir


def test_NXWriter_receiver_battery(cat, tempdir):
    callback = NXWriter()
    assert callback.nexus_release == NEXUS_RELEASE
    assert callback.file_extension == NEXUS_FILE_EXTENSION

    for uid in cat:
        callback.clear()
        callback.file_path = str(tempdir)
        assert callback.uid is None
        assert not callback.scanning

        replay(cat.v1[uid], callback.receiver)

        fname = pathlib.Path(callback.make_file_name())
        callback.wait_writer()

        assert fname.exists()
        with h5py.File(fname, "r") as nxroot:
            assert nxroot.attrs.get("NeXus_release") == NEXUS_RELEASE
            assert nxroot.attrs.get("creator") == callback.__class__.__name__

            nxentry = nxroot["/entry"]
            assert to_string(nxentry["entry_identifier"][()]) == to_string(callback.uid)
            assert to_string(nxentry["plan_name"][()]) == to_string(callback.plan_name)

            nxinstrument = nxentry["instrument"]
            for subgroup_name in "detectors positioners".split():
                if subgroup_name in nxinstrument:
                    subgroup = nxinstrument[subgroup_name]
                    assert len(subgroup) > 0, f"{uid[:7]=}  {subgroup_name=} is empty"

            assert "bluesky" in nxinstrument
            bluesky_group = nxinstrument["bluesky"]
            assert "metadata" in bluesky_group
            assert "streams" in bluesky_group
            assert len(bluesky_group["streams"]) == len(callback.streams)

            assert "undulator" not in nxinstrument


def test_SpecWriterCallback_writer_default_name(cat, tempdir):
    specwriter = SpecWriterCallback()
    path = pathlib.Path(specwriter.spec_filename).parent
    assert path != tempdir  # "default file not in tempdir"

    # change the directory
    fname = tempdir / specwriter.spec_filename
    assert not fname.exists()  # "data file not created yet"

    specwriter.spec_filename = pathlib.Path(fname)
    write_stream(specwriter, cat.v1[TUNE_MR].documents())
    assert str(fname) == str(specwriter.spec_filename)  # confirm unchanged
    assert fname.exists()  # "data file created"

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
    assert len(scan.header.o) == 1

    assert scan.raw.find("\n#P0 \n") > 0
    assert len(scan.P) == 1
    assert len(scan.positioner) == 0


def test_SpecWriterCallback_writer_filename(cat, tempdir):
    testfile = tempdir / "tune_mr.dat"
    if testfile.exists():
        testfile.unlink()  # remove
    specwriter = SpecWriterCallback(filename=testfile)

    assert isinstance(specwriter, SpecWriterCallback)
    assert specwriter.spec_filename == testfile

    assert not testfile.exists()
    write_stream(specwriter, cat.v1[TUNE_MR].documents())
    assert testfile.exists()


def test_SpecWriterCallback_newfile_exists(cat, tempdir):
    testfile = tempdir / "tune_mr.dat"
    if testfile.exists():
        testfile.unlink()  # remove
    specwriter = SpecWriterCallback(filename=testfile)

    from .. import SCAN_ID_RESET_VALUE

    assert SCAN_ID_RESET_VALUE == 0  # "default reset scan id"

    write_stream(specwriter, cat.v1[TUNE_MR].documents())
    assert testfile.exists()  # "data file created"

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


def test_SpecWriterCallback__rebuild_scan_command(cat):
    from ..spec_file_writer import _rebuild_scan_command

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
    from .. import spec_comment

    # spec_comment(comment, doc=None, writer=None)
    testfile = tempdir / "spec_comment.dat"
    if testfile.exists():
        testfile.unlink()  # remove
    specwriter = SpecWriterCallback(filename=testfile)

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
