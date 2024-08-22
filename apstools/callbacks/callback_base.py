"""
Base Class for File Writer Callbacks
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~FileWriterCallbackBase
"""


import datetime
import logging
import pathlib

import pyRestTable

logger = logging.getLogger(__name__)


class FileWriterCallbackBase:
    """
    Base class for filewriter callbacks.

    .. index:: Bluesky Callback; FileWriterCallbackBase

    New with apstools release 1.3.0.

    Applications should subclass and rewrite the ``writer()`` method.

    The local buffers are cleared when a start document is received.
    Content is collected here from each document until the stop document.
    The content is written once the stop document is received.


    User Interface methods

    .. autosummary::

       ~receiver

    Internal methods

    .. autosummary::

       ~clear
       ~make_file_name
       ~writer

    Document Handler methods

    .. autosummary::

       ~bulk_events
       ~datum
       ~descriptor
       ~event
       ~resource
       ~start
       ~stop
    """

    file_extension = "dat"
    _file_name = None
    _file_path = None

    # convention: methods written in alphabetical order

    def __init__(self, *args, **kwargs):
        """Initialize: clear and reset."""
        self.clear()
        self.xref = dict(
            bulk_events=self.bulk_events,
            datum=self.datum,
            descriptor=self.descriptor,
            event=self.event,
            resource=self.resource,
            start=self.start,
            stop=self.stop,
        )

    def receiver(self, key, doc):
        """
        bluesky callback (handles a stream of documents)

        .. index:: Bluesky Callback; FileWriterCallbackBase.receiver
        """
        handler = self.xref.get(key)
        if handler is None:
            logger.error("unexpected key %s" % key)
        else:
            ts = doc.get("time")
            if ts is not None:
                self.doc_timestamp = ts
            handler(doc)

        # - - - - - - - - - - - - - - -

    def clear(self):
        """
        delete any saved data from the cache and reinitialize
        """
        self.acquisitions = {}
        self.detectors = []
        self.exit_status = None
        self.externals = {}
        self.doc_timestamp = None
        self.metadata = {}
        self.plan_name = None
        self.positioners = []
        self.scanning = False
        self.scan_id = None
        self.streams = {}
        self.start_time = None
        self.stop_reason = None
        self.stop_time = None
        self.uid = None

    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, value):
        self._file_name = pathlib.Path(value)

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, value):
        self._file_path = pathlib.Path(value)

    def make_file_name(self):
        """
        generate a file name to be used as default

        default format: {ymd}-{hms}-S{scan_id}-{short_uid}.{ext}
        where the time (the run start time):

        * ymd = {year:4d}{month:02d}{day:02d}
        * hms = {hour:02d}{minute:02d}{second:02d}

        override in subclass to change
        """
        start_time = datetime.datetime.fromtimestamp(self.start_time)
        # fmt: off
        fname = (
            f"{start_time.strftime('%Y%m%d-%H%M%S')}"
            f"-S{self.scan_id:05d}"
            f"-{self.uid[:7]}.{self.file_extension}"
        )
        # fmt: on
        path = self.file_path or pathlib.Path(".")
        return path / fname

    def writer(self):
        """
        print summary of run as diagnostic

        override this method in subclass to write a file
        """
        # logger.debug("acquisitions: %s", yaml.dump(self.acquisitions))

        fname = self.file_name or self.make_file_name()
        print("print to console")
        print(f"suggested file name: {fname}")  # lgtm [py/clear-text-logging-sensitive-data]

        tbl = pyRestTable.Table()
        tbl.labels = "key value".split()
        keys = "plan_name scan_id exit_status start_time stop_reason stop_time uid".split()
        for k in sorted(keys):
            tbl.addRow((k, getattr(self, k)))
        print(tbl)

        def trim(value, length=60):
            text = str(value)
            if len(text) > length:
                text = text[: length - 3] + "..."
            return text

        tbl = pyRestTable.Table()
        tbl.labels = "metadata_key value".split()
        for k, v in sorted(self.metadata.items()):
            tbl.addRow((k, trim(v)))
        print(tbl)

        tbl = pyRestTable.Table()
        tbl.labels = "stream num_vars num_values".split()
        for k, v in sorted(self.streams.items()):
            if len(v) != 1:
                print(f"expecting only one descriptor in stream {k}, found {len(v)}")
            else:
                data = self.acquisitions[v[0]]["data"]
                num_vars = len(data)
                # get the key (symbol) of first data object
                symbol = list(data.keys())[0]
                if num_vars == 0:
                    num_values = 0
                else:
                    num_values = len(data[symbol]["data"])
                tbl.addRow((k, num_vars, num_values))
        print(tbl)

        tbl = pyRestTable.Table()
        tbl.labels = "external_key type value".split()
        for k, v in self.externals.items():
            tbl.addRow((k, v["_document_type_"], trim(v)))
        print(tbl)

        print(f"elapsed scan time: {self.stop_time-self.start_time:.3f}s")

    # - - - - - - - - - - - - - - -

    def bulk_events(self, doc):
        """Deprecated. Use EventPage instead."""
        if not self.scanning:
            return
        logger.info("not handled yet")
        logger.info(doc)
        logger.info("-" * 40)

    def datum(self, doc):
        """
        Like an event, but for data recorded outside of bluesky.

        Example::

            Datum
            =====
            datum_id        : 621caa0f-70f1-4e3d-8718-b5123d434502/0
            datum_kwargs    :
            HDF5_file_name  : /mnt/usaxscontrol/USAXS_data/2020-06/06_10_Minjee_waxs/AGIX3N1_0699.hdf
            point_number    : 0
            resource        : 621caa0f-70f1-4e3d-8718-b5123d434502
        """
        if not self.scanning:
            return
        # stash the whole thing (sort this out in the writer)
        ext = self.externals[doc["datum_id"]] = dict(doc)
        ext["_document_type_"] = "datum"

    def descriptor(self, doc):
        """
        description of the data stream to be acquired
        """
        if not self.scanning:
            return
        stream = doc["name"]
        uid = doc["uid"]

        if stream not in self.streams:
            self.streams[stream] = []
        self.streams[stream].append(uid)

        if uid not in self.acquisitions:
            self.acquisitions[uid] = dict(stream=stream, data={})
        data = self.acquisitions[uid]["data"]
        for k, entry in doc["data_keys"].items():
            # logger.debug("entry %s: %s", k, entry)
            dd = data[k] = {}
            dd["source"] = entry.get("source", "local")
            dd["dtype"] = entry.get("dtype", "")
            dd["shape"] = entry.get("shape", [])
            dd["units"] = entry.get("units", "")
            dd["lower_ctrl_limit"] = entry.get("lower_ctrl_limit", "")
            dd["upper_ctrl_limit"] = entry.get("upper_ctrl_limit", "")
            dd["precision"] = entry.get("precision", 0)
            dd["object_name"] = entry.get("object_name", k)
            dd["data"] = []  # entry data goes here
            dd["time"] = []  # entry time stamps here
            dd["external"] = entry.get("external") is not None
            # logger.debug("dd %s: %s", k, data[k])

    def event(self, doc):
        """
        a single "row" of data
        """
        if not self.scanning:
            return
        # uid = doc["uid"]
        descriptor_uid = doc["descriptor"]
        # seq_num = doc["seq_num"]

        # gather the data by streams
        descriptor = self.acquisitions.get(descriptor_uid)
        if descriptor is not None:
            for k, v in doc["data"].items():
                data = descriptor["data"].get(k)
                if data is None:
                    print(f"entry key {k} not found in descriptor of {descriptor['stream']}")
                else:
                    data["data"].append(v)
                    data["time"].append(doc["timestamps"][k])

    def resource(self, doc):
        """
        like a descriptor, but for data recorded outside of bluesky
        """
        if not self.scanning:
            return
        # stash the whole thing (sort this out in the writer)
        ext = self.externals[doc["uid"]] = dict(doc)
        ext["_document_type_"] = "resource"

    def start(self, doc):
        """
        beginning of a run, clear cache and collect metadata
        """
        self.clear()
        self.plan_name = doc["plan_name"]
        self.scanning = True
        self.scan_id = doc["scan_id"] or 0
        self.start_time = doc["time"]
        self.uid = doc["uid"]
        self.detectors = doc.get("detectors", [])
        self.positioners = doc.get("positioners") or doc.get("motors") or []

        # gather the metadata
        for k, v in doc.items():
            if k in "scan_id time uid".split():
                continue
            self.metadata[k] = v

    def stop(self, doc):
        """
        end of the run, end collection and initiate the ``writer()`` method
        """
        if not self.scanning:
            return
        self.exit_status = doc["exit_status"]
        self.stop_reason = doc.get("reason", "not available")
        self.stop_time = doc["time"]
        self.scanning = False

        self.writer()


# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2024, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
