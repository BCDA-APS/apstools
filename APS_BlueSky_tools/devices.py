
"""
(ophyd) Devices that might be useful at the APS using BlueSky

.. autosummary::
   
    ~ApsMachineParametersDevice
    ~ApsPssShutter
    ~AxisTunerException
    ~AxisTunerMixin
    ~EpicsMotorDialMixin
    ~EpicsMotorServoMixin
    ~EpicsMotorRawMixin
    ~EpicsMotorDescriptionMixin
    ~EpicsMotorShutter
    ~sscanRecord  
    ~sscanDevice
    ~swaitRecord
    ~swait_setup_random_number
    ~swait_setup_gaussian
    ~swait_setup_lorentzian
    ~swait_setup_incrementer
    ~use_EPICS_scaler_channels
    ~userCalcsDevice
    
    ~ApsHDF5Plugin

Internal routines

.. autosummary::

    ~ApsOperatorMessagesDevice
    ~ApsFileStoreHDF5
    ~ApsFileStoreHDF5IterativeWrite

Legacy routines

.. autosummary::
   
    ~EpicsMotorWithDial
    ~EpicsMotorWithServo

"""

# Copyright (c) 2017-2018, UChicago Argonne, LLC.  See LICENSE file.


from collections import OrderedDict
from datetime import datetime
import itertools
import threading
import time

from .synApps_ophyd import *
import ophyd
from ophyd import Component, Device, DeviceStatus, FormattedComponent
from ophyd import Signal, EpicsMotor, EpicsSignal, EpicsSignalRO
from ophyd.scaler import EpicsScaler, ScalerCH
from bluesky.plan_stubs import mv, mvr, abs_set, wait

from ophyd.areadetector.filestore_mixins import FileStoreHDF5
from ophyd.areadetector.filestore_mixins import FileStoreBase
from ophyd.areadetector.filestore_mixins import FileStorePluginBase
from ophyd.areadetector.filestore_mixins import FileStoreIterativeWrite
from ophyd import HDF5Plugin
from ophyd.utils import set_and_wait


def use_EPICS_scaler_channels(scaler):
    """
    configure scaler for only the channels with names assigned in EPICS 
    """
    if isinstance(scaler, EpicsScaler):
        import epics
        read_attrs = []
        for ch in scaler.channels.component_names:
            _nam = epics.caget("{}.NM{}".format(scaler.prefix, int(ch[4:])))
            if len(_nam.strip()) > 0:
                read_attrs.append(ch)
        scaler.channels.read_attrs = read_attrs
    elif isinstance(scaler, ScalerCH):
        read_attrs = []
        for ch in scaler.channels.component_names:
            nm_pv = scaler.channels.__getattribute__(ch)
            if nm_pv is not None and len(nm_pv.chname.value.strip()) > 0:
                read_attrs.append(ch)
        scaler.channels.read_attrs = read_attrs


class ApsOperatorMessagesDevice(Device):
    """general messages from the APS main control room"""
    operators = Component(EpicsSignalRO, "OPS:message1", string=True)
    floor_coordinator = Component(EpicsSignalRO, "OPS:message2", string=True)
    fll_pattern = Component(EpicsSignalRO, "OPS:message3", string=True)
    last_problem_message = Component(EpicsSignalRO, "OPS:message4", string=True)
    last_trip_message = Component(EpicsSignalRO, "OPS:message5", string=True)
    # messages 6-8: meaning?
    message6 = Component(EpicsSignalRO, "OPS:message6", string=True)
    message7 = Component(EpicsSignalRO, "OPS:message7", string=True)
    message8 = Component(EpicsSignalRO, "OPS:message8", string=True)


