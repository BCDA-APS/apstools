#!/usr/bin/env python

"""
develop spec2ophyd
"""

import os
from . import spec2ophyd
import sys


def main():
    cf = os.path.join(os.path.dirname(__file__), "config-MOTPAR")
    sys.argv.append(cf)
    spec2ophyd.main()


if __name__ == "__main__":
    main()
