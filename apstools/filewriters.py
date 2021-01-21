"""
Bluesky callbacks for writing files (such as for SPEC or NeXus).

The filewriter callbacks here are written as classes since they
cache information while collecting data and preserve information
about the state of the document sequence.

.. autosummary::

   ~FileWriterCallbackBase
   ~NXWriterAPS
   ~NXWriter
   ~SpecWriterCallback
   ~spec_comment
"""

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2021, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------


from collections import OrderedDict
import datetime
import getpass
import h5py
import logging
import numpy as np
import os
import pyRestTable
import socket
import time
import yaml


logger = logging.getLogger(__name__)


NEXUS_FILE_EXTENSION = "hdf"  # use this file extension for the output
NEXUS_RELEASE = "v2020.1"  # NeXus release to which this file is written
SPEC_TIME_FORMAT = "%a %b %d %H:%M:%S %Y"
SCAN_ID_RESET_VALUE = 0


def _rebuild_scan_command(doc):
    """
    reconstruct the scan command for SPEC data file #S line

    PARAMETERS

    doc
        *object* :
        instance of a bluesky ``start`` document

    RETURNS

    *str* :
        "scan_number reconstructed_scan_command"
    """

    def get_name(src):
        """
        get name field from object representation

        given: EpicsMotor(prefix='xxx:m1', name='m1', settle_time=0.0,
                    timeout=None, read_attrs=['user_readback', 'user_setpoint'],
                    configuration_attrs=['motor_egu', 'velocity', 'acceleration',
                    'user_offset', 'user_offset_dir'])
        return: "m1"
        """
        s = str(src)
        p = s.find("(")
        if p > 0:  # only if an open parenthesis is found
            # fmt: offf
            # fmt: on
            parts = s[p + 1:].rstrip(")").split(",")
            for item in parts:
                # should be key=value pairs
                item = item.strip()
                p = item.find("=")
                if item[:p] == "name":
                    # fmt: off
                    # fmt: on
                    s = item[p + 1:]  # get the name value
                    break
        return s

    def struct_to_str(struct):
        """Convert given structure into string representation."""
        if isinstance(struct, list):
            return (
                "[" + ", ".join([struct_to_str(v) for v in struct]) + "]"
            )
        elif isinstance(struct, dict):
            return (
                "{"
                + ", ".join(
                    [f"{k}={struct_to_str(v)}" for k, v in struct.items()]
                )
                + "}"
            )
        elif isinstance(struct, np.ndarray):
            return struct_to_str(list(struct))
        elif isinstance(struct, str):
            # escape embedded characters, such as single quote
            return f"'{struct}'".encode("unicode_escape").decode("utf8")
        else:
            return str(struct)

    s = []
    if "plan_args" in doc:
        for _k, _v in doc["plan_args"].items():
            if _k == "detectors":
                _v = doc[_k]
            elif _k.startswith("motor"):
                _v = doc["motors"]
            elif _k == "args":
                _v = "[" + ", ".join(map(get_name, _v)) + "]"
            s.append(f"{_k}={struct_to_str(_v)}")

    cmd = "{}({})".format(doc.get("plan_name", ""), ", ".join(s))
    scan_id = doc.get("scan_id") or 1
    return f"{scan_id}  {cmd}"