class ApsMachineParametersDevice(Device):
    """
    common operational parameters of the APS of general interest
    
    USAGE::

        APS = ApsMachineParametersDevice(name="APS")
        aps_current = APS.current

        # make sure these values are logged at start and stop of every scan
        sd.baseline.append(APS)
        # record storage ring current as secondary stream during scans
        # name: aps_current_monitor
        # db[-1].table("aps_current_monitor")
        sd.monitors.append(aps_current)

    The `sd.baseline` and `sd.monitors` usage relies on this global setup:

        from bluesky import SupplementalData
        sd = SupplementalData()
        RE.preprocessors.append(sd)

    """
    current = Component(EpicsSignalRO, "S:SRcurrentAI")
    lifetime = Component(EpicsSignalRO, "S:SRlifeTimeHrsCC")
    machine_status = Component(EpicsSignalRO, "S:DesiredMode", string=True)
    operating_mode = Component(EpicsSignalRO, "S:ActualMode", string=True)
    shutter_permit = Component(EpicsSignalRO, "ACIS:ShutterPermit", string=True)
    fill_number = Component(EpicsSignalRO, "S:FillNumber")
    orbit_correction = Component(EpicsSignalRO, "S:OrbitCorrection:CC")
    global_feedback = Component(EpicsSignalRO, "SRFB:GBL:LoopStatusBI", string=True)
    global_feedback_h = Component(EpicsSignalRO, "SRFB:GBL:HLoopStatusBI", string=True)
    global_feedback_v = Component(EpicsSignalRO, "SRFB:GBL:VLoopStatusBI", string=True)
    operator_messages = Component(ApsOperatorMessagesDevice)


class ApsPssShutter(Device):
    """
    APS PSS shutter
    
    * APS PSS shutters have separate bit PVs for open and close
    * set either bit, the shutter moves, and the bit resets a short time later
    * no indication that the shutter has actually moved from the bits
      (see :func:`ApsPssShutterWithStatus()` for alternative)
    
    USAGE:
    
        shutter_a = ApsPssShutter("2bma:A_shutter", name="shutter")
        
        shutter_a.open()
        shutter_a.close()
        
        shutter_a.set("open")
        shutter_a.set("close")
        
    When using the shutter in a plan, be sure to use `yield from`.

        def in_a_plan(shutter):
            yield from abs_set(shutter, "open", wait=True)
            # do something
            yield from abs_set(shutter, "close", wait=True)
        
        RE(in_a_plan(shutter_a))
        
    The strings accepted by `set()` are defined in two lists:
    `valid_open_values` and `valid_close_values`.  These lists
    are treated (internally to `set()`) as lower case strings.
    
    Example, add "o" & "x" as aliases for "open" & "close":
    
        shutter_a.valid_open_values.append("o")
        shutter_a.valid_close_values.append("x")
        shutter_a.set("o")
        shutter_a.set("x")
    """
    open_bit = Component(EpicsSignal, ":open")
    close_bit = Component(EpicsSignal, ":close")
    delay_s = 1.2
    valid_open_values = ["open",]   # lower-case strings ONLY
    valid_close_values = ["close",]
    busy = Signal(value=False, name="busy")
    
    def open(self):
        """request shutter to open, interactive use"""
        self.open_bit.put(1)
    
    def close(self):
        """request shutter to close, interactive use"""
        self.close_bit.put(1)
    
    def set(self, value, **kwargs):
        """request the shutter to open or close, BlueSky plan use"""
        # ensure numerical additions to lists are now strings
        def input_filter(v):
            return str(v).lower()
        self.valid_open_values = list(map(input_filter, self.valid_open_values))
        self.valid_close_values = list(map(input_filter, self.valid_close_values))
        
        if self.busy.value:
            raise RuntimeError("shutter is operating")

        acceptables = self.valid_open_values + self.valid_close_values
        if input_filter(value) not in acceptables:
            msg = "value should be one of " + " | ".join(acceptables)
            msg += " : received " + str(value)
            raise ValueError(msg)
        
        status = DeviceStatus(self)
        
        def move_shutter():
            if input_filter(value) in self.valid_open_values:
                self.open()     # no need to yield inside a thread
            elif input_filter(value) in self.valid_close_values:
                self.close()
        
        def run_and_delay():
            self.busy.put(True)
            move_shutter()
            # sleep, since we don't *know* when the shutter has moved
            time.sleep(self.delay_s)
            self.busy.put(False)
            status._finished(success=True)
        
        threading.Thread(target=run_and_delay, daemon=True).start()
        return status


