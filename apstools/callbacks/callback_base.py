"""
Base Class for File Writer Callbacks
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~FileWriterCallbackBase
"""

import datetime
import logging
from typing import Any, Dict, List, Optional, Union

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
       ~get_hklpy_configurations
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

    file_extension: str = "dat"
    _file_name: Optional[Union[pathlib.Path, str]] = None  # TODO: CHECK TESTS
    _file_path: Optional[Union[pathlib.Path, str]] = None  # TODO: CHECK TESTS

    # convention: methods written in alphabetical order

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize: clear and reset."""
        self.clear()
        self.xref: Dict[str, Any] = dict(
            bulk_events=self.bulk_events,
            datum=self.datum,
            descriptor=self.descriptor,
            event=self.event,
            resource=self.resource,
            start=self.start,
            stop=self.stop,
        )

    def receiver(self, key: str, doc: Dict[str, Any]) -> None:
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

    def clear(self) -> None:
        """
        delete any saved data from the cache and reinitialize
        """
        self.acquisitions: Dict[str, Any] = {}
        self.detectors: List[str] = []
        self.diffractometers: Dict[str, Any] = {}
        self.exit_status: Optional[str] = None
        self.externals: Dict[str, Any] = {}
        self.doc_timestamp: Optional[float] = None
        self.metadata: Dict[str, Any] = {}
        self.plan_name: Optional[str] = None
        self.positioners: List[str] = []
        self.scanning: bool = False
        self.scan_id: Optional[int] = None
        self.streams: Dict[str, List[str]] = {}
        self.start_time: Optional[float] = None
        self.stop_reason: Optional[str] = None
        self.stop_time: Optional[float] = None
        self.uid: Optional[str] = None

    @property
    def file_name(self) -> Optional[pathlib.Path]:
        return self._file_name

    @file_name.setter
    def file_name(self, value: Union[str, pathlib.Path]) -> None:
        self._file_name = pathlib.Path(value)

    @property
    def file_path(self) -> Optional[pathlib.Path]:
        return self._file_path

    @file_path.setter
    def file_path(self, value: Union[str, pathlib.Path]) -> None:
        self._file_path = pathlib.Path(value)

    def get_hklpy_configurations(self, doc: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Diffractometer details (from hklpy) in RE descriptor documents."""
        configurations: Dict[str, Dict[str, Any]] = {}  # zero, one, or more diffractometers are possible
        for diffractometer_name in doc.get("configuration", {}):
            record = doc["configuration"][diffractometer_name].get("data", {})
            attrs = record.get(f"{diffractometer_name}_orientation_attrs")
            if attrs is not None:
                configurations[diffractometer_name] = {
                    # empty when no orientation_attrs
                    attr: record[f"{diffractometer_name}_{attr}"]
                    for attr in attrs
                }
        return configurations

    def make_file_name(self) -> pathlib.Path:
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

    def writer(self) -> None:
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

        def trim(value: Any, length: int = 60) -> str:
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

    def bulk_events(self, doc: Dict[str, Any]) -> None:
        """Deprecated. Use EventPage instead."""
        if not self.scanning:
            return
        logger.info("not handled yet")
        logger.info(doc)
        logger.info("-" * 40)

    def datum(self, doc: Dict[str, Any]) -> None:
        """
        Like an event, but for data recorded outside of bluesky.

        Example::

            Datum
            =====
            datum_id        : 621caa0f-70f1-4e3d-8718-b5123d434502/0
            datum_kwargs    :
            HDF5_file_name  : /mnt/usaxscontrol/USAXS_data/2020-06/06_10_Minjee_waxs/AGIX3N1_0699.hdf
            point_number    : 0
        """
        if not self.scanning:
            return
        logger.info("datum document")
        logger.info(doc)
        logger.info("-" * 40)

    def descriptor(self, doc: Dict[str, Any]) -> None:
        """
        Process a descriptor document.

        Example::

            Descriptor
            =========
            configuration  : {}
            data_keys     : {}
            hints        : {}
            name         : primary
            object_keys  : {}
            run_metadata : {}
            time         : 1621451234.123456
            uid          : 621caa0f-70f1-4e3d-8718-b5123d434502
        """
        if not self.scanning:
            return
        logger.info("descriptor document")
        logger.info(doc)
        logger.info("-" * 40)

    def event(self, doc: Dict[str, Any]) -> None:
        """
        Process an event document.

        Example::

            Event
            =====
            data         : {}
            descriptor   : 621caa0f-70f1-4e3d-8718-b5123d434502
            filled       : {}
            seq_num      : 1
            time         : 1621451234.123456
            uid          : 621caa0f-70f1-4e3d-8718-b5123d434502/1
        """
        if not self.scanning:
            return
        logger.info("event document")
        logger.info(doc)
        logger.info("-" * 40)

    def resource(self, doc: Dict[str, Any]) -> None:
        """
        Process a resource document.

        Example::

            Resource
            ========
            path_semantics : posix
            resource_kwargs : {}
            resource_path   : /mnt/usaxscontrol/USAXS_data/2020-06/06_10_Minjee_waxs/AGIX3N1_0699.hdf
            root           : /mnt/usaxscontrol/USAXS_data
            run_start      : 621caa0f-70f1-4e3d-8718-b5123d434502
            spec           : AD_HDF5
            uid            : 621caa0f-70f1-4e3d-8718-b5123d434502/0
        """
        if not self.scanning:
            return
        logger.info("resource document")
        logger.info(doc)
        logger.info("-" * 40)

    def start(self, doc: Dict[str, Any]) -> None:
        """
        Process a start document.

        Example::

            Start
            =====
            plan_args     : {}
            plan_name     : count
            scan_id       : 1
            time          : 1621451234.123456
            uid           : 621caa0f-70f1-4e3d-8718-b5123d434502
        """
        self.scanning = True
        self.start_time = doc.get("time")
        self.scan_id = doc.get("scan_id")
        self.uid = doc.get("uid")
        self.plan_name = doc.get("plan_name")
        self.metadata = doc.get("run_metadata", {})
        logger.info("start document")
        logger.info(doc)
        logger.info("-" * 40)

    def stop(self, doc: Dict[str, Any]) -> None:
        """
        Process a stop document.

        Example::

            Stop
            ====
            exit_status   : success
            num_events    : {}
            reason        : None
            run_start     : 621caa0f-70f1-4e3d-8718-b5123d434502
            time          : 1621451234.123456
            uid           : 621caa0f-70f1-4e3d-8718-b5123d434502
        """
        self.scanning = False
        self.stop_time = doc.get("time")
        self.exit_status = doc.get("exit_status")
        self.stop_reason = doc.get("reason")
        logger.info("stop document")
        logger.info(doc)
        logger.info("-" * 40)
        self.writer()


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
