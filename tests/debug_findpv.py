"""
examine the execution of utils.findpv()

needs a connection to PVs, of course
"""

import apstools.utils
import ophyd
import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(__file__, "..")
    )
)


class MyCam(ophyd.SimDetectorCam):
    pool_max_buffers = None


class MyDetector(ophyd.SimDetector):
    cam = ophyd.ADComponent(MyCam, "cam1:")


def main():
    gpm1=ophyd.EpicsMotor("gp:m1", name="gpm1")
    simdet = MyDetector("ad:", name="simdet")
    gpm1.wait_for_connection()
    simdet.wait_for_connection()
    ns = dict(m1=gpm1, simdet=simdet)
    print(f'{apstools.utils.findpv("gp:m1.RBV", ns=ns) = }')
    print(f'{apstools.utils.findpv("ad:cam1:Acquire", ns=ns) = }')


if __name__ == "__main__":
    main()
