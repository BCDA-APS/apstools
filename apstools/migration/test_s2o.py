#!/usr/bin/env python

"""
test spec2ophyd
"""

import spec2ophyd
import sys


def main():
    cf = "config-CNTPAR"
    sys.argv.append(cf)
    spec2ophyd.main()


if __name__ == "__main__":
    main()