# TODO: consider refactor to use FileWriterCallbackBase()
class SpecWriterCallback(object):
    """
    Collect data from Bluesky RunEngine documents to write as SPEC data.

    .. index:: Bluesky Callback; SpecWriterCallback

    This gathers data from all documents in a scan and appends scan to the file
    when the ``stop`` document is received.  One or more scans can be written to
    the same file.  The file format is text.

    .. note:: ``SpecWriterCallback()`` does **not** inherit
       from ``FileWriterCallbackBase()``.

    PARAMETERS

    filename
        *string* :
        (optional)
        Local, relative or absolute name of SPEC data file to be used.
        If ``filename=None``, defaults to format of ``YYYmmdd-HHMMSS.dat``
        derived from the current system time.

    auto_write
        *boolean* :
        (optional)
        If ``True`` (default), ``write_scan()`` is called when *stop* document
        is received.
        If ``False``, the caller is responsible for calling ``write_scan()``
        before the next ``start`` document is received.

    RE
        *object* :
        Instance of ``bluesky.RunEngine`` or ``None``.

    reset_scan_id
        *boolean* :
        (optional)
        If True, and filename exists, then sets ``RE.md.scan_id`` to
        highest scan number in existing SPEC data file.
        default: False

    User Interface methods

    .. autosummary::

       ~receiver
       ~newfile
       ~usefile
       ~make_default_filename
       ~clear
       ~prepare_scan_contents
       ~write_scan

    Internal methods

    .. autosummary::

       ~write_header
       ~start
       ~descriptor
       ~event
       ~bulk_events
       ~datum
       ~resource
       ~stop
    """

    # EXAMPLE : the :ref:`specfile_example() <example_specfile>`
    # writes one or more scans to a SPEC data file using a jupyter notebook.

    def __init__(
        self, filename=None, auto_write=True, RE=None, reset_scan_id=False
    ):
        self.clear()
        self.buffered_comments = self._empty_comments_dict()
        self.spec_filename = filename
        self.auto_write = auto_write
        self.uid_short_length = 8
        self.write_file_header = False
        self.spec_epoch = None  # for both #E & #D line in header, also offset for all scans
        self.spec_host = None
        self.spec_user = None
        self._datetime = None  # most recent document time
        self._streams = {}  # descriptor documents, keyed by uid
        self.RE = RE

        if reset_scan_id is True:
            reset_scan_id = SCAN_ID_RESET_VALUE
        self.reset_scan_id = reset_scan_id

        if filename is None or not os.path.exists(filename):
            self.newfile(filename)
        else:
            max_scan_id = self.usefile(filename)
            if RE is not None and reset_scan_id is not False:
                RE.md["scan_id"] = max_scan_id

    def clear(self):
        """reset all scan data defaults"""
        self.uid = None
        self.scan_epoch = None  # absolute epoch to report in scan #D line
        self.time = None  # full time from document
        self.comments = self._empty_comments_dict()
        self.data = OrderedDict()  # data in the scan
        self.detectors = OrderedDict()  # names of detectors in the scan
        self.hints = OrderedDict()  # why?
        self.metadata = OrderedDict()  # #MD lines in header
        self.motors = OrderedDict()  # names of motors in the scan
        self.positioners = OrderedDict()  # names in #O, values in #P
        self.num_primary_data = 0
        #
        # note: for one scan, #O & #P information is not provided
        # unless collecting baseline data
        # wait for case with baseline data that needs #O/#P lines
        #
        self.columns = OrderedDict()  # #L in scan
        self.scan_command = None  # #S line
        self.scanning = False

    def _empty_comments_dict(self):
        return dict(
            start=[],
            event=[],
            descriptor=[],
            resource=[],
            datum=[],
            stop=[],
        )

    def _cmt(self, key, text):
        """enter a comment"""
        dt = self._datetime or datetime.datetime.now()
        ts = datetime.datetime.strftime(dt, SPEC_TIME_FORMAT)
        if self.scanning:
            dest = self.comments
        else:
            dest = self.buffered_comments
        dest[key].append(f"{ts}.  {text}")

    def receiver(self, key, document):
        """
        Bluesky callback: receive all documents for handling

        .. index:: Bluesky Callback; SpecWriterCallback.receiver
        """
        xref = dict(
            start=self.start,
            descriptor=self.descriptor,
            event=self.event,
            bulk_events=self.bulk_events,
            datum=self.datum,
            resource=self.resource,
            stop=self.stop,
        )
        logger = logging.getLogger(__name__)
        if key in xref:
            uid = document.get("uid") or document.get("datum_id")
            logger.debug("%s document, uid=%s", key, str(uid))
            ts = document.get("time")
            if ts is None:
                ts = datetime.datetime.now()
            else:
                ts = datetime.datetime.fromtimestamp(document["time"])
            self._datetime = ts
            xref[key](document)
        else:
            msg = f"custom_callback encountered: {key} : {document}"
            # raise ValueError(msg)
            logger.warning(msg)

    def start(self, doc):
        """handle *start* documents"""

        known_properties = """
            uid time project sample scan_id group owner
            hints
            plan_type plan_name plan_args
        """.split()

        self.clear()
        self.scanning = True
        self.uid = doc["uid"]

        self._cmt("start", f"uid = {self.uid}")
        self.metadata["uid"] = f"{self.uid}"
        for d, cl in self.buffered_comments.items():
            # bring in any comments collected when not scanning
            self.comments[d] += cl
        self.buffered_comments = self._empty_comments_dict()

        self.time = doc["time"]
        self.scan_epoch = int(self.time)
        self.scan_id = doc["scan_id"] or 0
        # Which reference? fixed counting time or fixed monitor count?
        # Can this be omitted?
        self.T_or_M = None  # for now
        # self.T_or_M = "T"           # TODO: how to get this from the document stream?
        # self.T_or_M_value = 1
        # self._cmt("start", "!!! #T line not correct yet !!!")

        # metadata
        for key in sorted(doc.keys()):
            if key not in known_properties:
                self.metadata[key] = doc[key]

        self.start_hints = doc.get("hints", {})

        # various dicts
        for item in "detectors hints motors".split():
            if item in doc:
                obj = self.__getattribute__(item)
                for key in doc.get(item):
                    obj[key] = None

        cmt = "plan_type = " + doc["plan_type"]
        ts = datetime.datetime.strftime(self._datetime, SPEC_TIME_FORMAT)
        self.comments["start"].insert(0, f"{ts}.  {cmt}")
        self.scan_command = _rebuild_scan_command(doc)

    def descriptor(self, doc):
        """
        handle *descriptor* documents

        prepare for primary scan data, ignore any other data stream
        """
        if doc["uid"] in self._streams:
            fmt = "duplicate descriptor UID {} found"
            raise KeyError(fmt.format(doc["uid"]))

        # log descriptor documents by uid
        # referenced by event and bulk_events documents
        self._streams[doc["uid"]] = doc

        if doc["name"] != "primary":
            return

        keyset = list(doc["data_keys"].keys())
        doc_hints_names = []
        for k, d in doc["hints"].items():
            doc_hints_names.append(k)
            doc_hints_names += d["fields"]

        # independent variable(s) first
        # assumes start["motors"] was defined
        first_keys = [k for k in self.motors if k in keyset]
        # TODO: if len(first_keys) == 0: look at self.start_hints

        # dependent variable(s) last
        # assumes start["detectors"] was defined
        last_keys = [d for d in self.detectors if d in doc_hints_names]
        # TODO: if len(last_keys) == 0: look at doc["hints"]

        # get remaining keys from keyset, they go in the middle
        middle_keys = [
            k for k in keyset if k not in first_keys + last_keys
        ]
        epoch_keys = "Epoch_float Epoch".split()

        self.data.update(
            {
                k: []
                for k in first_keys + epoch_keys + middle_keys + last_keys
            }
        )

    def event(self, doc):
        """
        handle *event* documents
        """
        stream_doc = self._streams.get(doc["descriptor"])
        if stream_doc is None:
            fmt = "descriptor UID {} not found"
            raise KeyError(fmt.format(doc["descriptor"]))
        if stream_doc["name"] == "primary":
            for k in doc["data"].keys():
                if k not in self.data.keys():
                    msg = f"unexpected failure here, key {k} not found"
                    raise KeyError(msg)
            for k in self.data.keys():
                if k == "Epoch":
                    v = int(doc["time"] - self.time + 0.5)
                elif k == "Epoch_float":
                    v = doc["time"] - self.time
                else:
                    # like SPEC, default to 0 if not found by name
                    v = doc["data"].get(k, 0)
                self.data[k].append(v)
            self.num_primary_data += 1

    def bulk_events(self, doc):
        """handle *bulk_events* documents"""
        pass

    def datum(self, doc):
        """handle *datum* documents"""
        self._cmt("datum", "datum " + str(doc))

    def resource(self, doc):
        """handle *resource* documents"""
        self._cmt("resource", "resource " + str(doc))

    def stop(self, doc):
        """handle *stop* documents"""
        if "num_events" in doc:
            for k, v in doc["num_events"].items():
                self._cmt("stop", f"num_events_{k} = {v}")
        if "exit_status" in doc:
            self._cmt("stop", "exit_status = " + doc["exit_status"])
        else:
            self._cmt("stop", "exit_status = not available")

        if self.auto_write:
            self.write_scan()

        self.scanning = False

    def prepare_scan_contents(self):
        """
        format the scan for a SPEC data file

        :returns: [str] a list of lines to append to the data file
        """
        dt = datetime.datetime.fromtimestamp(self.scan_epoch)
        lines = []
        lines.append("")
        lines.append("#S " + self.scan_command)
        lines.append(
            "#D " + datetime.datetime.strftime(dt, SPEC_TIME_FORMAT)
        )
        if self.T_or_M is not None:
            lines.append(f"#{self.T_or_M} {self.T_or_M_value}")

        for v in self.comments["start"]:
            # C Wed Feb 03 16:51:38 2016.  do ./usaxs.mac.
            lines.append(
                "#C " + v
            )  # TODO: add time/date stamp as SPEC does
        for v in self.comments["descriptor"]:
            lines.append("#C " + v)

        for k, v in self.metadata.items():
            # "#MD" is our ad hoc SPEC data tag
            lines.append(f"#MD {k} = {v}")

        lines.append("#P0 ")

        lines.append("#N " + str(len(self.data.keys())))
        if len(self.data.keys()) > 0:
            lines.append("#L " + "  ".join(self.data.keys()))
            for i in range(self.num_primary_data):
                str_data = OrderedDict()
                s = []
                for k in self.data.keys():
                    datum = self.data[k][i]
                    if isinstance(datum, str):
                        # SPEC scan data is expected to be numbers
                        # this is text, substitute the row number
                        # and report after this line in a #U line
                        str_data[k] = datum
                        datum = i
                    s.append(str(datum))
                lines.append(" ".join(s))
                for k in str_data.keys():
                    # report the text data
                    lines.append(f"#U {i} {k} {str_data[k]}")
        else:
            lines.append("#C no data column labels identified")

        for v in self.comments["event"]:
            lines.append("#C " + v)

        for v in self.comments["resource"]:
            lines.append("#C " + v)

        for v in self.comments["datum"]:
            lines.append("#C " + v)

        for v in self.comments["stop"]:
            lines.append("#C " + v)

        return lines

    def _write_lines_(self, lines, mode="a"):
        """write (more) lines to the file"""
        with open(self.spec_filename, mode) as f:
            f.write("\n".join(lines))

    def write_header(self):
        """write the header section of a SPEC data file"""
        dt = datetime.datetime.fromtimestamp(self.spec_epoch)
        lines = []
        lines.append(f"#F {self.spec_filename}")
        lines.append(f"#E {self.spec_epoch}")
        lines.append(
            f"#D {datetime.datetime.strftime(dt, SPEC_TIME_FORMAT)}"
        )
        lines.append(
            f"#C Bluesky  user = {self.spec_user}  host = {self.spec_host}"
        )
        lines.append("#O0 ")
        lines.append("#o0 ")
        lines.append("")

        if os.path.exists(self.spec_filename):
            lines.insert(0, "")
        self._write_lines_(lines, mode="a+")
        self.write_file_header = False

    def write_scan(self):
        """
        write the most recent (completed) scan to the file

        * creates file if not existing
        * writes header if needed
        * appends scan data

        note:  does nothing if there are no lines to be written
        """
        if os.path.exists(self.spec_filename):
            with open(self.spec_filename) as f:
                buf = f.read()
                if buf.find(self.uid) >= 0:
                    # raise exception if uid is already in the file!
                    msg = f"{self.spec_filename} already contains uid={self.uid}"
                    raise ValueError(msg)
        logger = logging.getLogger(__name__)
        lines = self.prepare_scan_contents()
        lines.append("")
        if lines is not None:
            if self.write_file_header:
                self.write_header()
                logger.info(
                    "wrote header to SPEC file: %s", self.spec_filename
                )
            self._write_lines_(lines, mode="a")
            logger.info(
                "wrote scan %d to SPEC file: %s",
                self.scan_id,
                self.spec_filename,
            )

    def make_default_filename(self):
        """generate a file name to be used as default"""
        now = datetime.datetime.now()
        return datetime.datetime.strftime(now, "%Y%m%d-%H%M%S") + ".dat"

    def newfile(self, filename=None, scan_id=None, RE=None):
        """
        prepare to use a new SPEC data file

        but don't create it until we have data
        """
        self.clear()
        filename = filename or self.make_default_filename()
        if os.path.exists(filename):
            from spec2nexus.spec import SpecDataFile

            sdf = SpecDataFile(filename)
            scan_list = sdf.getScanNumbers()
            l = len(scan_list)
            m = max(map(float, scan_list))
            highest = int(max(l, m) + 0.9999)  # solves issue #128
            scan_id = max(scan_id or 0, highest)
        self.spec_filename = filename
        self.spec_epoch = int(time.time())  # ! no roundup here!!!
        self.spec_host = socket.gethostname() or "localhost"
        self.spec_user = getpass.getuser() or "BlueskyUser"
        self.write_file_header = True  # don't write the file yet

        # backwards-compatibility
        if isinstance(scan_id, bool):
            # True means reset the scan ID to default
            # False means do not modify it
            scan_id = {True: SCAN_ID_RESET_VALUE, False: None}[scan_id]
        if scan_id is not None and RE is not None:
            # RE is an instance of bluesky.run_engine.RunEngine
            # (or duck type for testing)
            RE.md["scan_id"] = scan_id
            self.scan_id = scan_id
        return self.spec_filename

    def usefile(self, filename):
        """read from existing SPEC data file"""
        if not os.path.exists(self.spec_filename):
            raise IOError(f"file {filename} does not exist")
        scan_id = None
        with open(filename, "r") as f:
            key = "#F"
            line = f.readline().strip()
            if not line.startswith(key + " "):
                raise ValueError(f"first line does not start with {key}")

            key = "#E"
            line = f.readline().strip()
            if not line.startswith(key + " "):
                raise ValueError(f"first line does not start with {key}")
            epoch = int(line.split()[-1])

            key = "#D"
            line = f.readline().strip()
            if not line.startswith(key + " "):
                raise ValueError("first line does not start with " + key)
            # ignore content, it is derived from #E line

            key = "#C"
            line = f.readline().strip()
            if not line.startswith(key + " "):
                raise ValueError("first line does not start with " + key)
            p = line.split()
            username = "BlueskyUser"
            if len(p) > 4 and p[2] == "user":
                username = p[4]

            # find the highest scan number used
            key = "#S"
            scan_ids = []
            for line in f.readlines():
                if line.startswith(key + " ") and len(line.split()) > 1:
                    scan_id = int(line.split()[1])
                    scan_ids.append(scan_id)
            scan_id = max(scan_ids)

        self.spec_filename = filename
        self.spec_epoch = epoch
        self.spec_user = username
        return scan_id


