
"""
unit tests for the filewriters
"""

import h5py
import json
import os
import shutil
import spec2nexus
import sys
import tempfile
import unittest
import zipfile

_test_path = os.path.dirname(__file__)
_path = os.path.join(_test_path, '..')
if _path not in sys.path:
    sys.path.insert(0, _path)

from tests.common import Capture_stdout, Capture_stderr

import apstools.filewriters
import apstools.utils

ZIP_FILE = os.path.join(_test_path, "usaxs_docs.json.zip")
JSON_FILE = "usaxs_docs.json.txt"


def write_stream(specwriter, stream):
    """write the doc stream to the file"""
    for document in stream:
        tag, doc = document
        specwriter.receiver(tag, doc)


def get_test_data():
    """get document streams as dict from zip file"""
    with zipfile.ZipFile(ZIP_FILE, "r") as fp:
        buf = fp.read(JSON_FILE).decode("utf-8")
        return json.loads(buf)


class Test_Data_is_Readable(unittest.TestCase):
    
    def test_00_testdata_exist(self):
        self.assertTrue(
            os.path.exists(ZIP_FILE), 
            "zip file with test data")
        with zipfile.ZipFile(ZIP_FILE, "r") as fp:
            self.assertIn(JSON_FILE, fp.namelist(), "JSON test data")
        
    def test_testfile_content(self):
        # get our test document stream
        datasets = get_test_data()
        
        census = {}
        for document in datasets["tune_mr"]:
            tag, _doc = document
            if tag not in census:
                census[tag] = 0
            census[tag] += 1
        
        # test that tune_mr content arrived intact
        keys = dict(start=1, descriptor=2, event=33, stop=1)
        self.assertEqual(
            len(census.keys()), 
            len(keys), 
            "four document types")
        for k, v in keys.items():
            self.assertIn(k, census, f"{k} document exists")
            self.assertEqual(
                census[k], 
                v, 
                f"expected {v} '{k}' document(s)")


class Test_FileWriterCallbackBase(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.db = get_test_data()

    def tearDown(self):
        if os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir, ignore_errors=True)
    
    def test_receiver_battery(self):
        callback = apstools.filewriters.FileWriterCallbackBase()
        for plan_name, document_set in self.db.items():
            callback.clear()
            self.assertIsNone(callback.uid)
            self.assertFalse(callback.scanning)

            for idx, document in enumerate(document_set):
                tag, doc = document
                with Capture_stdout() as printed:
                    callback.receiver(tag, doc)
                if tag == "start":
                    self.assertTrue(callback.scanning)
                elif tag == "stop":
                    # callback.writer called after stop document
                    self.assertGreater(len(str(printed)), 0)
                    self.assertEqual(printed[0], "print to console")
                    self.assertTrue(printed[1].startswith("suggested file name: "))

            self.assertEqual(callback.plan_name, plan_name)
            self.assertFalse(callback.scanning)
            self.assertIsNotNone(callback.uid)
            self.assertIsNotNone(callback.exit_status)
            self.assertIsNotNone(callback.start_time)
            self.assertIsNotNone(callback.stop_time)
            self.assertIsNotNone(callback.stop_reason)
            self.assertGreater(callback.stop_time, callback.start_time)
            self.assertEqual(len(callback.acquisitions), len(callback.streams))
            self.assertGreater(callback.scan_id, 0)