class ApsPssShutterWithStatus(Device):
    """
    APS PSS shutter
    
    * APS PSS shutters have separate bit PVs for open and close
    * set either bit, the shutter moves, and the bit resets a short time later
    * a separate status PV tells if the shutter is open or closed
      (see :func:`ApsPssShutter()` for alternative)
    
    USAGE:
    
        A_shutter = ApsPssShutterWithStatus(
            "2bma:A_shutter", 
            "PA:02BM:STA_A_FES_OPEN_PL", 
            name="A_shutter")
        B_shutter = ApsPssShutterWithStatus(
            "2bma:B_shutter", 
            "PA:02BM:STA_B_SBS_OPEN_PL", 
            name="B_shutter")
        
        A_shutter.open()
        A_shutter.close()
        
        or
        
        %mov A_shutter "open"
        %mov A_shutter "close"
        
        or
        
        A_shutter.set("open")       # MUST be "open", not "Open"
        A_shutter.set("close")
        
    When using the shutter in a plan, be sure to use `yield from`.

        def in_a_plan(shutter):
            yield from abs_set(shutter, "open", wait=True)
            # do something
            yield from abs_set(shutter, "close", wait=True)
        
        RE(in_a_plan(A_shutter))
        
    The strings accepted by `set()` are defined in attributes
    (`open_str` and `close_str`).
    """
    open_bit = Component(EpicsSignal, ":open")
    close_bit = Component(EpicsSignal, ":close")
    pss_state = FormattedComponent(EpicsSignalRO, "{self.state_pv}")

    # strings the user will use
    open_str = 'open'
    close_str = 'close'

    # pss_state PV values from EPICS
    open_val = 1
    close_val = 0

    def __init__(self, prefix, state_pv, *args, **kwargs):
        self.state_pv = state_pv
        super().__init__(prefix, *args, **kwargs)

    def open(self, timeout=10):
        ophyd.status.wait(self.set(self.open_str), timeout=timeout)

    def close(self, timeout=10):
        ophyd.status.wait(self.set(self.close_str), timeout=timeout)

    def set(self, value, **kwargs):
        # first, validate the input value
        acceptables = (self.close_str, self.open_str)
        if value not in acceptables:
            msg = "value should be one of " + " | ".join(acceptables)
            msg += " : received " + str(value)
            raise ValueError(msg)

        command_signal = {
            self.open_str: self.open_bit, 
            self.close_str: self.close_bit
        }[value]
        expected_value = {
            self.open_str: self.open_val, 
            self.close_str: self.close_val
        }[value]

        working_status = DeviceStatus(self)
        
        def shutter_cb(value, timestamp, **kwargs):
            # APS shutter state PVs do not define strings, use numbers
            #value = enums[int(value)]
            value = int(value)
            if value == expected_value:
                self.pss_state.clear_sub(shutter_cb)
                working_status._finished()
        
        self.pss_state.subscribe(shutter_cb)
        command_signal.set(1)
        return working_status


class AxisTunerException(ValueError): 
    """Exception during execution of `AxisTunerBase` subclass"""
    pass


