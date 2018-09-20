"""
Plans that might be useful at the APS when using BlueSky

.. autosummary::
   
   ~nscan
   ~ProcedureRegistry
   ~run_blocker_in_plan
   ~run_in_thread
   ~TuneAxis
   ~tune_axes

"""

# Copyright (c) 2017-2018, UChicago Argonne, LLC.  See LICENSE file.

from collections import OrderedDict
import datetime
import logging
import numpy as np 
import threading
import time

from bluesky import preprocessors as bpp
from bluesky import plan_stubs as bps
from bluesky import plans as bp
from bluesky.callbacks.fitting import PeakStats
import ophyd
from ophyd import Device, Component, Signal


logger = logging.getLogger(__name__).addHandler(logging.NullHandler())


def run_in_thread(func):
    """
    (decorator) run ``func`` in thread
    
    USAGE::

       @run_in_thread
       def progress_reporting():
           logger.debug("progress_reporting is starting")
           # ...
       
       #...
       progress_reporting()   # runs in separate thread
       #...

    """
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper


def run_blocker_in_plan(blocker, *args, _poll_s_=0.01, _timeout_s_=None, **kwargs):
    """
    run blocking function ``blocker_(*args, **kwargs)`` from a Bluesky plan
    
    blocker (func) : function object to be called in a Bluesky plan

    _poll_s_ (float) : sleep interval in loop while waiting for completion (default: 0.01)

    _timeout_s_ (float) : maximum time for completion (default: `None` which means no timeout)
    
    Example (using ``time.sleep`` as blocking function)::
    
        RE(run_blocker_in_plan(time.sleep, 2.14))

    Example (within a plan, using ``time.sleep`` as blocking function)::

        def my_sleep(t=1.0):
            yield from run_blocker_in_plan(time.sleep, t)

        RE(my_sleep())

    """
    status = ophyd.status.Status()
    
    @run_in_thread
    def _internal(blocking_function, *args, **kwargs):
        blocking_function(*args, **kwargs)
        status._finished(success=True, done=True)
    
    if _timeout_s_ is not None:
        t_expire = time.time() + _timeout_s_

    # FIXME: how to keep this from running during summarize_plan()?
    _internal(blocker, *args, **kwargs)

    while not status.done:
        if _timeout_s_ is not None:
            if time.time() > t_expire:
                status._finished(success=False, done=True)
                break
        yield from bps.sleep(_poll_s_)
    return status


def nscan(detectors, *motor_sets, num=11, per_step=None, md=None):
    """
    Scan over ``n`` variables moved together, each in equally spaced steps.

    PARAMETERS

    detectors : list
        list of 'readable' objects
    motor_sets : list
        sequence of one or more groups of: motor, start, finish
    motor : object
        any 'settable' object (motor, temp controller, etc.)
    start : float
        starting position of motor
    finish : float
        ending position of motor
    num : int
        number of steps (default = 11)
    per_step : callable, optional
        hook for customizing action of inner loop (messages per step)
        Expected signature: ``f(detectors, step_cache, pos_cache)``
    md : dict, optional
        metadata
    """
    def take_n_at_a_time(args, n=2):
        yield from zip(*[iter(args)]*n)
        
    if len(motor_sets) < 3:
        raise ValueError("must provide at least one movable")
    if len(motor_sets) % 3 > 0:
        raise ValueError("must provide sets of movable, start, finish")

    motors = OrderedDict()
    for m, s, f in take_n_at_a_time(motor_sets, n=3):
        if not isinstance(s, (int, float)):
            msg = "start={} ({}): is not a number".format(s, type(s))
            raise ValueError(msg)
        if not isinstance(f, (int, float)):
            msg = "finish={} ({}): is not a number".format(f, type(f))
            raise ValueError(msg)
        motors[m.name] = dict(motor=m, start=s, finish=f, 
                              steps=np.linspace(start=s, stop=f, num=num))

    _md = {'detectors': [det.name for det in detectors],
           'motors': [m for m in motors.keys()],
           'num_points': num,
           'num_intervals': num - 1,
           'plan_args': {'detectors': list(map(repr, detectors)), 
                         'num': num,
                         'motors': repr(motor_sets),
                         'per_step': repr(per_step)},
           'plan_name': 'nscan',
           'plan_pattern': 'linspace',
           'hints': {},
           'iso8601': datetime.datetime.now(),
           }
    _md.update(md or {})

    try:
        m = list(motors.keys())[0]
        dimensions = [(motors[m]["motor"].hints['fields'], 'primary')]
    except (AttributeError, KeyError):
        pass
    else:
        _md['hints'].setdefault('dimensions', dimensions)

    if per_step is None:
        per_step = bps.one_nd_step

    @bpp.stage_decorator(list(detectors) 
                         + [m["motor"] for m in motors.values()])
    @bpp.run_decorator(md=_md)
    def inner_scan():
        for step in range(num):
            step_cache, pos_cache = {}, {}
            for m in motors.values():
                next_pos = m["steps"][step]
                m = m["motor"]
                pos_cache[m] = m.read()[m.name]["value"]
                step_cache[m] = next_pos
            yield from per_step(detectors, step_cache, pos_cache)

    return (yield from inner_scan())


