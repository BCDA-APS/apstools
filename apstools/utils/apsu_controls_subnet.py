"""
APS-U controls are on private subnets.  Check and advise as applicable.

.. autosummary::

    ~warn_if_not_aps_controls_subnet
"""

APSU_CONTROLS_SUBNET = "10.54."
APSU_XRAY_SUBNET = ".xray.aps.anl.gov"


def warn_if_not_aps_controls_subnet():
    """
    APS-U controls are on private subnets.  Check and advise as applicable.

    Call this function early in the startup procedure. It could explain easily
    the reason for subsequent EPICS PV connection failures.

    For workstations on subnets that do not match the criteria, this function
    should not post any warnings.
    """

    import socket
    import warnings

    host_name = socket.gethostname()
    if host_name.endswith(APSU_XRAY_SUBNET):
        host_ip_addr = socket.gethostbyname(host_name)
        if not host_ip_addr.startswith(APSU_CONTROLS_SUBNET):
            warnings.warn(
                f"Your APS workstation ({host_name}) has IP {host_ip_addr!r}."
                "  If you experience EPICS connection timeouts,"
                " consider switching to a workstation on the controls subnet"
                f" which has an IP starting with {APSU_CONTROLS_SUBNET!r}"
            )
