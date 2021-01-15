#!/usr/bin/env pytest

import socket


def is_aps_workstation():
    return socket.getfqdn().endswith(".aps.anl.gov")