# def sscan(*args, md=None, **kw):        # TODO: planned
#     """
#     gather data form the sscan record and emit documents
#     
#     Should this operate a complete scan using the sscan record?
#     """
#     raise NotImplemented("this is only planned")


class TuneAxis(object):
    """
    tune an axis with a signal
    
    This class provides a tuning object so that a Device or other entity
    may gain its own tuning process, keeping track of the particulars
    needed to tune this device again.  For example, one could add
    a tuner to a motor stage::
    
        motor = EpicsMotor("xxx:motor", "motor")
        motor.tuner = TuneAxis([det], motor)
    
    Then the ``motor`` could be tuned individually::
    
        RE(motor.tuner.tune(md={"activity": "tuning"}))
    
    or the :meth:`tune()` could be part of a plan with other steps.
    
    Example::
    
        tuner = TuneAxis([det], axis)
        live_table = LiveTable(["axis", "det"])
        RE(tuner.multi_pass_tune(width=2, num=9), live_table)
        RE(tuner.tune(width=0.05, num=9), live_table)

    .. autosummary::
       
       ~tune
       ~multi_pass_tune
       ~peak_detected

    """
    
    _peak_choices_ = "cen com".split()
    
    def __init__(self, signals, axis, signal_name=None):
        self.signals = signals
        self.signal_name = signal_name or signals[0].name
        self.axis = axis
        self.stats = {}
        self.tune_ok = False
        self.peaks = None
        self.peak_choice = self._peak_choices_[0]
        self.center = None
        self.stats = []
        
        # defaults
        self.width = 1
        self.num = 10
        self.step_factor = 4
        self.pass_max = 6
        self.snake = True

    def tune(self, width=None, num=None, md=None):
        """
        BlueSky plan to execute one pass through the current scan range
        
        Scan self.axis centered about current position from
        ``-width/2`` to ``+width/2`` with ``num`` observations.
        If a peak was detected (default check is that max >= 4*min), 
        then set ``self.tune_ok = True``.

        PARAMETERS
    
        width : float
            width of the tuning scan in the units of ``self.axis``
            Default value in ``self.width`` (initially 1)
        num : int
            number of steps
            Default value in ``self.num`` (initially 10)
        md : dict, optional
            metadata
        """
        width = width or self.width
        num = num or self.num
        
        if self.peak_choice not in self._peak_choices_:
            msg = "peak_choice must be one of {}, geave {}"
            msg = msg.format(self._peak_choices_, self.peak_choice)
            raise ValueError(msg)

        initial_position = self.axis.position
        final_position = initial_position       # unless tuned
        start = initial_position - width/2
        finish = initial_position + width/2
        self.tune_ok = False

        tune_md = dict(
            width = width,
            initial_position = self.axis.position,
            time_iso8601 = str(datetime.datetime.now()),
            )
        _md = {'tune_md': tune_md,
               'plan_name': self.__class__.__name__ + '.tune',
               'tune_parameters': dict(
                    num = num,
                    width = width,
                    initial_position = self.axis.position,
                    peak_choice = self.peak_choice,
                    x_axis = self.axis.name,
                    y_axis = self.signal_name,
                   ),
               'hints': dict(
                   dimensions = [
                       (
                           [self.axis.name], 
                           'primary')]
                   )
               }
        _md.update(md or {})
        if "pass_max" not in _md:
            self.stats = []
        self.peaks = PeakStats(x=self.axis.name, y=self.signal_name)
        
        class Results(Device):
            """because bps.read() needs a Device or a Signal)"""
            tune_ok = Component(Signal)
            initial_position = Component(Signal)
            final_position = Component(Signal)
            center = Component(Signal)
            # - - - - -
            x = Component(Signal)
            y = Component(Signal)
            cen = Component(Signal)
            com = Component(Signal)
            fwhm = Component(Signal)
            min = Component(Signal)
            max = Component(Signal)
            crossings = Component(Signal)
            peakstats_attrs = "x y cen com fwhm min max crossings".split()
            
            def report(self):
                keys = self.peakstats_attrs + "tune_ok center initial_position final_position".split()
                for key in keys:
                    print("{} : {}".format(key, getattr(self, key).value))

        @bpp.subs_decorator(self.peaks)
        def _scan(md=None):
            yield from bps.open_run(md)

            position_list = np.linspace(start, finish, num)
            signal_list = list(self.signals)
            signal_list += [self.axis,]
            for pos in position_list:
                yield from bps.mv(self.axis, pos)
                yield from bps.trigger_and_read(signal_list)
            
            final_position = initial_position
            if self.peak_detected():
                self.tune_ok = True
                if self.peak_choice == "cen":
                    final_position = self.peaks.cen
                elif self.peak_choice == "com":
                    final_position = self.peaks.com
                else:
                    final_position = None
                self.center = final_position

            # add stream with results
            # yield from add_results_stream()
            stream_name = "PeakStats"
            results = Results(name=stream_name)

            for key in "tune_ok center".split():
                getattr(results, key).put(getattr(self, key))
            results.final_position.put(final_position)
            results.initial_position.put(initial_position)
            for key in results.peakstats_attrs:
                getattr(results, key).put(getattr(self.peaks, key))

            yield from bps.create(name=stream_name)
            yield from bps.read(results)
            yield from bps.save()
            
            yield from bps.mv(self.axis, final_position)
            self.stats.append(self.peaks)
            yield from bps.close_run()

            results.report()
    
        return (yield from _scan(md=_md))
        
    
    def multi_pass_tune(self, width=None, step_factor=None, 
                        num=None, pass_max=None, snake=None, md=None):
        """
        BlueSky plan for tuning this axis with this signal
        
        Execute multiple passes to refine the centroid determination.
        Each subsequent pass will reduce the width of scan by ``step_factor``.
        If ``snake=True`` then the scan direction will reverse with
        each subsequent pass.

        PARAMETERS
    
        width : float
            width of the tuning scan in the units of ``self.axis``
            Default value in ``self.width`` (initially 1)
        num : int
            number of steps
            Default value in ``self.num`` (initially 10)
        step_factor : float
            This reduces the width of the next tuning scan by the given factor.
            Default value in ``self.step_factor`` (initially 4)
        pass_max : int
            Maximum number of passes to be executed (avoids runaway
            scans when a centroid is not found).
            Default value in ``self.pass_max`` (initially 10)
        snake : bool
            If ``True``, reverse scan direction on next pass.
            Default value in ``self.snake`` (initially True)
        md : dict, optional
            metadata
        """
        width = width or self.width
        num = num or self.num
        step_factor = step_factor or self.step_factor
        snake = snake or self.snake
        pass_max = pass_max or self.pass_max
        
        self.stats = []

        def _scan(width=1, step_factor=10, num=10, snake=True):
            for _pass_number in range(pass_max):
                _md = {'pass': _pass_number+1,
                       'pass_max': pass_max,
                       'plan_name': self.__class__.__name__ + '.multi_pass_tune',
                       }
                _md.update(md or {})
            
                yield from self.tune(width=width, num=num, md=_md)

                if not self.tune_ok:
                    return
                width /= step_factor
                if snake:
                    width *= -1
        
        return (
            yield from _scan(
                width=width, step_factor=step_factor, num=num, snake=snake))
    
    def peak_detected(self):
        """
        returns True if a peak was detected, otherwise False
        
        The default algorithm identifies a peak when the maximum
        value is four times the minimum value.  Change this routine
        by subclassing :class:`TuneAxis` and override :meth:`peak_detected`.
        """
        if self.peaks is None:
            return False
        self.peaks.compute()
        if self.peaks.max is None:
            return False
        
        ymax = self.peaks.max[-1]
        ymin = self.peaks.min[-1]
        return ymax > 4*ymin        # this works for USAXS@APS


