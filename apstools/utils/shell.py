
"""
support for shell commands (IPython, unix, ...)

.. autosummary::
   
   ~ipython_profile_name
   ~ipython_shell_namespace
   ~unix
"""

__all__ = """
    ipython_profile_name
    ipython_shell_namespace
    unix
""".split()

import logging
logger = logging.getLogger(__name__)

import subprocess
import sys


def ipython_profile_name():
    """
    return the name of the current ipython profile or `None`
    
    Example (add to default RunEngine metadata)::

        RE.md['ipython_profile'] = str(ipython_profile_name())
        print("using profile: " + RE.md['ipython_profile'])

    """
    from IPython import get_ipython
    return get_ipython().profile


def ipython_shell_namespace():
    """
    get the IPython shell's namespace dictionary (or empty if not found)
    """
    try:
        from IPython import get_ipython
        ns = get_ipython().user_ns
    except AttributeError as _exc:
        ns = {}
    return ns


def unix(command, raises=True):
    """
    run a UNIX command, returns (stdout, stderr)

    PARAMETERS
    
    command: str
        UNIX command to be executed
    raises: bool
        If `True`, will raise exceptions as needed,
        default: `True`
    """
    if sys.platform not in ("linux", "linux2"):
        emsg = f"Cannot call unix() when OS={sys.platform}"
        raise RuntimeError(emsg)

    process = subprocess.Popen(
        command, 
        shell=True,
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        )

    stdout, stderr = process.communicate()

    if len(stderr) > 0:
        emsg = f"unix({command}) returned error:\n{stderr}"
        logger.error(emsg)
        if raises:
            raise RuntimeError(emsg)

    return stdout, stderr
