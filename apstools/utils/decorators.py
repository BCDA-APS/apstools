
"""
support for Python decorator functions

.. autosummary::
   
   ~run_in_thread
"""

__all__ = ["run_in_thread",]

import logging
logger = logging.getLogger(__name__)

import threading


def run_in_thread(func):
    """
    (decorator) run ``func`` in thread
    
    USAGE::

       @run_in_thread
       def progress_reporting():
           logger.debug("progress_reporting is starting")
           # ...
       
       #...
       progress_reporting()   # runs in separate thread
       #...

    """
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return wrapper