class AxisTunerMixin(object):
    """
    Mixin class to provide tuning capabilities for an axis
    
    USAGE::
    
        class TunableEpicsMotor(EpicsMotor, AxisTunerMixin):
            pass
        
        def a2r_pretune_hook():
            # set the counting time for *this* tune
            yield from bps.abs_set(scaler.preset_time, 0.2)
            
        a2r = TunableEpicsMotor("xxx:m1", name="a2r")
        a2r.tuner = TuneAxis([scaler], a2r, signal_name=scaler.channels.chan2.name)
        a2r.tuner.width = 0.02
        a2r.tuner.num = 21
        a2r.pre_tune_method = a2r_pretune_hook
        RE(a2r.tune())
        
        # tune four of the USAXS axes (using preconfigured parameters for each)
        RE(tune_axes([mr, m2r, ar, a2r])

    HOOK METHODS
    
    There are two hook methods (`pre_tune_method()`, and `post_tune_method()`)
    for callers to add additional plan parts, such as opening or closing shutters, 
    setting detector parameters, or other actions.
    
    Each hook method must accept one argument: 
    axis object such as `EpicsMotor` or `SynAxis`,
    such as::
    
        def my_pre_tune_hook(axis):
            yield from bps.mv(shutter, "open")
        def my_post_tune_hook(axis):
            yield from bps.mv(shutter, "close")
        
        class TunableSynAxis(SynAxis, AxisTunerMixin):
            pass

        myaxis = TunableSynAxis(name="myaxis")
        mydet = SynGauss('mydet', myaxis, 'myaxis', center=0.21, Imax=0.98e5, sigma=0.127)
        myaxis.tuner = TuneAxis([mydet], myaxis)
        myaxis.pre_tune_method = my_pre_tune_hook
        myaxis.post_tune_method = my_post_tune_hook
        
        RE(myaxis.tune())

    """
    
    def __init__(self):
        self.tuner = None   # such as: APS_BlueSky_tools.plans.TuneAxis
        
        # Hook functions for callers to add additional plan parts
        # Each must accept one argument: axis object such as `EpicsMotor` or `SynAxis`
        self.pre_tune_method = self._default_pre_tune_method
        self.post_tune_method = self._default_post_tune_method
    
    def _default_pre_tune_method(self):
        """called before `tune()`"""
        print("{} position before tuning: {}".format(self.name, self.position))

    def _default_post_tune_method(self):
        """called after `tune()`"""
        print("{} position after tuning: {}".format(self.name, self.position))

    def tune(self, md=None, **kwargs):
        if self.tuner is None:
            msg = "Must define an axis tuner, none specified."
            msg += "  Consider using APS_BlueSky_tools.plans.TuneAxis()"
            raise AxisTunerException(msg)
        
        if self.tuner.axis is None:
            msg = "Must define an axis, none specified."
            raise AxisTunerException(msg)

        if md is None:
            md = OrderedDict()
        md["purpose"] = "tuner"
        md["datetime"] = str(datetime.now())

        if self.tuner is not None:
            if self.pre_tune_method is not None:
                self.pre_tune_method()

            yield from self.tuner.tune(md=md, **kwargs)
    
            if self.post_tune_method is not None:
                self.post_tune_method()


class EpicsMotorDialMixin(object):
    """
    add motor record's dial coordinate fields
    
    USAGE::
    
        class myEpicsMotor(EpicsMotor, EpicsMotorDialMixin): pass
        m1 = myEpicsMotor('xxx:m1', name='m1')
    
    """
    
    dial = Component(EpicsSignal, ".DRBV", write_pv=".DVAL")


class EpicsMotorWithDial(EpicsMotor, EpicsMotorDialMixin):
    """
    add motor record's dial coordinates to EpicsMotor
    
    USAGE::
    
        m1 = EpicsMotorWithDial('xxx:m1', name='m1')
    
    This is legacy support.  For new work, use `EpicsMotorDialMixin`.
    """
    pass


class EpicsMotorServoMixin(object):
    """
    add motor record's servo loop controls
    
    USAGE::
    
        class myEpicsMotor(EpicsMotor, EpicsMotorServoMixin): pass
        m1 = myEpicsMotor('xxx:m1', name='m1')
    
    """
    
    # values: "Enable" or "Disable"
    servo = Component(EpicsSignal, ".CNEN", string=True)


class EpicsMotorWithServo(EpicsMotor, EpicsMotorServoMixin):
    """
    extend basic motor support to enable/disable the servo loop controls
    
    USAGE::
    
        m1 = EpicsMotorWithDial('xxx:m1', name='m1')
    
    This is legacy support.  For new work, use `EpicsMotorServoMixin`.
    """
    pass


class EpicsMotorRawMixin(object):
    """
    add motor record's raw coordinate fields
    
    USAGE::
    
        class myEpicsMotor(EpicsMotor, EpicsMotorRawMixin): pass
        m1 = myEpicsMotor('xxx:m1', name='m1')
    
    """
    
    raw = Component(EpicsSignal, ".RRBV", write_pv=".RVAL")


