
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


class Test_Something(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir, ignore_errors=True)
    
    def test_newfile(self):
        self.assertTrue(os.path.exists(ZIP_FILE), "zip file with test data")
        
        # get our test document stream
        with zipfile.ZipFile(ZIP_FILE, "r") as fp:
            self.assertIn(JSON_FILE, fp.namelist(), "JSON test data")
            buf = fp.read(JSON_FILE).decode("utf-8")
            datasets = json.loads(buf)
            for document in datasets["tune_mr"]:
                tag, doc = document
                print(tag)
        
        # TODO: finish this test


def suite(*args, **kw):
    test_list = [
        Test_Something,
        ]
    test_suite = unittest.TestSuite()
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == "__main__":
    runner=unittest.TextTestRunner()
    runner.run(suite())
