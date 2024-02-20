"""
Request user input in a plan
++++++++++++++++++++++++++++

.. autosummary::

   ~request_input

Wrap ``bps.input_plan()`` to *ask* the user a question.
"""

import bluesky.plan_stubs as bps


def request_input(msg="", default="n", agree="y", bypass=False):
    """
    Request input from the user.  Returns ``True`` if confirmed.

    Return whether (lower case) the response from user (or default) starts with the text
    of ``agree`` or ``bypass is True``.

    PARAMETERS

    msg str:
        Message text to be printed.
        (default: ``""``)
    default str:
        Default response if user accepts default.
        (default: ``"n"``)
    agree (str or list):
        User (or default) response must start with this text for ``True``. If a
        list of strings is provided, response must match (lower case) one of the
        strings in the list.
        (default: ``"y"``)
    bypass bool:
        Allow for automated plans to bypass this request in-place.
        (default: ``False``)

    New in release 1.6.6
    """
    match = False
    if not bypass:
        #  note: caller should write ``msg`` to show the value(s) that match ``agree``
        full_text = f"{msg} [{default}] "
        r = yield from bps.input_plan(full_text)
        print(f"Response: {r = }")
        if len(r) == 0:
            r = default
        r = r.lower()
        if isinstance(agree, str):
            match = r.startswith(agree)
        elif isinstance(agree, list):
            match = r in [str(l).lower() for l in agree]
        else:
            raise TypeError(f"Unhandled type: agree={agree}")
    return bypass or match


# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2024, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
