
"""
Support for streams of bluesky/databroker documents

.. autosummary::
   
   ~json_export
   ~json_import
   ~replay
"""

__all__ = """
    json_export
    json_import
    replay
""".split()

import logging
logger = logging.getLogger(__name__)

from bluesky.callbacks.best_effort import BestEffortCallback
import databroker
from event_model import NumpyEncoder
from ..filewriters import _rebuild_scan_command
import json
from .shell import ipython_profile_name, ipython_shell_namespace
import zipfile


def json_export(headers, filename, zipfilename=None):
    """
    write a list of headers (from databroker) to a file

    PARAMETERS

    headers : list(headers) or `databroker._core.Results` object
        list of databroker headers as returned from `db(...search criteria...)`
    filename : str
        name of file into which to write JSON
    zipfilename : str or None
        name of ZIP file container of `filename` 
        (if None, do not ZIP `filename`)
        
        .. note::  If writing to a ZIP file, the data file is
           *only* written into the ZIP file.
    
    EXAMPLE::

        from databroker import Broker
        db = Broker.named("mongodb_config")
        headers = db(plan_name="count", since="2019-04-01")

        json_export(
            headers, 
            "data.json", 
            zipfilename="bluesky_data.zip")
    
    EXAMPLE: READ THE ZIP FILE:
    
     using :meth:`~json_import`::

        datasets = json_import("data.json", zipfilename="bluesky_data.zip")
    
    EXAMPLE: READ THE JSON TEXT FILE
    
    using :meth:`~json_import`::

        datasets = json_import("data.json)

    """
    datasets = [list(h.documents()) for h in headers]
    buf = json.dumps(datasets, cls=NumpyEncoder, indent=2)

    if zipfilename is None:
        with open(filename, "w") as fp:
            fp.write(buf)
    else:
        with zipfile.ZipFile(zipfilename, "w", allowZip64=True) as fp:
            fp.writestr(filename, buf, compress_type=zipfile.ZIP_LZMA)
                

def json_import(filename, zipfilename=None):
    """
    read the file exported by :meth:`~json_export()`
    
    RETURNS

    datasets : list of documents
        list of 
        `documents <https://blueskyproject.io/bluesky/documents.html/>`_,
        such as returned by
        `[list(h.documents()) for h in db]`
        
        See:
        https://blueskyproject.io/databroker/generated/databroker.Header.documents.html
    
    EXAMPLE
    
    Insert the datasets into the databroker ``db``::
    
        def insert_docs(db, datasets):
            for i, h in enumerate(datasets):
                print(f"{i+1}/{len(datasets)} : {len(h)} documents")
                for k, doc in h:
                    db.insert(k, doc)
    
    """
    if zipfilename is None:
        with open(filename, "r") as fp:
            buf = fp.read()
            datasets = json.loads(buf)
    else:
        with zipfile.ZipFile(zipfilename, "r") as fp:
            buf = fp.read(filename).decode("utf-8")
            datasets = json.loads(buf)
    
    return datasets


def replay(headers, callback=None, sort=True):
    """
    replay the document stream from one (or more) scans (headers)
    
    PARAMETERS
    
    headers: scan or [scan]
        Scan(s) to be replayed through callback.
        A *scan* is an instance of a Bluesky `databroker.Header`.
        see: https://nsls-ii.github.io/databroker/api.html?highlight=header#header-api
    
    callback: scan or [scan]
        The Bluesky callback to handle the stream of documents from a scan.
        If `None`, then use the `bec` (BestEffortCallback) from the IPython shell.
        (default:``None``)
    
    sort: bool
        Sort the headers chronologically if True.
        (default:``True``)

    *new in apstools release 1.1.11*
    """
    callback = callback or ipython_shell_namespace().get(
        "bec",                  # get from IPython shell
        BestEffortCallback(),   # make one, if we must
        )
    _headers = headers   # do not mutate the input arg
    if isinstance(_headers, databroker.Header):
        _headers = [_headers]

    def time_sorter(run):    # by increasing time
        return run.start["time"]

    sequence = list(_headers)    # for sequence_sorter
    def sequence_sorter(run):    # by sequence as-given
        v = sequence.index(run)
        return v
    
    sorter = {True: time_sorter, False: sequence_sorter}[sort]

    for h in sorted(_headers, key=sorter):
        if not isinstance(h, databroker.Header):
            emsg = f"Must be a databroker Header: received: {type(h)}: |{h}|"
            raise TypeError(emsg)
        cmd = _rebuild_scan_command(h.start)
        logger.debug(f"{cmd}")
        
        # at last, this is where the real action happens
        for k, doc in h.documents():    # get the stream
            callback(k, doc)            # play it through the callback