def tune_axes(axes):
    """
    BlueSky plan to tune a list of axes in sequence
    """
    for axis in axes:
        yield from axis.tune()


class ProcedureRegistry(ophyd.Device):
    """
    Procedure Registry
    
    With many instruments, such as USAXS,, there are several operating 
    modes to be used, each with its own setup code.  This ophyd Device
    should coordinate those modes so that the setup procedures can be called
    either as part of a Bluesky plan or from the command line directly.

    Assumes that users will write functions to setup a particular 
    operation or operating mode.  The user-written functions may not
    be appropriate to use in a plan directly since they might
    make blocking calls.  The ProcedureRegistry will call the function
    in a thread (which is allowed to make blocking calls) and wait
    for the thread to complete.
    
    It is assumed that each user-written function will not return until
    it is complete.

    .. autosummary::
       
        ~dir
        ~add
        ~remove
        ~set
        ~put

    EXAMPLE::

        use_mode = ProcedureRegistry(name="use_mode")

        def clearScalerNames():
            for ch in scaler.channels.configuration_attrs:
                if ch.find(".") < 0:
                    chan = scaler.channels.__getattribute__(ch)
                    chan.chname.put("")

        def setMyScalerNames():
            scaler.channels.chan01.chname.put("clock")
            scaler.channels.chan02.chname.put("I0")
            scaler.channels.chan03.chname.put("detector")

        def useMyScalerNames(): # Bluesky plan
            yield from bps.mv(
                m1, 5,
                use_mode, "clear",
            )
            yield from bps.mv(
                m1, 0,
                use_mode, "set",
            )

        def demo():
            print(1)
            m1.move(5)
            print(2)
            time.sleep(2)
            print(3)
            m1.move(0)
            print(4)


        use_mode.add(demo)
        use_mode.add(clearScalerNames, "clear")
        use_mode.add(setMyScalerNames, "set")
        # use_mode.set("demo")
        # use_mode.set("clear")
        # RE(useMyScalerNames())

    """
    
    busy = ophyd.Component(ophyd.Signal, value=False)
    registry = {}
    delay_s = 0
    timeout_s = None
    state = "__created__"
    
    @property
    def dir(self):
        """tuple of procedure names"""
        return tuple(sorted(self.registry.keys()))
    
    def add(self, procedure, proc_name=None):
        """
        add procedure to registry
        """
        #if procedure.__class__ == "function":
        nm = proc_name or procedure.__name__
        self.registry[nm] = procedure
    
    def remove(self, procedure):
        """
        remove procedure from registry
        """
        if isinstance(procedure, str):
            nm = procedure
        else:
            nm = procedure.__name__
        if nm in self.registry:
            del self.registry[nm]
    
    def set(self, proc_name):
        """
        run procedure in a thread, return once it is complete
        
        proc_name (str) : name of registered procedure to be run
        """
        if not isinstance(proc_name, str):
            raise ValueError("expected a procedure name, not {}".format(proc_name))
        if proc_name not in self.registry:
            raise KeyError("unknown procedure name: "+proc_name)
        if self.busy.value:
            raise RuntimeError("busy now")
 
        self.state = "__busy__"
        status = ophyd.DeviceStatus(self)
        
        @run_in_thread
        def run_and_delay():
            self.busy.put(True)
            self.registry[proc_name]()
            # optional delay
            if self.delay_s > 0:
                time.sleep(self.delay_s)
            self.busy.put(False)
            status._finished(success=True)
        
        run_and_delay()
        ophyd.status.wait(status, timeout=self.timeout_s)
        self.state = proc_name
        return status
    
    def put(self, value):   # TODO: risky?
        """replaces ophyd Device default put() behavior"""
        self.set(value)
