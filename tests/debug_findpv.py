"""
examine the execution of utils.findpv()

needs a connection to PVs, of course
"""

from apstools.utils import findpv
import ophyd

m1 = ophyd.EpicsMotor("gp:m1", name="m1")


def main():
    choices = findpv("gp:m1.RBV")
    print(f"{choices = }")


if __name__ == "__main__":
    main()
