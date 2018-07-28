
"""
BlueSky callback that writes SPEC data files

.. autosummary::
   
   ~SpecWriterCallback

EXAMPLE : use as BlueSky callback::

    from APS_BlueSky_tools.filewriters import SpecWriterCallback
    specwriter = SpecWriterCallback()
    RE.subscribe(specwriter.receiver)

EXAMPLE : use as writer from Databroker::

    from APS_BlueSky_tools.filewriters import SpecWriterCallback
    specwriter = SpecWriterCallback()
    for key, doc in db.get_documents(db[-1]):
        specwriter.receiver(key, doc)
    print("Look at SPEC data file: "+specwriter.spec_filename)

EXAMPLE : use as writer from Databroker with customizations::

    from APS_BlueSky_tools.filewriters import SpecWriterCallback
    
    # write into file: /tmp/cerium.spec
    specwriter = SpecWriterCallback(filename="/tmp/cerium.spec")
    for key, doc in db.get_documents(db[-1]):
        specwriter.receiver(key, doc)
    
    # write into file: /tmp/barium.dat
    specwriter.newfile("/tmp/barium.dat")
    for key, doc in db.get_documents(db["b46b63d4"]):
        specwriter.receiver(key, doc)

"""

# Copyright (c) 2017-2018, UChicago Argonne, LLC.  See LICENSE file.


from collections import OrderedDict
import datetime
import getpass
import logging
import os
import socket
import time


logger = logging.getLogger(__name__).addHandler(logging.NullHandler())


#    Programmer's Note: subclassing from `object` avoids the need 
#    to import `bluesky.callbacks.core.CallbackBase`.  
#    One less import when only accessing the Databroker.
#    The *only* advantage to subclassing from CallbackBase
#    seems to be a simpler setup call to RE.subscribe().
#
#    superclass   | subscription code
#    ------------ | -------------------------------
#    object       | RE.subscribe(specwriter.receiver)
#    CallbackBase | RE.subscribe(specwriter)


SPEC_TIME_FORMAT = "%a %b %d %H:%M:%S %Y"

def _rebuild_scan_command(doc):
    """reconstruct the scan command for SPEC data file #S line"""
    
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
        if p > 0:           # only if an open parenthesis is found
            parts = s[p+1:].rstrip(")").split(",")
            for item in parts:
                # should be key=value pairs
                item = item.strip()
                p = item.find("=")
                if item[:p] == "name":
                    s = item[p+1:]      # get the name value
                    break
        return s

    s = []
    if "plan_args" in doc:
        for _k, _v in doc['plan_args'].items():
            if _k == "detectors":
                _v = doc[_k]
            elif _k.startswith("motor"):
                _v = doc["motors"]
            elif _k == "args":
                _v = "[" +  ", ".join(map(get_name, _v)) + "]"
            s.append("{}={}".format(_k, _v))
    
    cmd = "{}({})".format(doc.get("plan_name", ""), ", ".join(s))
    scan_id = doc.get("scan_id") or 1    # TODO: improve the `1` default
    return "{}  {}".format(scan_id, cmd)