class Test_NXWriterBase(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.db = get_test_data()

    def tearDown(self):
        if os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir, ignore_errors=True)
    
    def test_make_file_name(self):
        callback = apstools.filewriters.NXWriterBase()

        self.assertIsNone(callback.file_path)
        self.assertIsNone(callback.scan_id)
        self.assertIsNone(callback.start_time)
        self.assertIsNone(callback.uid)

        with self.assertRaises(TypeError) as context:
            callback.make_file_name()
        self.assertEqual(
            'an integer is required (got type NoneType)',
            str(context.exception)
        )
        callback.start_time = 1000      # 1969-12-31T18:16:40

        with self.assertRaises(TypeError) as context:
            callback.make_file_name()
        self.assertEqual(
            'unsupported format string passed to NoneType.__format__',
            str(context.exception)
        )
        callback.scan_id = 9876

        with self.assertRaises(TypeError) as context:
            callback.make_file_name()
        self.assertEqual(
            "'NoneType' object is not subscriptable",
            str(context.exception)
        )
        callback.uid = "012345678901234567890123456789"

        fname = callback.make_file_name()
        expected = "19691231-181640"
        expected += f"-S{9876:05d}"
        expected += "-0123456"
        expected += f".{apstools.filewriters.NEXUS_FILE_EXTENSION}"
        self.assertEqual(os.path.split(fname)[-1], expected)
        self.assertEqual(os.path.dirname(fname), os.getcwd())

        callback.file_path = self.tempdir
        fname = callback.make_file_name()
        self.assertEqual(os.path.dirname(fname), self.tempdir)

    def test_receiver_battery(self):
        def str_tool(text):
            """Make string comparisons consistent."""
            if isinstance(text, bytes):
                text = text.decode()
            return text

        callback = apstools.filewriters.NXWriterBase()
        self.assertEqual(
            callback.nexus_release,
            apstools.filewriters.NEXUS_RELEASE)
        self.assertEqual(
            callback.file_extension,
            apstools.filewriters.NEXUS_FILE_EXTENSION)

        for plan_name, document_set in self.db.items():
            callback.clear()
            callback.file_path = self.tempdir
            self.assertIsNone(callback.uid)
            self.assertFalse(callback.scanning)

            for idx, document in enumerate(document_set):
                tag, doc = document
                with Capture_stdout() as printed:
                    # capture any logging messages, too
                    with Capture_stderr() as printed_error:
                        callback.receiver(tag, doc)

            fname = callback.make_file_name()
            self.assertTrue(os.path.exists(fname))
            with h5py.File(fname, "r") as nxroot:
                self.assertEqual(
                    nxroot.attrs["NeXus_version"],
                    apstools.filewriters.NEXUS_RELEASE)
                self.assertEqual(
                    nxroot.attrs["creator"],
                    callback.__class__.__name__)

                self.assertIn("/entry", nxroot)
                nxentry = nxroot["/entry"]
                self.assertEqual(
                    str_tool(nxentry["entry_identifier"][()]),
                    str_tool(callback.uid))
                self.assertEqual(
                    str_tool(nxentry["plan_name"][()]),
                    str_tool(callback.plan_name))

                self.assertIn("instrument", nxentry)
                nxinstrument = nxentry["instrument"]
                # TODO: /entry/instrument/bluesky/metadata
                # TODO: /entry/instrument/bluesky/streams
                self.assertIn("bluesky_metadata", nxinstrument)
                self.assertIn("bluesky_streams", nxinstrument)
                self.assertEqual(
                    len(nxinstrument["bluesky_streams"]),
                    len(callback.streams))

                # TODO: more tests for NeXus content


