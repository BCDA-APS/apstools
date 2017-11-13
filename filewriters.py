
"""
BlueSky callback that writes SPEC data files

EXAMPLE : use as BlueSky callback::

    from filewriters import SpecWriterCallback
    specwriter = SpecWriterCallback()
    RE.subscribe(specwriter.receiver)

EXAMPLE : use as writer from Databroker::

    from filewriters import SpecWriterCallback
    specwriter = SpecWriterCallback()
    for key, doc in db.get_documents(db[-1]):
        specwriter.receiver(key, doc)

EXAMPLE : use as writer from Databroker with customizations::

    from filewriters import SpecWriterCallback
    specwriter = SpecWriterCallback(path="/tmp", auto_write=False)
    for key, doc in db.get_documents(db[-1]):
        specwriter.receiver(key, doc)
    # write into file: /tmp/cerium.spec
    specwriter.spec_filename = "cerium"
    specwriter.file_suffix = ".spec"
    specwriter.write_file()

"""


from collections import OrderedDict
import datetime
import os


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


class SpecWriterCallback(object):
    """
    collect data from BlueSky RunEngine documents to write as SPEC data
    
    This gathers data from all documents and writes the file when the 
    *stop* document is received.  Only one scan is written to a data 
    file now.  (An upgrade would be to add a flag to the callback 
    to write more than one scan to a single data file.)
    
    Parameters
    ----------
    path : string, optional
        The directory in which to write SPEC data files.
        If path = None (or not specified), then the current 
        working directory (`os.getcwd()`) will be used.
    auto_write : boolean, optional
        If True (default), `write_file()` is called when *stop* document 
        is received.
        If False, the caller is responsible for calling `write_file()`.

    """
    
    def __init__(self, path=None, auto_write=True):
        self.clear()
        self.path = path or os.getcwd()
        self.auto_write = auto_write
        self.file_suffix = ".dat"
        self.uid_short_length = 8

    def clear(self):
        """reset all scan data defaults"""
        self.uid = None
        self.spec_filename = None
        self.spec_epoch = None      # for both #E & #D line in header, also offset for all scans
        self.time = None            # full time from document
        self.spec_comment = None    # for first #C line in header
        self.comments = dict(start=[], event=[], descriptor=[], stop=[])
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
        # TODO: show case for baseline data that needs #O/#P lines
        #
        self.columns = OrderedDict()        # #L in scan
        self.scan_command = None            # #S line

    def receiver(self, key, document):
        """receive all documents for handling"""
        xref = dict(
            start = self.start,
            descriptor = self.descriptor,
            event = self.event,
            bulk_events = self.bulk_events,
            stop = self.stop,
        )
        if key in xref:
            xref[key](document)
        else:
            msg = "custom_callback encountered: {} : {}".format(key, document)
            # raise ValueError(msg)
            print(msg)
        return
    
    def start(self, doc):
        """handle *start* documents"""
        
        known_properties = """
            uid time project sample scan_id group owner
            detectors hints
            plan_type plan_name plan_args
        """.split()

        self.clear()
        self.uid = doc["uid"]
        self.spec_filename = self._build_file_name(doc)
        self.time = doc["time"]
        self.spec_epoch = int(self.time)
        self.spec_comment = "BlueSky  uid = " + self.uid
        # Which reference? fixed counting time or fixed monitor count?
        # Can this be omitted?
        self.T_or_M = None          # for now
        #self.T_or_M = "T"           # TODO: how to get this from the document stream?
        #self.T_or_M_value = 1
        self.comments["start"].append("!!! #T line not correct yet !!!")
        dt = datetime.datetime.fromtimestamp(self.time)
        self.comments["start"].append("time = " + str(dt))
        
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
        
        self.comments["start"].insert(0, "plan_type = " + doc["plan_type"])
        self.scan_command = self._rebuild_scan_command(doc)
    
    def _build_file_name(self, doc):
        """create the SPEC data file name"""
        # example shows how to override with a custom name
        s = self.uid[:self.uid_short_length]
        s += self.file_suffix
        return s

    def _rebuild_scan_command(self, doc):
        """reconstruct the scan command for SPEC data file #S line"""
        s = []
        for _k, _v in doc['plan_args'].items():
            if _k == "detectors":
                _v = doc[_k]
            elif _k.startswith("motor"):
                _v = doc["motors"]
            s.append("{}={}".format(_k, _v))
        
        cmd = "{}({})".format(doc.get("plan_name", ""), ", ".join(s))
        scan_id = doc.get("scan_id") or 1    # TODO: improve the default
        return "{}  {}".format(scan_id, cmd)
        
    def descriptor(self, doc):
        """
        handle *descriptor* documents
        
        prepare for primary scan data, ignore any other data stream
        """
        if doc["name"] == "primary":        # general?
            for k in doc["data_keys"].keys():
                self.data[k] = []
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
                if det_name not in self.data:
                    det_name = list(doc["data_keys"].keys())[0]
                if det_name in self.data:
                    self.data.move_to_end(det_name)

    def event(self, doc):
        """
        handle *event* documents
        """
        # first, ensure that all data keys in this event doc are expected
        # as a substitute check of the descriptor document for "primary"
        for k in doc["data"].keys():
            if k not in self.data.keys():
                return                  # not our expected event data
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
    
    def stop(self, doc):
        """handle *stop* documents"""
        if "num_events" in doc:
            for k, v in doc["num_events"].items():
                self.comments["stop"].append("num_events_{} = {}".format(k, v))
        if "time" in doc:
            dt = datetime.datetime.fromtimestamp(doc["time"])
            self.comments["stop"].append("time = " + str(dt))
        if "exit_status" in doc:
            self.comments["stop"].append("exit_status = " + doc["exit_status"])
        else:
            self.comments["stop"].append("exit_status = not available")

        if self.auto_write:
            self.write_file()

    def write_file(self):
        lines = self.prepare_file_contents()
        if lines is not None:
            fname = os.path.join(self.path, self.spec_filename)
            with open(fname, "w") as f:
                f.write("\n".join(lines))
                print("wrote SPEC file: " + fname)

    def prepare_file_contents(self):
        """
        write the SPEC data file
        
        buffer all content in memory before writing the file
        """
        dt = datetime.datetime.fromtimestamp(self.spec_epoch)
        lines = []
        lines.append("#F " + self.spec_filename)
        lines.append("#E " + str(self.spec_epoch))
        lines.append("#D " + datetime.datetime.strftime(dt, "%c"))
        lines.append("#C " + self.spec_comment)
        # TODO: #O line(s)

        lines.append("")
        lines.append("#S " + self.scan_command)
        lines.append("#D " + datetime.datetime.strftime(dt, "%c"))
        if self.T_or_M is not None:
            lines.append("#{} {}".format(self.T_or_M, self.T_or_M_value))
            self.T_or_M = "T"
            self.T_or_M_value = 1

        # TODO: #P line(s)
        for v in self.comments["start"]:
            lines.append("#C " + v)
        for v in self.comments["descriptor"]:
            lines.append("#C " + v)

        for k, v in self.metadata.items():
            # "#MD" is our ad hoc SPEC data tag
            lines.append("#MD {} = {}".format(k, v))

        lines.append("#N " + str(self.num_primary_data))
        if len(self.data.keys()) > 0:
            lines.append("#L " + "  ".join(self.data.keys()))
            for i in range(self.num_primary_data):
                s = [str(self.data[k][i]) for k in self.data.keys()]
                lines.append(" ".join(s))
        else:
            lines.append("#C no data column labels identified")

        for v in self.comments["event"]:
            lines.append("#C " + v)

        for v in self.comments["stop"]:
            lines.append("#C " + v)
        
        return lines