class EpicsMotorDescriptionMixin(object):
    """
    add motor record's description field
    
    USAGE::
    
        class myEpicsMotor(EpicsMotor, EpicsMotorDescriptionMixin): pass
        m1 = myEpicsMotor('xxx:m1', name='m1')
    
    """
    
    desc = Component(EpicsSignal, ".DESC")


class EpicsMotorShutter(Device):
    """
    a shutter, implemented with an EPICS motor moved between two positions
    
    USAGE::

        tomo_shutter = EpicsMotorShutter("2bma:m23", name="tomo_shutter")
        tomo_shutter.closed_position = 1.0      # default
        tomo_shutter.open_position = 0.0        # default
        tomo_shutter.open()
        tomo_shutter.close()
        
        # or, when used in a plan
        def planA():
            yield from abs_set(tomo_shutter, "open", group="O")
            yield from wait("O")
            yield from abs_set(tomo_shutter, "close", group="X")
            yield from wait("X")
        def planA():
            yield from abs_set(tomo_shutter, "open", wait=True)
            yield from abs_set(tomo_shutter, "close", wait=True)
        def planA():
            yield from mv(tomo_shutter, "open")
            yield from mv(tomo_shutter, "close")

    """
    motor = Component(EpicsMotor, "")
    closed_position = 1.0
    open_position = 0.0
    _tolerance = 0.01
    
    def isopen(self):
        return abs(self.motor.position - self.open_position) <= self._tolerance
    
    def isclosed(self):
        return abs(self.motor.position - self.closed_position) <= self._tolerance
    
    def open(self):
        """move motor to BEAM NOT BLOCKED position, interactive use"""
        self.motor.move(self.open_position)
    
    def close(self):
        """move motor to BEAM BLOCKED position, interactive use"""
        self.motor.move(self.closed_position)

    def set(self, value, *, timeout=None, settle_time=None):
        """
        `set()` is like `put()`, but used in BlueSky plans

        PARAMETERS
        
        value : "open" or "close"

        timeout : float, optional
            Maximum time to wait. Note that set_and_wait does not support
            an infinite timeout.

        settle_time: float, optional
            Delay after the set() has completed to indicate completion
            to the caller

        RETURNS
        
        status : DeviceStatus
        """

        # using put completion:
        # timeout and settle time is handled by the status object.
        status = DeviceStatus(
            self, timeout=timeout, settle_time=settle_time)

        def put_callback(**kwargs):
            status._finished(success=True)

        if value.lower() == "open":
            pos = self.open_position
        elif value.lower() == "close":
            pos = self.closed_position
        else:
            msg = "value should be either open or close"
            msg + " : received " + str(value)
            raise ValueError(msg)
        self.motor.user_setpoint.put(
            pos, use_complete=True, callback=put_callback)

        return status


# AreaDetector support