def spec_comment(comment, doc=None, writer=None):
    """
    make it easy to add spec-style comments in a custom plan

    These comments *only* go into the SPEC data file.

    PARAMETERS

    comment
        *string* :
        (optional)
        Comment text to be written.  SPEC expects it to be only one line!

    doc
        *string* :
        (optional)
        Bluesky RunEngine document type.
        One of: ``start descriptor event resource datum stop``
        (default: ``event``)

    writer
        *obj* :
        (optional)
        Instance of ``SpecWriterCallback()``,
        typically: ``specwriter = SpecWriterCallback()``

    EXAMPLE:

    Execution of this plan (with ``RE(myPlan())``)::

        def myPlan():
            yield from bps.open_run()
            spec_comment("this is a start document comment", "start")
            spec_comment("this is a descriptor document comment", "descriptor")
            yield bps.Msg('checkpoint')
            yield from bps.trigger_and_read([scaler])
            spec_comment("this is an event document comment after the first read")
            yield from bps.sleep(2)
            yield bps.Msg('checkpoint')
            yield from bps.trigger_and_read([scaler])
            spec_comment("this is an event document comment after the second read")
            spec_comment("this is a stop document comment", "stop")
            yield from bps.close_run()

    results in this SPEC file output::

        #S 1145  myPlan()
        #D Mon Jan 28 12:48:09 2019
        #C Mon Jan 28 12:48:09 2019.  plan_type = generator
        #C Mon Jan 28 12:48:09 2019.  uid = ef98648a-8e3a-4e7e-ac99-3290c9b5fca7
        #C Mon Jan 28 12:48:09 2019.  this is a start document comment
        #C Mon Jan 28 12:48:09 2019.  this is a descriptor document comment
        #MD APSTOOLS_VERSION = 2019.0103.0+5.g0f4e8b2
        #MD BLUESKY_VERSION = 1.4.1
        #MD OPHYD_VERSION = 1.3.0
        #MD SESSION_START = 2019-01-28 12:19:25.446836
        #MD beamline_id = developer
        #MD ipython_session_start = 2018-02-14 12:54:06.447450
        #MD login_id = mintadmin@mint-vm
        #MD pid = 21784
        #MD proposal_id = None
        #N 2
        #L Epoch_float  scaler_time  Epoch
        1.4297869205474854 1.1 1
        4.596935987472534 1.1 5
        #C Mon Jan 28 12:48:11 2019.  this is an event document comment after the first read
        #C Mon Jan 28 12:48:14 2019.  this is an event document comment after the second read
        #C Mon Jan 28 12:48:14 2019.  this is a stop document comment
        #C Mon Jan 28 12:48:14 2019.  num_events_primary = 2
        #C Mon Jan 28 12:48:14 2019.  exit_status = success

    """
    global specwriter  # such as: specwriter = SpecWriterCallback()
    writer = writer or specwriter
    if doc is None:
        if writer.scanning:
            doc = "event"
        else:
            doc = "start"
    for line in comment.splitlines():
        writer._cmt(doc, line)


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
    file_name = None
    file_path = None

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
        fname = start_time.strftime("%Y%m%d-%H%M%S")
        fname += f"-S{self.scan_id:05d}"
        fname += f"-{self.uid[:7]}.{self.file_extension}"
        path = os.path.abspath(self.file_path or os.getcwd())
        return os.path.join(path, fname)

    def writer(self):
        """
        print summary of run as diagnostic

        override this method in subclass to write a file
        """
        # logger.debug("acquisitions: %s", yaml.dump(self.acquisitions))

        fname = self.file_name or self.make_file_name()
        print("print to console")
        print(f"suggested file name: {fname}")

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
                print(
                    f"expecting only one descriptor in stream {k},"
                    f" found {len(v)}"
                )
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
                    print(
                        f"entry key {k} not found in"
                        f" descriptor of {descriptor['stream']}"
                    )
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
        self.positioners = (
            doc.get("positioners") or doc.get("motors") or []
        )

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


