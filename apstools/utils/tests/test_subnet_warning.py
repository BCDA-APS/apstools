import socket
from contextlib import nullcontext as does_not_raise

import pytest

from ..apsu_controls_subnet import APSU_CONTROLS_SUBNET
from ..apsu_controls_subnet import APSU_XRAY_SUBNET
from ..apsu_controls_subnet import warn_if_not_aps_controls_subnet


def test_subnet_check():
    host_name = socket.gethostname()
    host_ip_addr = socket.gethostbyname(host_name)
    # fmt: off
    warns = (
        host_name.endswith(APSU_XRAY_SUBNET)
        and not host_ip_addr.startswith(APSU_CONTROLS_SUBNET)
    )
    # fmt: on
    with pytest.raises(UserWarning) if warns else does_not_raise():
        warn_if_not_aps_controls_subnet()