class Test_SpecWriterCallback(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.db = get_test_data()

    def tearDown(self):
        if os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir, ignore_errors=True)
    
    def test_writer_default_name(self):
        specwriter = apstools.filewriters.SpecWriterCallback()
        path = os.path.abspath(
            os.path.dirname(
                specwriter.spec_filename))
        self.assertNotEqual(
            path, 
            self.tempdir, 
            "default file not in tempdir")
        self.assertEqual(
            path, 
            os.path.abspath(os.getcwd()), 
            "default file to go in pwd")

        # change the directory
        specwriter.spec_filename = os.path.join(
            self.tempdir, 
            specwriter.spec_filename)

        self.assertFalse(
            os.path.exists(specwriter.spec_filename), 
            "data file not created yet")
        write_stream(specwriter, self.db["tune_mr"])
        self.assertTrue(
            os.path.exists(specwriter.spec_filename), 
            "data file created")

        sdf = spec2nexus.spec.SpecDataFile(specwriter.spec_filename)
        self.assertEqual(len(sdf.headers), 1)
        self.assertEqual(len(sdf.scans), 1)

        # check that the #N line is written properly (issue #203)
        scans = sdf.getScanNumbers()
        self.assertNotIn(108, scans)
        self.assertIn("108", scans)
        scan = sdf.getScan(108)
        self.assertEqual(scan.N[0], len(scan.L))
        
        self.assertGreater(scan.header.raw.find("\n#O0 \n"), 0)
        self.assertGreater(scan.header.raw.find("\n#o0 \n"), 0)
        self.assertEqual(len(scan.header.O), 1)
        self.assertEqual(len(scan.header.O[0]), 0)
        self.assertEqual(len(scan.header.o), 1)
        self.assertEqual(len(scan.header.o[0]), 0)

        self.assertGreater(scan.raw.find("\n#P0 \n"), 0)
        self.assertEqual(len(scan.P), 1)
        self.assertEqual(len(scan.P[0]), 0)
        self.assertEqual(len(scan.positioner), 0)

    def test_writer_filename(self):
        self.assertTrue(len(self.db) > 0, "test data ready")

        testfile = os.path.join(self.tempdir, "tune_mr.dat")
        if os.path.exists(testfile):
            os.remove(testfile)
        specwriter = apstools.filewriters.SpecWriterCallback(filename=testfile)

        self.assertIsInstance(
            specwriter, apstools.filewriters.SpecWriterCallback, 
            "specwriter object")
        self.assertEqual(
            specwriter.spec_filename, 
            testfile, 
            "output data file")

        self.assertFalse(
            os.path.exists(testfile), 
            "data file not created yet")
        write_stream(specwriter, self.db["tune_mr"])
        self.assertTrue(os.path.exists(testfile), "data file created")

    def test_newfile_exists(self):
        testfile = os.path.join(self.tempdir, "tune_mr.dat")
        if os.path.exists(testfile):
            os.remove(testfile)
        specwriter = apstools.filewriters.SpecWriterCallback(filename=testfile)

        from apstools.filewriters import SCAN_ID_RESET_VALUE
        self.assertEqual(SCAN_ID_RESET_VALUE, 0, "default reset scan id")

        write_stream(specwriter, self.db["tune_mr"])
        self.assertTrue(os.path.exists(testfile), "data file created")
        
        raised = False
        try:
            specwriter.newfile(filename=testfile)
        except ValueError:
            raised = True
        finally:
            self.assertFalse(raised, "file exists")
        self.assertEqual(specwriter.reset_scan_id, 0, "check scan id")
        
        class my_RunEngine:
            # dick type for testing _here_
            md = dict(scan_id=SCAN_ID_RESET_VALUE)
        RE = my_RunEngine()
        
        specwriter.scan_id = -5  # an unusual value for testing only
        RE.md["scan_id"] = -10   # an unusual value for testing only
        specwriter.newfile(filename=testfile, scan_id=None, RE=RE)
        self.assertEqual(specwriter.scan_id, 108, "scan_id unchanged")
        self.assertEqual(RE.md["scan_id"], 108, "RE.md['scan_id'] unchanged")

        specwriter.scan_id = -5  # an unusual value for testing only
        RE.md["scan_id"] = -10   # an unusual value for testing only
        specwriter.newfile(filename=testfile, scan_id=False, RE=RE)
        self.assertEqual(specwriter.scan_id, 108, "scan_id unchanged")
        self.assertEqual(RE.md["scan_id"], 108, "RE.md['scan_id'] unchanged")

        specwriter.scan_id = -5  # an unusual value for testing only
        RE.md["scan_id"] = -10   # an unusual value for testing only
        specwriter.newfile(filename=testfile, scan_id=True, RE=RE)
        self.assertEqual(specwriter.scan_id, 108, "scan_id reset")
        self.assertEqual(RE.md["scan_id"], 108, "RE.md['scan_id'] reset")

        for n, s in {'0': 108, '108': 108, '110': 110}.items():
            specwriter.scan_id = -5  # an unusual value for testing only
            RE.md["scan_id"] = -10   # an unusual value for testing only
            specwriter.newfile(filename=testfile, scan_id=int(n), RE=RE)
            self.assertEqual(specwriter.scan_id, s, f"scan_id set to {n}, actually {s}")
            self.assertEqual(RE.md["scan_id"], s, f"RE.md['scan_id'] set to {n}, actually {s}")
    
    def test__rebuild_scan_command(self):
        from apstools.filewriters import _rebuild_scan_command

        self.assertTrue(len(self.db) > 0, "test data ready")

        start_docs = []
        for header in self.db["tune_mr"]:
            tag, doc = header
            if tag == "start":
                start_docs.append(doc)
        self.assertEqual(len(start_docs), 1, "unique start doc found")

        doc = start_docs[0]
        expected = "108  tune_mr()"
        result = _rebuild_scan_command(doc)
        self.assertEqual(result, expected, "rebuilt #S line")
    
    def test_spec_comment(self):
        from apstools.filewriters import spec_comment
        
        # spec_comment(comment, doc=None, writer=None)
        testfile = os.path.join(self.tempdir, "spec_comment.dat")
        if os.path.exists(testfile):
            os.remove(testfile)
        specwriter = apstools.filewriters.SpecWriterCallback(filename=testfile)

        for category in "buffered_comments comments".split():
            for k in "start stop descriptor event".split():
                o = getattr(specwriter, category)
                self.assertEqual(len(o[k]), 0, f"no '{k}' {category}")
        
        # insert comments with every document
        spec_comment(
            "TESTING: Should appear within start doc", 
            doc=None, 
            writer=specwriter)

        for idx, document in enumerate(self.db["tune_mr"]):
            tag, doc = document
            msg = f"TESTING: document {idx+1}: '{tag}' %s specwriter.receiver"
            spec_comment(
                msg % "before", 
                doc=tag, 
                writer=specwriter)
            specwriter.receiver(tag, doc)
            if tag == "stop":
                # since stop doc was received, this appears in the next scan
                spec_comment(
                    str(msg % "before") + " (appears at END of next scan)", 
                    doc=tag, 
                    writer=specwriter)
            else:
                spec_comment(
                    msg % "after", 
                    doc=tag, 
                    writer=specwriter)

        self.assertEqual(
            len(specwriter.buffered_comments['stop']), 
            1, 
            "last 'stop' comment buffered")
        
        # since stop doc was received, this appears in the next scan
        spec_comment(
            "TESTING: Appears at END of next scan", 
            doc="stop", 
            writer=specwriter)

        self.assertEqual(
            len(specwriter.buffered_comments['stop']), 
            2, 
            "last end of scan comment buffered")
        write_stream(specwriter, self.db["tune_ar"])

        for k in "start descriptor event".split():
            o = specwriter.buffered_comments
            self.assertEqual(len(o[k]), 0, f"no '{k}' {category}")
        expected = dict(start=2, stop=5, event=0, descriptor=0)
        for k, v in expected.items():
            self.assertEqual(
                len(specwriter.comments[k]), 
                v, 
                f"'{k}' comments")


def suite(*args, **kw):
    test_list = [
        Test_Data_is_Readable,
        Test_SpecWriterCallback,
        Test_FileWriterCallbackBase,
        Test_NXWriterBase,
        # Test_NXWriterAps,
        ]
    test_suite = unittest.TestSuite()
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == "__main__":
    runner=unittest.TextTestRunner()
    runner.run(suite())
