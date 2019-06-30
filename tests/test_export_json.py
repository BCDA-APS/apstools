
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

from apstools.utils import json_export, json_import


TEST_JSON_FILE = "data.json"
TEST_ZIP_FILE = os.path.join(_test_path, "bluesky_data.zip")


def get_db():
    from databroker import Broker, temp_config
    conf = temp_config()
    conf["metadatastore"]["config"]["timezone"] = "US/Central"
    db = Broker.from_config(conf)
    datasets = json_import(TEST_JSON_FILE, TEST_ZIP_FILE)
    insert_docs(db, datasets)
    return db


def insert_docs(db, datasets, verbose=False):
    for i, h in enumerate(datasets):
        if verbose:
            print(f"{i+1}/{len(datasets)} : {len(h)} documents")
        for k, doc in h:
            db.insert(k, doc)


class Test_JsonExport(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir, ignore_errors=True)
    
    def test_export_import(self):
        db = get_db()
        headers = db(plan_name="count")
        headers = list(headers)[0:1]

        filename = os.path.join(self.tempdir, "export1.txt")
        json_export(headers, filename=filename)
        self.assertTrue(os.path.exists(filename), f"wrote to requested {filename}")

        testdata = json_import(filename)
        self.assertEqual(len(testdata), 1, "file contains one dataset")
        dataset = testdata[0]
        self.assertGreater(len(dataset), 1, "dataset contains more than one document")
        tag, doc = dataset[0]
        self.assertEqual(tag, "start", "found start document")
        self.assertNotEqual(doc.get("plan_name"), None, "found a start document by duck type")
        self.assertNotEqual(doc.get("uid"), None, "found a uid document")
        self.assertEqual(
            doc["uid"],
            headers[0].start["uid"],
            "found matching start document"
            )
    
    def test_export_import_zip(self):
        db = get_db()
        headers = db(plan_name="count")
        headers = list(headers)[0:1]
        
        filename = "export2.txt"
        zipfilename = os.path.join(self.tempdir, "export2.zip")
        json_export(headers, filename, zipfilename=zipfilename)
        self.assertFalse(os.path.exists(filename), f"did not write to {filename}")
        self.assertTrue(
            os.path.exists(zipfilename), 
            f"wrote to requested ZIP {zipfilename}")
        with zipfile.ZipFile(zipfilename, "r") as fp:
            self.assertIn(filename, fp.namelist(), "found JSON test data")

        testdata = json_import(filename, zipfilename)
        self.assertEqual(len(testdata), 1, "file contains one dataset")
        dataset = testdata[0]
        self.assertGreater(len(dataset), 1, "dataset contains more than one document")
        tag, doc = dataset[0]
        self.assertEqual(tag, "start", "found start document")
        self.assertNotEqual(doc.get("plan_name"), None, "found a start document by duck type")
        self.assertNotEqual(doc.get("uid"), None, "found a uid document")
        self.assertEqual(
            doc["uid"],
            headers[0].start["uid"],
            "found matching start document"
            )


def suite(*args, **kw):
    test_list = [
        Test_JsonExport,
        ]

    test_suite = unittest.TestSuite()
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == "__main__":
    runner=unittest.TextTestRunner()
    runner.run(suite())
