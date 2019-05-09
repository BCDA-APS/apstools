
"""
unit tests for the SPEC filewriter
"""

import json
import os
import shutil
import sys
import tempfile
import unittest
import zipfile

_test_path = os.path.dirname(__file__)
_path = os.path.join(_test_path, '..')
if _path not in sys.path:
    sys.path.insert(0, _path)

from apstools.filewriters import SpecWriterCallback


ZIP_FILE = os.path.join(_test_path, "usaxs_docs.json.zip")
JSON_FILE = "usaxs_docs.json.txt"


def write_stream(specwriter, stream):
    """write the doc stream to the file"""
    for document in stream:
        tag, doc = document
        specwriter.receiver(tag, doc)


class Test_Data_is_Readable(unittest.TestCase):
    
    def test_00_testfile_exists(self):
        self.assertTrue(
            os.path.exists(ZIP_FILE), 
            "zip file with test data")
        
    
    def test_testfile_content(self):
        # get our test document stream
        with zipfile.ZipFile(ZIP_FILE, "r") as fp:
            self.assertIn(JSON_FILE, fp.namelist(), "JSON test data")
            buf = fp.read(JSON_FILE).decode("utf-8")
            datasets = json.loads(buf)
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


class Test_newfile(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.db = None
        # get our test document stream
        with zipfile.ZipFile(ZIP_FILE, "r") as fp:
            buf = fp.read(JSON_FILE).decode("utf-8")
            self.db = json.loads(buf)

    def tearDown(self):
        if os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir, ignore_errors=True)
    
    def test_writer_default_name(self):
        specwriter = SpecWriterCallback()
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
    
    def test_writer_filename(self):
        self.assertTrue(len(self.db) > 0, "test data ready")

        testfile = os.path.join(self.tempdir, "tune_mr.dat")
        specwriter = SpecWriterCallback(filename=testfile)

        self.assertIsInstance(
            specwriter, SpecWriterCallback, 
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
        specwriter = SpecWriterCallback(filename=testfile)
        write_stream(specwriter, self.db["tune_mr"])
        self.assertTrue(os.path.exists(testfile), "data file created")
        
        # TODO: #128 do not raise if exists
        try:
            specwriter.newfile(filename=testfile)
            raised = False
        except ValueError:
            raised = True
        finally:
            self.assertTrue(raised, "file exists")


def suite(*args, **kw):
    test_list = [
        Test_Data_is_Readable,
        Test_newfile,
        ]
    test_suite = unittest.TestSuite()
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == "__main__":
    runner=unittest.TextTestRunner()
    runner.run(suite())
