"""
ideas to try with mona

2017-11-09: working on setting up fly scanning
            preparing to fly scan areadetector vs. motor
            all of this (below) works

Also, look at this work with Dan Allan from 2017-07:
https://gist.github.com/danielballan/5cdd4ab1c54a54303ebf1b6e319c101d
analysis server-client sketch
"""

from ophyd.sim import *  # simulated hardware
from bluesky.plans import count
from bluesky.preprocessors import (
   fly_during_wrapper, 
   fly_during_decorator,
   monitor_during_wrapper,
   monitor_during_decorator
   )


RE.unsubscribe(callback_db['zmq_talker'])
del callback_db['zmq_talker']


RE(fly_during_wrapper(count([det], num=5), [flyer1, flyer2]))

fly_and_count = fly_during_decorator([flyer1, flyer2])(count)
RE(fly_and_count([det]))

RE(monitor_during_wrapper(count([det], num=5), [det1]))

monitor_and_count = monitor_during_decorator([det1])(count)
RE(monitor_and_count([det]))

flyerm1 = MockFlyer('flyerm1', det, m1, -2, 0, 20)
RE(fly_during_wrapper(count([det], num=5), [flyerm1,]), None)

def myFlyScan(detectors, motor, start, stop, num=10):
    flymotor = MockFlyer('flymotor', detectors[0], motor, start, stop, num)
    yield from fly_during_wrapper(count(detectors, num=num), [flymotor,])

RE(myFlyScan([det], m1, -2, 0, 5))