class ApsFileStoreHDF5(FileStorePluginBase):
    """
    custom class to define image file name from EPICS

    To allow users to control the file name,
    we override the ``make_filename()`` method here
    and we need to override some intervening classes.

    To allow users to control the file number,
    we override the ``stage()`` method here
    and triple-comment out that line, and bring in
    sections from the methods we are replacing here.

    The image file name is set in `FileStoreBase.make_filename()` 
    from `ophyd.areadetector.filestore_mixins`.  This is called 
    (during device staging) from `FileStoreBase.stage()`

    To use this custom class, we need to connect it to some
    intervening structure:

    ====================================  ============================
    custom class                          superclass(es)
    ====================================  ============================
    ``ApsFileStoreHDF5``                  ``FileStorePluginBase`
    ``ApsFileStoreHDF5IterativeWrite``    ``ApsFileStoreHDF5`, `FileStoreIterativeWrite`
    ``ApsHDF5Plugin``                     ``HDF5Plugin`, `ApsFileStoreHDF5IterativeWrite`
    ====================================  ============================
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filestore_spec = 'AD_HDF5'  # spec name stored in resource doc
        self.stage_sigs.update([
            ('file_template', '%s%s_%4.4d.h5'),
            ('file_write_mode', 'Stream'),
            ('capture', 1)
        ])

    def make_filename(self):
        """
        overrides default behavior: Get info from EPICS HDF5 plugin.
        """
        # start of the file name, file number will be appended per template
        filename = self.file_name.value
        
        # this is where the HDF5 plugin will write the image, 
        # relative to the IOC's filesystem
        write_path = self.file_path.value
        
        # this is where the DataBroker will find the image, 
        # on a filesystem accessible to BlueSky
        read_path = write_path

        return filename, read_path, write_path

    def generate_datum(self, key, timestamp, datum_kwargs):
        "Generate a uid and cache it with its key for later insertion."
        template = self.file_template.get()
        filename, read_path, write_path = self.make_filename()
        file_number = self.file_number.get()
        hdf5_file_name = template % (read_path, filename, file_number)

        # inject the actual name of the HDF5 file here into datum_kwargs
        datum_kwargs["HDF5_file_name"] = hdf5_file_name
        
        # print("make_filename:", hdf5_file_name)
        return super().generate_datum(key, timestamp, datum_kwargs)

    def get_frames_per_point(self):
        return self.num_capture.get()

    def stage(self):
        # Make a filename.
        filename, read_path, write_path = self.make_filename()

        # Ensure we do not have an old file open.
        set_and_wait(self.capture, 0)
        # These must be set before parent is staged (specifically
        # before capture mode is turned on. They will not be reset
        # on 'unstage' anyway.
        set_and_wait(self.file_path, write_path)
        set_and_wait(self.file_name, filename)
        ### set_and_wait(self.file_number, 0)
        
        # get file number now since it is incremented during stage()
        file_number = self.file_number.get()
        # Must avoid parent's stage() since it sets file_number to 0
        # Want to call grandparent's stage()
        #super().stage()     # avoid this - sets `file_number` to zero
        # call grandparent.stage()
        FileStoreBase.stage(self)

        # AD does the file name templating in C
        # We can't access that result until after acquisition
        # so we apply the same template here in Python.
        template = self.file_template.get()
        self._fn = template % (read_path, filename, file_number)
        self._fp = read_path
        if not self.file_path_exists.get():
            raise IOError("Path %s does not exist on IOC."
                          "" % self.file_path.get())

        # from FileStoreIterativeWrite.stage()
        self._point_counter = itertools.count()
        
        # from FileStoreHDF5.stage()
        res_kwargs = {'frame_per_point': self.get_frames_per_point()}
        self._generate_resource(res_kwargs)


class ApsFileStoreHDF5IterativeWrite(ApsFileStoreHDF5, FileStoreIterativeWrite):
    """custom class to enable users to control image file name"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FileStoreIterativeWrite.__init__(self, *args, **kwargs)


class ApsHDF5Plugin(HDF5Plugin, ApsFileStoreHDF5IterativeWrite):
    """
    custom class to take image file names from EPICS
    
    NOTE: replaces standard Bluesky algorithm where file names
       are defined as UUID strings, virtually guaranteeing that 
       no existing images files will ever be overwritten.
       *Caveat emptor* applies here.  You assume some expertise!
    
    USAGE::

        class MySimDetector(SingleTrigger, SimDetector):
            '''SimDetector with HDF5 file names specified by EPICS'''
            
            cam = ADComponent(MyAltaCam, "cam1:")
            image = ADComponent(ImagePlugin, "image1:")
            
            hdf1 = ADComponent(
                ApsHDF5Plugin, 
                suffix = "HDF1:", 
                root = "/",
                write_path_template = "/local/data",
                )

        simdet = MySimDetector("13SIM1:", name="simdet")
        # remove this so array counter is not set to zero each staging
        del simdet.hdf1.stage_sigs["array_counter"]
        simdet.hdf1.stage_sigs["file_template"] = '%s%s_%3.3d.h5'
        simdet.hdf1.file_path.put("/local/data/demo/")
        simdet.hdf1.file_name.put("test")
        simdet.hdf1.array_counter.put(0)
        RE(bp.count([simdet]))

    """