class NXWriter(FileWriterCallbackBase):
    """
    General class for writing HDF5/NeXus file (using only NeXus base classes).

    .. index:: Bluesky Callback; NXWriter

    New with apstools release 1.3.0.

    One scan is written to one HDF5/NeXus file.

    METHODS

    .. autosummary::

       ~writer
       ~h5string
       ~add_dataset_attributes
       ~assign_signal_type
       ~create_NX_group
       ~get_sample_title
       ~get_stream_link
       ~write_data
       ~write_detector
       ~write_entry
       ~write_instrument
       ~write_metadata
       ~write_monochromator
       ~write_positioner
       ~write_root
       ~write_sample
       ~write_slits
       ~write_source
       ~write_streams
       ~write_user
    """

    file_extension = NEXUS_FILE_EXTENSION
    instrument_name = None  # name of this instrument
    # NeXus release to which this file is written
    nexus_release = NEXUS_RELEASE
    nxdata_signal = None  # name of dataset for Y axis on plot
    nxdata_signal_axes = None  # name of dataset for X axis on plot
    root = None  # instance of h5py.File

    # convention: methods written in alphabetical order

    def add_dataset_attributes(self, ds, v, long_name=None):
        """
        add attributes from v dictionary to dataset ds
        """
        ds.attrs["units"] = self.h5string(v["units"])
        ds.attrs["source"] = self.h5string(v["source"])
        if long_name is not None:
            ds.attrs["long_name"] = self.h5string(long_name)
        if v["dtype"] not in ("string",):
            ds.attrs["precision"] = v["precision"]

            def cautious_set(key):
                if v[key] is not None:
                    ds.attrs[key] = v[key]

            cautious_set("lower_ctrl_limit")
            cautious_set("upper_ctrl_limit")

    def assign_signal_type(self):
        """
        decide if a signal in the primary stream is a detector or a positioner
        """
        try:
            primary = self.root[
                "/entry/instrument/bluesky/streams/primary"
            ]
        except KeyError:
            raise KeyError(
                f"no primary data stream in "
                f"scan {self.scan_id} ({self.uid[:7]})"
            )
        for k, v in primary.items():
            # logger.debug(v.name)
            # logger.debug(v.keys())
            if k in self.detectors:
                signal_type = "detector"
            elif k in self.positioners:
                signal_type = "positioner"
            else:
                signal_type = "other"
            v.attrs["signal_type"] = signal_type  # group
            try:
                v["value"].attrs["signal_type"] = signal_type  # dataset
            except KeyError:
                logger.warning(
                    "Could not assign %s as signal type %s", k, signal_type
                )

    def create_NX_group(self, parent, specification):
        """
        create an h5 group with named NeXus class (specification)
        """
        local_address, nx_class = specification.split(":")
        if not nx_class.startswith("NX"):
            raise ValueError(
                "NeXus base class must start with 'NX',"
                f" received {nx_class}"
            )
        group = parent.create_group(local_address)
        group.attrs["NX_class"] = nx_class
        group.attrs["target"] = group.name  # for use as NeXus link
        return group

    def getResourceFile(self, resource_id):
        """
        full path to the resource file specified by uid ``resource_id``

        override in subclass as needed
        """
        # reject unsupported specifications
        resource = self.externals[resource_id]
        if resource["spec"] not in ("AD_HDF5",):
            # HDF5-specific implementation for now
            raise ValueError(
                f'{resource_id}: spec {resource["spec"]} not handled'
            )

        # logger.debug(yaml.dump(resource))
        fname = os.path.join(resource["root"], resource["resource_path"],)
        return fname

    def get_sample_title(self):
        """
        return the title for this sample

        default title: {plan_name}-S{scan_id}-{short_uid}
        """
        return f"{self.plan_name}-S{self.scan_id:04d}-{self.uid[:7]}"

    def get_stream_link(self, signal, stream=None, ref=None):
        """
        return the h5 object for ``signal``

        DEFAULTS

        ``stream`` : ``baseline``
        ``key`` : ``value_start``
        """
        stream = stream or "baseline"
        ref = ref or "value_start"
        h5_addr = (
            f"/entry/instrument/bluesky/streams/{stream}/{signal}/{ref}"
        )
        if h5_addr not in self.root:
            raise KeyError(f"HDF5 address {h5_addr} not found.")
        # return the h5 object, to make a link
        return self.root[h5_addr]

    def h5string(self, text):
        """Format string for h5py interface."""
        if isinstance(text, (tuple, list)):
            return [self.h5string(str(t)) for t in text]
        text = text or ""
        return text.encode("utf8")

    def writer(self):
        """
        write collected data to HDF5/NeXus data file
        """
        fname = self.file_name or self.make_file_name()
        with h5py.File(fname, "w") as self.root:
            self.write_root(fname)

        self.root = None
        logger.info(f"wrote NeXus file: {fname}")
        self.output_nexus_file = fname

    def write_data(self, parent):
        """
        group: /entry/data:NXdata
        """
        nxdata = self.create_NX_group(parent, "data:NXdata")

        primary = parent["instrument/bluesky/streams/primary"]
        for k in primary.keys():
            nxdata[k] = primary[k + "/value"]

        # pick the timestamps from one of the datasets (the last one)
        nxdata["EPOCH"] = primary[k + "/time"]

        signal_attribute = self.nxdata_signal
        if signal_attribute is None:
            if len(self.detectors) > 0:
                # arbitrary but consistent choice
                signal_attribute = self.detectors[0]
        axes_attribute = self.nxdata_signal_axes
        if axes_attribute is None:
            if len(self.positioners) > 0:
                # TODO: what if wrong shape here?
                axes_attribute = self.positioners

        # TODO: rabbit-hole alert!  simplify
        # this code is convoluted (like the selection logic)
        # Is there a library to help? databroker? event_model? area_detector_handlers?
        fmt = "Cannot set %s as %s attribute, no such dataset"
        if signal_attribute is not None:
            if signal_attribute in nxdata:
                nxdata.attrs["signal"] = signal_attribute

                axes = []
                for ax in axes_attribute or []:
                    if ax in nxdata:
                        axes.append(ax)
                    else:
                        logger.warning(fmt, ax, "axes")
                if axes_attribute is not None:
                    nxdata.attrs["axes"] = axes_attribute
            else:
                logger.warning(fmt, signal_attribute, "signal")

        return nxdata

    def write_detector(self, parent):
        """
        group: /entry/instrument/detectors:NXnote/DETECTOR:NXdetector
        """
        if len(self.detectors) == 0:
            logger.info("No detectors identified.")
            return

        primary = parent["/entry/instrument/bluesky/streams/primary"]

        group = self.create_NX_group(parent, "detectors:NXnote")
        for k, v in primary.items():
            if v.attrs.get("signal_type") != "detector":
                continue
            nxdetector = self.create_NX_group(group, f"{k}:NXdetector")
            nxdetector["data"] = v

        return group

    def write_entry(self):
        """
        group: /entry/data:NXentry
        """
        nxentry = self.create_NX_group(
            self.root, self.root.attrs["default"] + ":NXentry"
        )

        nxentry.create_dataset(
            "start_time",
            data=datetime.datetime.fromtimestamp(
                self.start_time
            ).isoformat(),
        )
        nxentry.create_dataset(
            "end_time",
            data=datetime.datetime.fromtimestamp(
                self.stop_time
            ).isoformat(),
        )
        ds = nxentry.create_dataset(
            "duration", data=self.stop_time - self.start_time
        )
        ds.attrs["units"] = "s"

        nxentry.create_dataset("program_name", data="bluesky")

        self.write_instrument(nxentry)  # also writes streams and metadata
        try:
            nxdata = self.write_data(nxentry)
            nxentry.attrs["default"] = nxdata.name.split("/")[-1]
        except KeyError as exc:
            logger.warning(exc)

        self.write_sample(nxentry)
        self.write_user(nxentry)

        # apply links
        h5_addr = "/entry/instrument/source/cycle"
        if h5_addr in self.root:
            nxentry["run_cycle"] = self.root[h5_addr]
        else:
            logger.warning("No data for /entry/run_cycle")

        nxentry["title"] = self.get_sample_title()
        nxentry["plan_name"] = self.root[
            "/entry/instrument/bluesky/metadata/plan_name"
        ]
        nxentry["entry_identifier"] = self.root[
            "/entry/instrument/bluesky/uid"
        ]

        return nxentry

    def write_instrument(self, parent):
        """
        group: /entry/instrument:NXinstrument
        """
        nxinstrument = self.create_NX_group(
            parent, "instrument:NXinstrument"
        )
        bluesky_group = self.create_NX_group(
            nxinstrument, "bluesky:NXnote"
        )

        md_group = self.write_metadata(bluesky_group)
        self.write_streams(bluesky_group)

        bluesky_group["uid"] = md_group["run_start_uid"]
        bluesky_group["plan_name"] = md_group["plan_name"]

        try:
            self.assign_signal_type()
        except KeyError as exc:
            logger.warning(exc)

        self.write_slits(nxinstrument)
        try:
            self.write_detector(nxinstrument)
        except KeyError as exc:
            logger.warning(exc)

        self.write_monochromator(nxinstrument)
        try:
            self.write_positioner(nxinstrument)
        except KeyError as exc:
            logger.warning(exc)
        self.write_source(nxinstrument)
        return nxinstrument

    def write_metadata(self, parent):
        """
        group: /entry/instrument/bluesky/metadata:NXnote

        metadata from the bluesky start document
        """
        group = self.create_NX_group(parent, "metadata:NXnote")

        ds = group.create_dataset("run_start_uid", data=self.uid)
        ds.attrs["long_name"] = "bluesky run uid"
        ds.attrs["target"] = ds.name

        for k, v in self.metadata.items():
            is_yaml = False
            if isinstance(v, (dict, tuple, list)):
                # fallback technique: save complicated structures as YAML text
                v = yaml.dump(v)
                is_yaml = True
            if isinstance(v, str):
                v = self.h5string(v)
            ds = group.create_dataset(k, data=v)
            ds.attrs["target"] = ds.name
            if is_yaml:
                ds.attrs["text_format"] = "yaml"

        return group

    def write_monochromator(self, parent):
        """
        group: /entry/instrument/monochromator:NXmonochromator
        """
        pre = "monochromator_dcm"
        keys = "wavelength energy theta y_offset mode".split()

        try:
            links = {
                key: self.get_stream_link(f"{pre}_{key}") for key in keys
            }
        except KeyError as exc:
            logger.warning(
                "%s -- not creating monochromator group", str(exc)
            )
            return

        pre = "monochromator"
        key = "feedback_on"
        try:
            links[key] = self.get_stream_link(f"{pre}_{key}")
        except KeyError as exc:
            logger.warning("%s -- feedback signal not found", str(exc))

        nxmonochromator = self.create_NX_group(
            parent, "monochromator:NXmonochromator"
        )
        for k, v in links.items():
            nxmonochromator[k] = v
        return nxmonochromator

    def write_positioner(self, parent):
        """
        group: /entry/instrument/positioners:NXnote/POSITIONER:NXpositioner
        """
        if len(self.positioners) == 0:
            logger.info("No positioners identified.")
            return

        primary = parent["/entry/instrument/bluesky/streams/primary"]

        group = self.create_NX_group(parent, "positioners:NXnote")
        for k, v in primary.items():
            if v.attrs.get("signal_type") != "positioner":
                continue
            nxpositioner = self.create_NX_group(group, f"{k}:NXpositioner")
            nxpositioner["value"] = v

        return group

    def write_root(self, filename):
        """
        root of the HDF5 file
        """
        self.root.attrs["file_name"] = filename
        self.root.attrs["file_time"] = datetime.datetime.now().isoformat()
        if self.instrument_name is not None:
            self.root.attrs["instrument"] = self.instrument_name
        self.root.attrs["creator"] = self.__class__.__name__
        self.root.attrs["NeXus_version"] = self.nexus_release
        self.root.attrs["HDF5_Version"] = h5py.version.hdf5_version
        self.root.attrs["h5py_version"] = h5py.version.version
        self.root.attrs["default"] = "entry"

        self.write_entry()

    def write_sample(self, parent):
        """
        group: /entry/sample:NXsample
        """
        pre = "sample_data"
        keys = """
            chemical_formula
            concentration
            description
            electric_field
            magnetic_field
            rotation_angle
            scattering_length_density
            stress_field
            temperature
            volume_fraction
            x_translation
        """.split()

        links = {}
        for key in keys:
            try:
                links[key] = self.get_stream_link(f"{pre}_{key}")
            except KeyError as exc:
                logger.warning("%s", str(exc))
        if len(links) == 0:
            logger.warning(
                "no sample data found, not creating sample group"
            )
            return

        nxsample = self.create_NX_group(parent, "sample:NXsample")
        for k, v in links.items():
            nxsample[k] = v

        for key in "electric_field magnetic_field stress_field".split():
            ds = nxsample[key]
            ds.attrs["direction"] = self.get_stream_link(
                f"{pre}_{key}_dir"
            )[()].lower()

        return nxsample

    def write_slits(self, parent):
        """
        group: /entry/instrument/slits:NXnote/SLIT:NXslit

        override in subclass to store content, name patterns
        vary with each instrument
        """
        # group = self.create_NX_group(parent, f"slits:NXnote")

    def write_source(self, parent):
        """
        group: /entry/instrument/source:NXsource

        Note: this is (somewhat) generic, override for a different source
        """
        nxsource = self.create_NX_group(parent, "source:NXsource")

        ds = nxsource.create_dataset("name", data="Bluesky framework")
        ds.attrs["short_name"] = "bluesky"
        nxsource.create_dataset("type", data="Synchrotron X-ray Source")
        nxsource.create_dataset("probe", data="x-ray")

        return nxsource

    def write_stream_external(
        self, parent, d, subgroup, stream_name, k, v
    ):
        # TODO: rabbit-hole alert! simplify
        # lots of variations possible

        # count number of unique resources (expect only 1)
        resource_id_list = []
        for datum_id in d:
            resource_id = self.externals[datum_id]["resource"]
            if resource_id not in resource_id_list:
                resource_id_list.append(resource_id)
        if len(resource_id_list) != 1:
            raise ValueError(
                f"{len(resource_id_list)}"
                f" unique resource UIDs: {resource_id_list}"
            )

        fname = self.getResourceFile(resource_id)
        logger.info("reading %s from EPICS AD data file: %s", k, fname)
        with h5py.File(fname, "r") as hdf_image_file_root:
            h5_obj = hdf_image_file_root["/entry/data/data"]
            ds = subgroup.create_dataset(
                "value",
                data=h5_obj[()],
                compression="lzf",
                # compression="gzip",
                # compression_opts=9,
                shuffle=True,
                fletcher32=True,
            )
            ds.attrs["target"] = ds.name
            ds.attrs["source_file"] = fname
            ds.attrs["source_address"] = h5_obj.name
            ds.attrs["resource_id"] = resource_id
            ds.attrs["units"] = ""

        subgroup.attrs["signal"] = "value"

    def write_stream_internal(
        self, parent, d, subgroup, stream_name, k, v
    ):
        # fmt: off
        subgroup.attrs["signal"] = "value"
        subgroup.attrs["axes"] = ["time", ]
        # fmt: on
        if isinstance(d, list) and len(d) > 0:
            if v["dtype"] in ("string",):
                d = self.h5string(d)
            elif v["dtype"] in ("integer", "number"):
                d = np.array(d)
        try:
            ds = subgroup.create_dataset("value", data=d)
            ds.attrs["target"] = ds.name
            try:
                self.add_dataset_attributes(ds, v, k)
            except Exception as exc:
                logger.error("%s %s %s %s", v["dtype"], type(d), k, exc)
        except TypeError as exc:
            logger.error(
                "%s %s %s %s",
                v["dtype"],
                k,
                f"TypeError({exc})",
                v["data"],
            )
        if stream_name == "baseline":
            # make it easier to pick single values
            # identify start/end of acquisition
            ds = subgroup.create_dataset("value_start", data=d[0])
            self.add_dataset_attributes(ds, v, k)
            ds.attrs["target"] = ds.name
            ds = subgroup.create_dataset("value_end", data=d[-1])
            self.add_dataset_attributes(ds, v, k)
            ds.attrs["target"] = ds.name

    def write_streams(self, parent):
        """
        group: /entry/instrument/bluesky/streams:NXnote

        data from all the bluesky streams
        """
        bluesky = self.create_NX_group(parent, "streams:NXnote")
        for stream_name, uids in self.streams.items():
            if len(uids) != 1:
                raise ValueError(
                    f"stream {len(uids)} has descriptors, expecting only 1"
                )
            group = self.create_NX_group(bluesky, stream_name + ":NXnote")
            uid0 = uids[0]  # just get the one descriptor uid
            group.attrs["uid"] = uid0
            # just get the one descriptor
            acquisition = self.acquisitions[uid0]
            for k, v in acquisition["data"].items():
                d = v["data"]
                # NXlog is for time series data but NXdata makes an automatic plot
                subgroup = self.create_NX_group(group, k + ":NXdata")

                if v["external"]:
                    self.write_stream_external(
                        parent, d, subgroup, stream_name, k, v
                    )
                else:
                    self.write_stream_internal(
                        parent, d, subgroup, stream_name, k, v
                    )

                t = np.array(v["time"])
                ds = subgroup.create_dataset("EPOCH", data=t)
                ds.attrs["units"] = "s"
                ds.attrs["long_name"] = "epoch time (s)"
                ds.attrs["target"] = ds.name

                t_start = t[0]
                ds = subgroup.create_dataset("time", data=t - t_start)
                ds.attrs["units"] = "s"
                ds.attrs["long_name"] = "time since first data (s)"
                ds.attrs["target"] = ds.name
                ds.attrs["start_time"] = t_start
                ds.attrs[
                    "start_time_iso"
                ] = datetime.datetime.fromtimestamp(t_start).isoformat()

            # link images to parent names
            for k in group:
                if k.endswith("_image") and k[:-6] not in group:
                    group[k[:-6]] = group[k]

        return bluesky

    def write_user(self, parent):
        """
        group: /entry/contact:NXuser
        """
        keymap = dict(
            name="bss_user_info_contact",
            affiliation="bss_user_info_institution",
            email="bss_user_info_email",
            facility_user_id="bss_user_info_badge",
        )

        try:
            links = {k: self.get_stream_link(v) for k, v in keymap.items()}
        except KeyError as exc:
            logger.warning("%s -- not creating source group", str(exc))
            return

        nxuser = self.create_NX_group(parent, "contact:NXuser")
        nxuser.create_dataset("role", data="contact")
        for k, v in links.items():
            nxuser[k] = v
        return nxuser


