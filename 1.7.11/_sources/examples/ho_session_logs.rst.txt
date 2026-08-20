.. _howto_session_logs:

How to setup logging
=======================

Using functions from :mod:`apstools.utils.log_utils`, it is easy to setup
logging [#logging]_ reports to either the console or a file. Refer to the logging
levels, as described in the section :ref:`logging_levels` below.

To setup for logging in your code:

.. code-block:: python
    :linenos:

    import logging
    logger = logging.getLogger(__name__)

You can use this code in any module to create a ``logger`` object. Use one of
the levels such as ``logger.warning("a warning message")`` or
``logger.debug("some detail")`` to add messages for logging.  ``INFO`` and
``DEBUG`` level messages will not be reported unless you adjust the level to
allow this level of detail. To set the level:

.. code-block:: python
    :linenos:

    logger.setLevel(logging.DEBUG)  # allow any log content at this level

Yet still, you may not see any output on your console unless you provide a
*handler* which tells the logger what to do with each message.  A logger has its
own reporting level which determines which messages to report.

.. tip:: Set the logger level to the lowest level of any of the handlers you will use.

In the next sections, we show you how to add handlers.  You can add multiple
handlers to a ``logger`` for different types of reporting.

Handlers
+++++++++++++

Logging handlers describe when, where, and how to report a logging message. The
sections below show how to report to the console and to files. The logging
documentation ([#logging]_) shows how to report to more places. The bluesky
documentation [#bluesky_logging]_ provides debugging and logging guidance.

Reporting to the console (``StreamHandler``)
------------------------------------------------

Starting with the ``logger`` from :ref:`howto_session_logs`, add a handler for
reporting ``INFO`` (and higher) messages to the console.  You can change the
level with a keyword argument, see
:func:`~apstools.utils.log_utils.stream_log_handler()`.

.. code-block:: python
    :linenos:

    logger.addHandler(stream_log_handler())  # logger to the console

Reporting to a file (``FileHandler`` or ``RotatingFileHandler``)
----------------------------------------------------------------------

Starting with the ``logger`` from :ref:`howto_session_logs`, add a handler for
reporting ``DEBUG`` (and higher) messages to the file.  The log file
will be named ``.logs/my_log_file.log`` with up to 9 older
files, each no larger than 1 MB.

.. code-block:: python
    :linenos:

    BYTE = 1
    kB = 1024 * BYTE
    MB = 1024 * kB

    logger.addHandler(
        file_log_handler(  # logger to a file
            "my_log_file,
            maxBytes=1 * MB,
            backupCount=9,
            level="DEBUG",
        )
    )

Reporting from included packages
-----------------------------------

Some of the packages included might report via Python's ``logging`` package. For
example, ``bluesky`` [#bluesky_logging_names]_ and ``ophyd``
[#ophyd_logging_names]_ have several logger names that report messages.  Here,
we enable reporting from the top-level logger names in both these packages:

.. code-block:: python
    :linenos:

    BYTE = 1
    kB = 1024 * BYTE
    MB = 1024 * kB

    log_these_names = {
        "bluesky": "INFO",
        "ophyd": "INFO",
    }
    for logger_name, level in log_these_names.items():
        _l = logging.getLogger(logger_name)
        _l.setLevel(logging.DEBUG)  # allow any log content at this level
        _l.addHandler(
            file_log_handler(  # logger to a file
                logger_name,
                logger_name,
                maxBytes=1 * MB,
                backupCount=9,
                level=level,  # filter reporting to this level
            )
        )

Recording IPython console Input and Output
------------------------------------------

IPython offers its own logging process for recording the input (``IN``) and
output (``OUT``) messages.  When diagnosing problems, or for education reasons,
it is useful to record this content to a file for later review.

This will create a file ``.logs/ipython_console.log`` (relative to
the current working directory) for this log.

.. code-block:: python
    :linenos:

    setup_IPython_console_logging()

.. _logging_levels:

What are the logging levels?
++++++++++++++++++++++++++++++++++

==============  ======================  ========================
text            symbol                  remarks
==============  ======================  ========================
``"CRITICAL"``  ``logging.CRITICAL``    rare for any messages
``"ERROR"``     ``logging.ERROR``
``"WARNING"``   ``logging.WARNING``     default reporting level
``"INFO"``      ``logging.INFO``
``"DEBUG"``     ``logging.DEBUG``       the most verbose level
==============  ======================  ========================

A logging *handler* will report any messages it receives at its current level or
*higher* as shown in this table.  With the default level (``WARNING``), you will
only receive messages from ``logger.critical()``,  ``logger.error()``,
and  ``logger.warning()`` calls.

Simply put, `WARNING` level only reports when something has gone wrong.

The usual practice is to set the ``logger`` (instance of ``logging.Logger``)
to the lowest level used by any handler.

The bluesky documentation ([#flowchart]_) provides a flowchart
illustrating how a log message will be reported by a handler.

-----

References

.. [#bluesky_logging] Bluesky debugging & logging guidance:
    https://blueskyproject.io/bluesky/debugging.html
.. [#bluesky_logging_names] Bluesky logger names:
    https://blueskyproject.io/bluesky/debugging.html
.. [#flowchart] Flowchart for loggers and handlers:
    https://blueskyproject.io/bluesky/debugging.html#advanced-example
.. [#ophyd_logging_names] Ophyd logger names:
    https://blueskyproject.io/bluesky/debugging.html
.. [#logging] Python's *Logging HOWTO*:
    https://docs.python.org/3/howto/logging.html