class SpecWriterCallback(object):
    """
    collect data from BlueSky RunEngine documents to write as SPEC data
    
    This gathers data from all documents and appends scan to the file 
    when the *stop* document is received.
    
    Parameters

    filename : string, optional
        Local, relative or absolute name of SPEC data file to be used.
        If `filename=None`, defaults to format of YYYmmdd-HHMMSS.dat
        derived from the current system time.
    auto_write : boolean, optional
        If True (default), `write_scan()` is called when *stop* document 
        is received.
        If False, the caller is responsible for calling `write_scan()`
        before the next *start* document is received.

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
       ~stop

    """
    
    def __init__(self, filename=None, auto_write=True):
        self.clear()
        self.spec_filename = filename
        self.auto_write = auto_write
        self.uid_short_length = 8
        self.write_file_header = False
        self.spec_epoch = None      # for both #E & #D line in header, also offset for all scans
        self.spec_host = None
        self.spec_user = None
        self._datetime = None       # most recent document time as datetime object
        self._streams = {}          # descriptor documents, keyed by uid
        if filename is None or not os.path.exists(filename):
            self.newfile(filename)
        else:
            last_scan_id = self.usefile(filename)   # TODO: set RE's scan_id based on result?

    def clear(self):
        """reset all scan data defaults"""
        self.uid = None
        self.scan_epoch = None      # absolute epoch to report in scan #D line
        self.time = None            # full time from document
        self.comments = dict(start=[], event=[], descriptor=[], resource=[], datum=[], stop=[])
        self.data = OrderedDict()           # data in the scan
        self.detectors = OrderedDict()      # names of detectors in the scan
        self.hints = OrderedDict()          # why?
        self.metadata = OrderedDict()       # #MD lines in header
        self.motors = OrderedDict()         # names of motors in the scan
        self.positioners = OrderedDict()    # names in #O, values in #P
        self.num_primary_data = 0
        #
        # note: for one scan, #O & #P information is not provided
        # unless collecting baseline data
        # wait for case with baseline data that needs #O/#P lines
        #
        self.columns = OrderedDict()        # #L in scan
        self.scan_command = None            # #S line

    def _cmt(self, key, text):
        """enter a comment"""
        ts = datetime.datetime.strftime(self._datetime, SPEC_TIME_FORMAT)
        self.comments[key].append("{}.  {}".format(ts, text))


    def receiver(self, key, document):
        """BlueSky callback: receive all documents for handling"""
        xref = dict(
            start = self.start,
            descriptor = self.descriptor,
            event = self.event,
            bulk_events = self.bulk_events,
            datum = self.datum,
            resource = self.resource,
            stop = self.stop,
        )
        logger = logging.getLogger(__name__)
        if key in xref:
            uid = document.get("uid") or document.get("datum_id")
            logger.debug("{} document, uid={}".format(key, uid))
            ts = document.get("time")
            if ts is None:
                ts = datetime.datetime.now()
            else:
                ts = datetime.datetime.fromtimestamp(document["time"])
            self._datetime = ts
            xref[key](document)
        else:
            msg = "custom_callback encountered: {} : {}".format(key, document)
            # raise ValueError(msg)
            logger.warning(msg)

    def start(self, doc):
        """handle *start* documents"""
        
        known_properties = """
            uid time project sample scan_id group owner
            detectors hints
            plan_type plan_name plan_args
        """.split()

        self.clear()
        self.uid = doc["uid"]
        self._cmt("start", "uid = {}".format(self.uid))
        self.time = doc["time"]
        self.scan_epoch = int(self.time)
        self.scan_id = doc["scan_id"] or 0
        # Which reference? fixed counting time or fixed monitor count?
        # Can this be omitted?
        self.T_or_M = None          # for now
        # self.T_or_M = "T"           # TODO: how to get this from the document stream?
        # self.T_or_M_value = 1
        # self._cmt("start", "!!! #T line not correct yet !!!")
        
        # metadata
        for key in sorted(doc.keys()):
            if key not in known_properties:
                self.metadata[key] = doc[key]
        
        # various dicts
        for item in "detectors hints motors".split():
            if item in doc:
                obj = self.__getattribute__(item)
                for key in doc.get(item):
                    obj[key] = None
        
        cmt = "plan_type = " + doc["plan_type"]
        ts = datetime.datetime.strftime(self._datetime, SPEC_TIME_FORMAT)
        self.comments["start"].insert(0, "{}.  {}".format(ts, cmt))
        self.scan_command = _rebuild_scan_command(doc)
    
    def descriptor(self, doc):
        """
        handle *descriptor* documents
        
        prepare for primary scan data, ignore any other data stream
        """
        # TODO: log descriptor documents by uid 
        #       for reference from event and bulk_events documents
        if doc["uid"] in self._streams:
            fmt = "duplicate descriptor UID {} found"
            raise KeyError(fmt.format(doc["uid"]))
        
        # log descriptor documents by uid
        # referenced by event and bulk_events documents
        self._streams[doc["uid"]] = doc
        
        if doc["name"] == "primary":
            doc_data_keys = list(doc["data_keys"].keys())
            self.data.update({k: [] for k in sorted(doc_data_keys)})
            self.data["Epoch"] = []
            self.data["Epoch_float"] = []
        
            # SPEC data files have implied defaults
            # SPEC default: X axis in 1st column and Y axis in last column
            _at_last = len(self.motors) > 0
            self.data.move_to_end("Epoch_float", last=_at_last)
            self.data.move_to_end("Epoch")
            
            # TODO: move motors to first
            # TODO: move detectors to last
            
            if len(self.motors) > 0:
                # find 1st motor and move to last
                motor_name = list(self.motors.keys())[0]
                self.data.move_to_end(motor_name, last=False)
            # monitor (detector) in next to last position 
            # but how can we get that name here?
            if len(self.detectors) > 0:
                # find 1st detector and move to last
                det_name = list(self.detectors.keys())[0]
                if det_name not in self.data and len(doc_data_keys) > 0:
                    det_name = doc_data_keys[0]
                if det_name in self.data:
                    self.data.move_to_end(det_name)

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
                    fmt = "unexpected failure here, key {} not found"
                    raise KeyError(fmt.format(k))
                    #return                  # not our expected event data
            for k in self.data.keys():
                if k == "Epoch":
                    v = int(doc["time"] - self.time + 0.5)
                elif k == "Epoch_float":
                    v = doc["time"] - self.time
                else:
                    v = doc["data"][k]
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
                self._cmt("stop", "num_events_{} = {}".format(k, v))
        if "exit_status" in doc:
            self._cmt("stop", "exit_status = " + doc["exit_status"])
        else:
            self._cmt("stop", "exit_status = not available")

        if self.auto_write:
            self.write_scan()

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
            lines.append("#{} {}".format(self.T_or_M, self.T_or_M_value))

        for v in self.comments["start"]:
            #C Wed Feb 03 16:51:38 2016.  do ./usaxs.mac.
            lines.append("#C " + v)     # TODO: add time/date stamp as SPEC does
        for v in self.comments["descriptor"]:
            lines.append("#C " + v)

        for k, v in self.metadata.items():
            # "#MD" is our ad hoc SPEC data tag
            lines.append("#MD {} = {}".format(k, v))

        lines.append("#N " + str(self.num_primary_data))
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
                    lines.append("#U {} {} {}".format(i, k, str_data[k]))
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
        lines.append("#F " + self.spec_filename)
        lines.append("#E " + str(self.spec_epoch))
        lines.append("#D " + datetime.datetime.strftime(dt, SPEC_TIME_FORMAT))
        lines.append("#C " + "BlueSky  user = {}  host = {}".format(self.spec_user, self.spec_host))
        lines.append("")

        if os.path.exists(self.spec_filename):
            raise IOError("file ({}) exists".format(self.spec_filename))
        self._write_lines_(lines, mode="w")
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
                    fmt = "{} already contains uid={}"
                    raise ValueError(fmt.format(self.spec_filename, self.uid))
        logger = logging.getLogger(__name__)
        lines = self.prepare_scan_contents()
        lines.append("")
        if lines is not None:
            if self.write_file_header:
                self.write_header()
                logger.info("wrote header to SPEC file: " + self.spec_filename)
            self._write_lines_(lines, mode="a")
            logger.info("wrote scan {} to SPEC file: {}".format(self.scan_id, self.spec_filename))

    def make_default_filename(self):
        """generate a file name to be used as default"""
        now = datetime.datetime.now()
        return datetime.datetime.strftime(now, "%Y%m%d-%H%M%S")+".dat"

    def newfile(self, filename=None, reset_scan_id=False):
        """
        prepare to use a new SPEC data file
        
        but don't create it until we have data
        """
        self.clear()
        filename = filename or self.make_default_filename()
        if os.path.exists(filename):
            ValueError("file {} exists".format(filename))
        self.spec_filename = filename
        self.spec_epoch = int(time.time())  # ! no roundup here!!!
        self.spec_host = socket.gethostname() or 'localhost'
        self.spec_user = getpass.getuser() or 'BlueSkyUser' 
        self.write_file_header = True       # don't write the file yet
        if reset_scan_id:
            raise NotImplemented("How to reset the BlueSky RE scan_id?")
        return self.spec_filename
    
    def usefile(self, filename):
        """read from existing SPEC data file"""
        if not os.path.exists(self.spec_filename):
            IOError("file {} does not exist".format(filename))
        scan_id = None
        with open(filename, "r") as f:
            key = "#F"
            line = f.readline().strip()
            if not line.startswith(key+" "):
                raise ValueError("first line does not start with "+key)

            key = "#E"
            line = f.readline().strip()
            if not line.startswith(key+" "):
                raise ValueError("first line does not start with "+key)
            epoch = int(line.split()[-1])

            key = "#D"
            line = f.readline().strip()
            if not line.startswith(key+" "):
                raise ValueError("first line does not start with "+key)
            # ignore content, it is derived from #E line

            key = "#C"
            line = f.readline().strip()
            if not line.startswith(key+" "):
                raise ValueError("first line does not start with "+key)
            p = line.split()
            username = "BlueSkyUser"
            if len(p) > 4 and p[2] == "user":
                username = p[4]
            
            # find the last scan number used
            key = "#S"
            for line in f.readlines():
                if line.startswith(key+" ") and len(line.split())>1:
                    scan_id = int(line.split()[1])

        self.spec_filename = filename
        self.spec_epoch = epoch
        self.spec_user = username
        return scan_id