class NXWriterAPS(NXWriter):
    """
    Customize :class:`~NXWriter` with APS-specific content.

    .. index:: Bluesky Callback; NXWriterAPS

    New with apstools release 1.3.0.

    * Adds `/entry/instrument/undulator` group if metadata exists.
    * Adds APS information to `/entry/instrument/source` group.

    .. autosummary::

       ~write_instrument
       ~write_source
       ~write_undulator
    """

    # convention: methods written in alphabetical order

    def write_instrument(self, parent):
        """
        group: /entry/instrument:NXinstrument
        """
        nxinstrument = super().write_instrument(parent)
        self.write_undulator(nxinstrument)

    def write_source(self, parent):
        """
        group: /entry/instrument/source:NXsource

        Note: this is specific to the APS, override for a different source
        """
        pre = "aps"
        keys = "current fill_number".split()

        try:
            # fmt: off
            links = {
                key: self.get_stream_link(f"{pre}_{key}")
                for key in keys
            }
            # fmt: on
        except KeyError as exc:
            logger.warning("%s -- not creating source group", str(exc))
            return

        nxsource = self.create_NX_group(parent, "source:NXsource")
        for k, v in links.items():
            nxsource[k] = v

        ds = nxsource.create_dataset("name", data="Advanced Photon Source")
        ds.attrs["short_name"] = "APS"
        nxsource.create_dataset("type", data="Synchrotron X-ray Source")
        nxsource.create_dataset("probe", data="x-ray")
        ds = nxsource.create_dataset("energy", data=6)
        ds.attrs["units"] = "GeV"

        try:
            nxsource["cycle"] = self.get_stream_link("aps_aps_cycle")
        except KeyError:
            pass  # Should we compute the cycle?

        return nxsource

    def write_undulator(self, parent):
        """
        group: /entry/instrument/undulator:NXinsertion_device
        """
        pre = "undulator_downstream"
        keys = """
            device location
            energy
            energy_taper
            gap
            gap_taper
            harmonic_value
            total_power
            version
        """.split()

        try:
            links = {
                key: self.get_stream_link(f"{pre}_{key}") for key in keys
            }
        except KeyError as exc:
            logger.warning("%s -- not creating undulator group", str(exc))
            return

        undulator = self.create_NX_group(
            parent, "undulator:NXinsertion_device"
        )
        undulator.create_dataset("type", data="undulator")
        for k, v in links.items():
            undulator[k] = v
        return undulator
