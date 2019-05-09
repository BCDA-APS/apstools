
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


"""
sqlite fails with this error:

  File "/home/mintadmin/Apps/anaconda/envs/bluesky/lib/python3.6/site-packages/databroker/headersource/sqlite.py", line 257, in _insert_events
    values[desc_uid])
sqlite3.InterfaceError: Error binding parameter 107 - probably unsupported type.

Can we pick a different backend for temporary work?
"""

DOCS_FILE = os.path.join(_test_path, "docs_tune_mr.json")


def get_broker_sqlite_config(path, tz=None):
    """
    get a temporary sqlite directory configuration
    
    path = "/tmp"
    config_tmp_sqlite = get_broker_sqlite_config(path)
    self.db = Broker.from_config(config_tmp_sqlite)
    """
    
    tz = tz or "US/Central"
    assets_dir = path       # FIXME:
    config = {
         'description': 'lightweight personal database',
         'metadatastore': {
             'module': 'databroker.headersource.sqlite',
             'class': 'MDS',
             'config': {
                 'directory': path,
                 'timezone': tz}
         },
         'assets': {
             'module': 'databroker.assets.sqlite',
             'class': 'Registry',
             'config': {
                 'dbpath': os.path.join(path, '/assets.sqlite')}
         }
     }
    return config


class Test_Something(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        config_tmp_sqlite = get_broker_sqlite_config(self.tempdir)
        self.db = Broker.from_config(config_tmp_sqlite)

    def tearDown(self):
        if os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir, ignore_errors=True)
    
    def test_newfile(self):
        self.assertTrue(os.path.exists(DOCS_FILE))
        
        # load the db with our test document stream
        with open(DOCS_FILE, "r") as fp:
            plans = json.load(fp)
            for document in plans["tune_mr"]:
                tag, doc = document
                print(tag)
                self.db.insert(tag, doc)    # FIXME: fails here
        
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
