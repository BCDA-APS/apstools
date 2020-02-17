
"""
add spec-style comments

.. autosummary::
   
   ~spec_comment
"""

__all__ = ["spec_comment",]

import logging
logger = logging.getLogger(__name__)

from .shell import ipython_shell_namespace


def spec_comment(comment, doc=None, writer=None):
    """
    make it easy to add spec-style comments in a custom plan
    
    These comments *only* go into the SPEC data file.

    Parameters

    comment : string, optional
        Comment text to be written.  SPEC expects it to be only one line!

    doc : string, optional (default: ``event``)
        Bluesky RunEngine document type.
        One of: ``start descriptor event resource datum stop``

    writer : obj, optional
        Instance of ``SpecWriterCallback()``, 
        typically: ``specwriter = SpecWriterCallback()``
    
    EXAMPLE:
    
    Execution of this plan (with ``RE(myPlan())``)::

        def myPlan():
            yield from bps.open_run()
            spec_comment("this is a start document comment", "start")
            spec_comment("this is a descriptor document comment", "descriptor")
            yield bps.Msg('checkpoint')
            yield from bps.trigger_and_read([scaler])
            spec_comment("this is an event document comment after the first read")
            yield from bps.sleep(2)
            yield bps.Msg('checkpoint')
            yield from bps.trigger_and_read([scaler])
            spec_comment("this is an event document comment after the second read")
            spec_comment("this is a stop document comment", "stop")
            yield from bps.close_run()

    results in this SPEC file output::

        #S 1145  myPlan()
        #D Mon Jan 28 12:48:09 2019
        #C Mon Jan 28 12:48:09 2019.  plan_type = generator
        #C Mon Jan 28 12:48:09 2019.  uid = ef98648a-8e3a-4e7e-ac99-3290c9b5fca7
        #C Mon Jan 28 12:48:09 2019.  this is a start document comment
        #C Mon Jan 28 12:48:09 2019.  this is a descriptor document comment
        #MD APSTOOLS_VERSION = 2019.0103.0+5.g0f4e8b2
        #MD BLUESKY_VERSION = 1.4.1
        #MD OPHYD_VERSION = 1.3.0
        #MD SESSION_START = 2019-01-28 12:19:25.446836
        #MD beamline_id = developer
        #MD ipython_session_start = 2018-02-14 12:54:06.447450
        #MD login_id = mintadmin@mint-vm
        #MD pid = 21784
        #MD proposal_id = None
        #N 2
        #L Epoch_float  scaler_time  Epoch
        1.4297869205474854 1.1 1
        4.596935987472534 1.1 5
        #C Mon Jan 28 12:48:11 2019.  this is an event document comment after the first read
        #C Mon Jan 28 12:48:14 2019.  this is an event document comment after the second read
        #C Mon Jan 28 12:48:14 2019.  this is a stop document comment
        #C Mon Jan 28 12:48:14 2019.  num_events_primary = 2
        #C Mon Jan 28 12:48:14 2019.  exit_status = success

    """
    ns = ipython_shell_namespace()
    writer = writer or ns.get("specwriter") # instance of SpecWriterCallback()
    if writer is None:
        raise ValueError("Cannot find SpecWriterCallback() instance.")
    if doc is None:
        if writer.scanning:
            doc = "event"
        else:
            doc = "start"
    for line in comment.splitlines():
        writer._cmt(doc, line)
