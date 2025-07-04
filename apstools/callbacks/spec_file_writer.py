"""
SPEC Data File Writer Callback
++++++++++++++++++++++++++++++

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


.. autosummary::

   ~SpecWriterCallback
   ~SpecWriterCallback2
   ~spec_comment
"""

import datetime
import getpass
import logging
import pathlib
import socket
import time
from collections import OrderedDict

import numpy as np
from deprecated.sphinx import deprecated
from deprecated.sphinx import versionadded
from deprecated.sphinx import versionchanged

from .callback_base import FileWriterCallbackBase

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
            parts = s[p + 1 :].rstrip(")").split(",")
            for item in parts:
                # should be key=value pairs
                item = item.strip()
                p = item.find("=")
                if item[:p] == "name":
                    s = item[p + 1 :]  # get the name value
                    break
        return s

    def struct_to_str(struct):
        """Convert given structure into string representation."""
        if isinstance(struct, list):
            return "[" + ", ".join([struct_to_str(v) for v in struct]) + "]"
        elif isinstance(struct, dict):
            return "{" + ", ".join([f"{k}={struct_to_str(v)}" for k, v in struct.items()]) + "}"
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


@deprecated(version="1.7.0", reason="Use SpecWriterCallback2()")
class SpecWriterCallback(object):
    """
    **Deprecated**: Use :class:`~apstools.callbacks.spec_file_writer.SpecWriterCallback2`.

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

    def __init__(self, filename=None, auto_write=True, RE=None, reset_scan_id=False):
        self.clear()
        self.buffered_comments = self._empty_comments_dict()
        self.auto_write = auto_write
        self.uid_short_length = 8
        self.write_new_header = False
        self.spec_epoch = None  # for both #E & #D line in header, also offset for all scans
        self.spec_host = None
        self.spec_user = None
        self._datetime = None  # most recent document time
        self._motor_stream_name = "label_start_motor"
        self._header_motor_keys = None
        self._streams = {}  # descriptor documents, keyed by uid
        self.RE = RE

        if reset_scan_id is True:
            reset_scan_id = SCAN_ID_RESET_VALUE
        self.reset_scan_id = reset_scan_id

        if isinstance(filename, str):
            filename = pathlib.Path(filename)
        if filename is None or not filename.exists():
            filename = self.newfile(filename)
        else:
            max_scan_id = self.usefile(filename)
            if RE is not None and reset_scan_id is not False:
                RE.md["scan_id"] = max_scan_id
        self.spec_filename = filename

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
            token = document.get("uid") or document.get("datum_id")
            logger.debug("%s document, uid=%s", key, str(token))  # lgtm [py/clear-text-logging-sensitive-data]
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
        self.T_or_M_value = 1
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

        if doc["name"] == self._motor_stream_name:
            # list of all known positioners (motors)
            mlist = sorted(doc["object_keys"].keys())
            if self._header_motor_keys != mlist:
                self.write_new_header = True
            self.positioners = {k: None for k in mlist}
            return
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
        middle_keys = [k for k in keyset if k not in first_keys + last_keys]
        epoch_keys = "Epoch_float Epoch".split()

        self.data.update({k: [] for k in first_keys + epoch_keys + middle_keys + last_keys})

    def event(self, doc):
        """
        handle *event* documents
        """
        descriptor = self._streams.get(doc["descriptor"])
        if descriptor is None:
            fmt = "descriptor UID {} not found"
            raise KeyError(fmt.format(doc["descriptor"]))
        if descriptor["name"] == self._motor_stream_name:
            for k in self.positioners.keys():
                self.positioners[k] = doc["data"][k]  # get motor values
        elif descriptor["name"] == "primary":
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
        lines.append("#D " + datetime.datetime.strftime(dt, SPEC_TIME_FORMAT))
        if self.T_or_M is not None:
            lines.append(f"#{self.T_or_M} {self.T_or_M_value}")

        for v in self.comments["start"]:
            # C Wed Feb 03 16:51:38 2016.  do ./usaxs.mac.
            lines.append("#C " + v)  # TODO: add time/date stamp as SPEC does
        for v in self.comments["descriptor"]:
            lines.append("#C " + v)

        for k, v in self.metadata.items():
            # "#MD" is our ad hoc SPEC data tag
            lines.append(f"#MD {k} = {v}")

        if sorted(self.positioners.keys()) != self._header_motor_keys:
            self.write_new_header = True
        if len(self.positioners) == 0:
            lines.append("#P0 ")
        else:
            values = list(self.positioners.values())
            r = 0
            while len(values) > 0:
                lines.append(f"#P{r} " + " ".join([str(v) for v in values[:8]]))
                values = values[8:]
                r += 1

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
        """Write the (initial) header section of a SPEC data file."""
        dt = datetime.datetime.fromtimestamp(self.spec_epoch)
        lines = []
        # Ok to repeat #F in addtional header sections
        lines.append(f"#F {self.spec_filename}")
        lines.append(f"#E {self.spec_epoch}")
        lines.append(f"#D {datetime.datetime.strftime(dt, SPEC_TIME_FORMAT)}")
        lines.append(f"#C Bluesky  user = {self.spec_user}  host = {self.spec_host}")
        self._header_motor_keys = sorted(self.positioners.keys())
        if len(self._header_motor_keys) == 0:
            lines.append("#O0 ")  # names
            lines.append("#o0 ")  # mnemonics
        else:
            delimiter = " " * 2  # two spaces between names
            for pre in "#O #o".split():  # same list for names and mnemonics
                values = self._header_motor_keys
                r = 0
                while len(values) > 0:
                    lines.append(f"{pre}{r} " + delimiter.join([str(v) for v in values[:8]]))
                    values = values[8:]
                    r += 1

        lines.append("")

        if self.spec_filename.exists():
            lines.insert(0, "")
        self._write_lines_(lines, mode="a+")
        self.write_new_header = False

    def write_scan(self):
        """
        write the most recent (completed) scan to the file

        * creates file if not existing
        * writes header if needed
        * appends scan data

        note:  does nothing if there are no lines to be written
        """
        if self.spec_filename.exists():
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
            if self.write_new_header:
                self.write_header()
                logger.info("wrote header to SPEC file: %s", self.spec_filename)
            self._write_lines_(lines, mode="a")
            logger.info(
                "wrote scan %d to SPEC file: %s",
                self.scan_id,
                self.spec_filename,
            )

    def make_default_filename(self):
        """generate a file name to be used as default"""
        now = datetime.datetime.now()
        filename = now.strftime("%Y%m%d-%H%M%S") + ".dat"
        return pathlib.Path(filename)

    def newfile(self, filename=None, scan_id=None, RE=None):
        """
        prepare to use a new SPEC data file

        but don't create it until we have data
        """
        self.clear()
        filename = pathlib.Path(filename or self.make_default_filename())
        if filename.exists():
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
        self.write_new_header = True  # don't write the file yet

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
        if not self.spec_filename.exists():
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


@versionchanged(
    version="1.7.6",
    reason="Translate motor object_key to motor data_key",
)
@versionchanged(version="1.7.4", reason="refactor how labels are gathered")
@versionchanged(version="1.7.1", reason="set spec_filename in constructor")
@versionadded(version="1.7.0")
class SpecWriterCallback2(FileWriterCallbackBase):
    """
    Write SPEC data file as data is collected, line-by-line.

    .. index:: Bluesky Callback; SpecWriterCallback2

    This writes data from a scan as each *event* document is received. One or
    more scans can be written to the same file.  The file format is text.

    .. rubric: Override Methods from FileWriterCallbackBase
    .. autosummary::
        ~descriptor
        ~event
        ~start
        ~stop
        ~writer

    .. rubric: New Methods
    .. autosummary::
        ~_cmt
        ~_write_lines_
        ~make_default_filename
        ~newfile
        ~usefile
        ~write_file_header
        ~write_scan_data_row
        ~write_scan_end
        ~write_scan_header

    .. rubric: Properties
    .. autosummary::
        ~spec_filename
    """

    # - - - - # - - - - # - - - - # - - - - # - - - - # - - - - # - - - - #
    # Override Methods

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._file_header_motor_keys = None
        self._motor_stream_name = "label_start_motor"
        self.data_labels: list = []
        self.file_epoch = None
        self.spec_filename = None
        self.write_new_file_header = True
        self.write_new_scan_header = False

    def descriptor(self, doc):
        """
        Handle *descriptor* documents of certain streams.
        """
        from ..utils.descriptor_support import get_stream_data_map

        if doc["uid"] in self._streams:
            fmt = "duplicate descriptor UID {} found"
            raise KeyError(fmt.format(doc["uid"]))

        # log descriptor documents by uid
        # referenced by event and bulk_events documents
        self._streams[doc["uid"]] = doc

        if doc["name"] == self._motor_stream_name:
            # list of all known positioners (motors), #O:#P lines
            mlist = sorted(doc["configuration"])
            if self._file_header_motor_keys != mlist:
                self.write_new_file_header = True
            self.motors = {k: None for k in mlist}
            return  # nothing more to do now

        elif doc["name"] != "primary":
            return

        super().descriptor(doc)  # process the document

        detectors = self.data_map.get("detectors", [])
        motors = self.data_map.get("motors", [])
        others = self.data_map.get("unassigned", [])
        if len(detectors) > 1:
            # First detector assumed to be the most important one.
            # Move first "detector" to last column per SPEC convention.
            detectors.append(detectors.pop(0))

        # Per SPEC convention, write the labels in this order:
        self.data_labels = motors + "Epoch Epoch_float".split() + others + detectors
        self.write_new_scan_header = True

    def event(self, doc):
        super().event(doc)  # process the document

        descriptor = self._streams.get(doc["descriptor"])
        if descriptor is None:
            raise KeyError(f"Descriptor UID {doc['descriptor']} not found.")

        if descriptor["name"] == self._motor_stream_name:
            for k in self.motors.keys():
                key = k
                if key not in doc["data"]:
                    # De-reference assuming readback is the first in the list.
                    key = descriptor["object_keys"][k][0]
                self.motors[k] = doc["data"][key]  # get motor readback value
            return

        self.write_file_header()
        self.write_scan_header()
        self.write_scan_data_row(doc)

    def start(self, doc):
        """First document of the run."""
        super().start(doc)  # process the document

        self.data_labels: list = []  # clear it for this run, descriptor will define it.
        self.file_epoch = self.file_epoch or self.start_time  # timestamp
        login_id = self.metadata.get("login_id")
        if login_id is not None:
            self.spec_user, self.spec_host = login_id.split("@")
        else:
            self.spec_host = socket.gethostname() or "localhost"
            self.spec_user = getpass.getuser() or "BlueskyUser"

        # Create new file (if necessary)
        self.file_name = self.file_name or self.make_file_name()

        self.motors = {}  # names in #O, values in #P
        self._streams = {}  # descriptor documents, keyed by uid

        self.T_or_M = None  # TODO: How to learn if "T" or "M" from the document stream?
        self.T_or_M_value = 1

        self.scan_command = _rebuild_scan_command(doc)

    def stop(self, doc):
        """Last document of the run."""
        # ... just in case these have not been written.
        self.write_file_header()
        self.write_scan_header()

        super().stop(doc)  # process the document

        self.write_scan_end(doc)

    def writer(self):
        """Output to a file completed by other methods."""
        pass

    # - - - - # - - - - # - - - - # - - - - # - - - - # - - - - # - - - - #
    # Local Methods

    def _cmt(self, text):
        """
        Return a SPEC-style comment.

        ``#C Wed Jul 04 14:56:21 1776.  uid = abcdefg-1234-4321-8524686c-abcd1234dcba``
        """
        dt = datetime.datetime.fromtimestamp(self.doc_timestamp or time.time())
        spec_time = dt.strftime(SPEC_TIME_FORMAT)
        return f"#C {spec_time}.  {text}"

    def make_default_filename(self):
        """generate a file name to be used as default"""
        now = datetime.datetime.now()
        filename = now.strftime("%Y%m%d-%H%M%S") + ".dat"
        return pathlib.Path(filename)

    def newfile(self, filename=None, scan_id=None, RE=None):
        """
        prepare to use a new SPEC data file

        but don't create it until we have data
        """
        self.clear()
        filename = pathlib.Path(filename or self.make_default_filename())
        if filename.exists():
            from spec2nexus.spec import SpecDataFile

            sdf = SpecDataFile(filename)
            scan_list = sdf.getScanNumbers()
            l = len(scan_list)
            m = 0 if l == 0 else max(map(float, scan_list))
            highest = int(max(l, m) + 0.9999)  # solves issue #128
            scan_id = max(scan_id or 0, highest)
        self.spec_filename = filename
        self.spec_epoch = int(time.time())  # ! no roundup here!!!
        self.spec_host = socket.gethostname() or "localhost"
        self.spec_user = getpass.getuser() or "BlueskyUser"

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
        if not self.spec_filename.exists():
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

    def write_file_header(self):
        """Write file header to file, if needed."""
        if not self.write_new_file_header:
            # print(f"No new file header for {self.uid=!r}")
            return

        dt = datetime.datetime.fromtimestamp(self.file_epoch)

        lines = []

        if self.file_name.exists() and self.file_name.stat().st_size > 0:
            lines.append("")
        lines.append(f"#F {self.file_name}")
        lines.append(f"#E {self.file_epoch}")
        lines.append(f"#D {datetime.datetime.strftime(dt, SPEC_TIME_FORMAT)}")
        lines.append(f"#C Bluesky  user = {self.spec_user}  host = {self.spec_host}")

        self._file_header_motor_keys = sorted(self.motors.keys())
        if len(self._file_header_motor_keys) == 0:
            lines.append("#O0 ")  # names
            lines.append("#o0 ")  # mnemonics
        else:
            delimiter = " " * 2  # two spaces between names
            for pre in "#O #o".split():  # same list for names and mnemonics
                values = self._file_header_motor_keys
                r = 0
                while len(values) > 0:
                    lines.append(f"{pre}{r} " + delimiter.join([str(v) for v in values[:8]]))
                    values = values[8:]
                    r += 1

        # lines.append("")

        self._write_lines_(lines, mode="a+")
        self.write_new_file_header = False

    def write_scan_data_row(self, doc):
        """Write row of scan data to file."""
        from ..utils.misc import render

        line = []
        remarks = []
        for label in self.data_labels:
            if label in ("Epoch", "Epoch_float"):
                value = doc["time"] - self.start_time
                if label == "Epoch":
                    value = round(value)
            else:
                value = doc["data"].get(label)
            if isinstance(value, (float, int)):
                line.append(render(value))
            else:
                # Scan data is expected to be numbers. This is not.  Substitute
                # the row number and report after this line in a #U line.
                line.append(str(doc["seq_num"]))
                remarks.append(f"#U {label} = {value}")

        lines = [" ".join(line)]
        self._write_lines_(lines + remarks, mode="a+")

    def write_scan_end(self, doc):
        """Write scan ending to file."""
        lines = []

        if len(self.externals) > 0:
            lines.append(f"#U externals: {self.externals!r}")

        if "num_events" in doc:
            for k, v in doc["num_events"].items():
                lines.append(self._cmt(f"num_events_{k} = {v}"))

        if "exit_status" in doc:
            lines.append(self._cmt(f"exit_status = {doc['exit_status']}"))
        else:
            lines.append(self._cmt("exit_status = not available"))

        self._write_lines_(lines, mode="a+")

    def write_scan_header(self):
        """Write scan header to file."""
        from ..utils.misc import render

        if not self.write_new_scan_header:
            # print(f"Not writing new scan header. {self.scan_id=!r}")
            return

        dt = datetime.datetime.fromtimestamp(self.start_time)

        lines = [""]
        lines.append(f"#S {self.scan_command}")
        lines.append("#D " + datetime.datetime.strftime(dt, SPEC_TIME_FORMAT))
        if self.T_or_M is not None:
            lines.append(f"#{self.T_or_M} {self.T_or_M_value}")
        lines.append(self._cmt(f"uid = {self.uid}"))

        if len(self.motors) == 0:
            lines.append("#P0 ")
        else:
            values = list(self.motors.values())
            r = 0
            while len(values) > 0:
                lines.append(f"#P{r} " + " ".join([render(v) for v in values[:8]]))
                values = values[8:]
                r += 1

        for k, v in self.metadata.items():
            # "#MD" is our ad hoc SPEC data tag
            lines.append(f"#MD {k} = {v}")

        lines.append("#N " + str(len(self.data_labels)))
        if len(self.data_labels) > 0:
            lines.append("#L " + "  ".join(self.data_labels))
        else:
            lines.append("#C no data column labels identified")

        self._write_lines_(lines, mode="a+")

        self.write_new_scan_header = False

    def _write_lines_(self, lines, mode="a"):
        """write (more) lines to the file"""
        lines.append("")
        with open(self.file_name, mode) as f:
            f.write("\n".join(lines))

    # - - - - # - - - - # - - - - # - - - - # - - - - # - - - - # - - - - #
    # properties

    @property
    def spec_filename(self):
        """
        Synonym for 'file_name' property.

        API compatibility with SpecWriterCallback.
        """
        return self.file_name

    @spec_filename.setter
    def spec_filename(self, file_name):
        self.file_name = file_name or self.make_default_filename()


@versionadded(version="1.7.1")
def spec_comment(comment, doc=None, writer=None):
    """
    make it easy to add spec-style comments in a custom plan

    These comments *only* go into the SPEC data file.

    PARAMETERS

    comment *string* :
        (optional)
        Comment text to be written.  SPEC expects it to be only one line!

    doc *string* :
        (optional)
        Bluesky RunEngine document type.
        One of: ``start descriptor event resource datum stop``
        (default: ``event``)

    writer *obj* :
        (optional)
        Instance of ``SpecWriterCallback()``,
        typically: ``specwriter = SpecWriterCallback()``
    """
    # global specwriter  # such as: specwriter = SpecWriterCallback()
    # writer = writer or specwriter  # FIXME: get from namespace
    if doc is None:
        if writer.scanning:
            doc = "event"
        else:
            doc = "start"
    for line in comment.splitlines():
        writer._cmt(doc, line)


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
