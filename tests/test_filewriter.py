
"""
unit tests for the SPEC filewriter
"""

import os
import sys
import unittest

_test_path = os.path.dirname(__file__)
_path = os.path.join(_test_path, '..')
if _path not in sys.path:
    sys.path.insert(0, _path)

import apstools
from apstools.filewriters import SpecWriterCallback
from databroker import Broker
import json
import shutil
import tempfile
import zipfile


"""
sqlite fails with this error:

  File "/home/mintadmin/Apps/anaconda/envs/bluesky/lib/python3.6/site-packages/databroker/headersource/sqlite.py", line 257, in _insert_events
    values[desc_uid])
sqlite3.InterfaceError: Error binding parameter 107 - probably unsupported type.

Can we pick a different backend for temporary work?
"""

ZIP_FILE = os.path.join(_test_path, "usaxs_docs.json.zip")
JSON_FILE = "usaxs_docs.json.txt"


class Test_Data_is_Readable(unittest.TestCase):
    
    def test_00_testfile_exists(self):
        self.assertTrue(os.path.exists(ZIP_FILE), "zip file with test data")
        
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
        self.assertEqual(len(census.keys()), len(keys), "four document types")
        for k, v in keys.items():
            self.assertIn(k, census, f"{k} document exists")
            self.assertEqual(census[k], v, f"expected {v} '{k}' document(s)")


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
    
    def test_writer(self):
        self.assertTrue(len(self.db) > 0, "test data ready")

        testfile = os.path.join(self.tempdir, "tune_mr.dat")
        specwriter = SpecWriterCallback(filename=testfile)

        self.assertIsInstance(specwriter, SpecWriterCallback, "specwriter object")
        self.assertEqual(specwriter.spec_filename, testfile, "output data file")
        self.assertFalse(os.path.exists(testfile), "data file not created yet")

        # write the doc stream to the file
        for document in self.db["tune_mr"]:
            tag, doc = document
            specwriter.receiver(tag, doc)

        self.assertTrue(os.path.exists(testfile), "data file created")
        
        # TODO: test newfile() with existing file


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
