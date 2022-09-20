"""
Support for IPython profiles
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~getDefaultNamespace
   ~ipython_profile_name
   ~ipython_shell_namespace
"""

import logging


logger = logging.getLogger(__name__)


def getDefaultNamespace(attr="user_ns"):
    """
    get the IPython shell's namespace dictionary (or globals() if not found)
    """
    try:
        from IPython import get_ipython

        ns = getattr(get_ipython(), attr)
    except (ModuleNotFoundError, AttributeError):
        ns = globals()
    return ns


def ipython_profile_name():
    """
    return the name of the current ipython profile or ``None``

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
    except AttributeError:
        ns = {}
    return ns

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
