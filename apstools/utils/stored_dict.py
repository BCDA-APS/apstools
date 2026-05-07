"""
Save/restore for the `RE.md` dictionary
=======================================

To save and restore metadata between Python sessions, we provide
:class:`~apstools.utils.stored_dict.StoredDict`.  This support is used to save
the contents of ``RE.md`` in a YAML file when this dictionary is changed.

.. autosummary::
   :nosignatures:

   ~StoredDict

.. rubric:: Example

Setup :class:`~apstools.utils.stored_dict.StoredDict()` to write the contents
of ``RE.md`` to file ``".re.md_dict.yml"`` (in the present working directory):

.. code-block: python
    :linenos:

    RE = bluesky.RunEngine()
    RE.md = StoredDict(".re.md_dict.yml")

Within seconds of changing any key in the ``RE.md`` dictionary, the entire
dictionary contents will be written to the file.

.. note:: Only changes to the top level of `RE.md` will trigger the file
    to be updated.  Changes to lower-level structure will not trigger updates.

.. note:: The YAML file is only loaded on initial use.
    It is not intended for :class:`~apstools.utils.stored_dict.StoredDict()` to be
    used to share information between multiple instances (such as two simulataneous
    Bluesky sessions, each writing to the same file).

    To share the ``scan_id`` (so that it increases in a monotonic sequence)
    between multiple sessions, consider using an EPICS PV
    :class:`~apstools.devices.epics_scan_id_signal.EpicsScanIdSignal()`.

.. tip:: The file could be stored in the present working directory
    (of the bluesky session) or could be in any directory (absolute or
    relative) to which the session has write access.

.. tip:: The storage model (YAML) could be changed to something else
    (such as EPICS PV) by changing these two static methods:
    :meth:`~apstools.utils.stored_dict.StoredDict.dump()` and
    :meth:`~apstools.utils.stored_dict.StoredDict.load()`.
"""

import atexit
import collections.abc
import datetime
import json
import pathlib
import threading
import time

import yaml


class StoredDict(collections.abc.MutableMapping):
    """
    A MutableMapping which syncs it contents to storage.

    The contents are stored as a single YAML file.

    When an item is *mutated* it is not written to storage immediately. The
    mapping is written to storage afer a 'delay' period. The 'delay' is
    chosen long enough to allow multiple updates to the mapping before a single
    write but short enough to ensure prompt backup of the mapping.

    Example::

        >>> import bluesky
        >>> RE = bluesky.RunEngine()
        >>> RE.md = StoredDict(".re_md_dict")  # save file in pwd

    .. rubric:: Static methods

    All support for the YAML format is implemented in the static methods.

    .. autosummary::

        ~dump
        ~load

    .. rubric:: Other public methods

    .. autosummary::

        ~flush
        ~popitem
        ~reload
    """

    def __init__(self, file, delay=5, title=None, serializable=True):
        """
        StoredDict : Dictionary that syncs to storage

        PARAMETERS

        file : str or pathlib.Path
            Name of file to store dictionary contents.
        delay : number
            Time delay (s) since last dictionary update to write to storage.
            Default: 5 seconds.
        title : str or None
            Comment to write at top of file.
            Default: "Written by StoredDict."
        serializable : bool
            If True, validate new dictionary entries are JSON serializable.
        """
        self._file = pathlib.Path(file)
        self._delay = max(0, delay)
        self._title = title or f"Written by {self.__class__.__name__}."
        self.test_serializable = serializable

        self.sync_in_progress = False
        self._sync_deadline = time.time()
        self._sync_key = f"sync_agent_{id(self):x}"
        self._sync_loop_period = 0.005

        self._cache = {}
        self.reload()

        # Write to storage (as needed) when process exits.
        atexit.register(self.flush)

    def __delitem__(self, key):
        """Delete dictionary value by key."""
        del self._cache[key]
        self._queue_storage()

    def __getitem__(self, key):
        """Get dictionary value by key."""
        return self._cache[key]

    def __iter__(self):
        """Iterate over the dictionary keys."""
        yield from self._cache

    def __len__(self):
        """Number of keys in the dictionary."""
        return len(self._cache)

    def __repr__(self):
        """representation of this object."""
        return f"<{self.__class__.__name__} {dict(self)!r}>"

    def __setitem__(self, key, value):
        """Write to the dictionary."""
        if self.test_serializable:
            json.dumps({key: value})

        self._cache[key] = value  # Store the new (or revised) content.
        self._queue_storage()

    def _delayed_sync_to_storage(self):
        """
        Sync the metadata to storage.

        Start a time-delay thread.  New writes to the metadata dictionary will
        extend the deadline.  Sync once the deadline is reached.
        """

        def sync_agent():
            """Threaded task."""
            self.sync_in_progress = True
            while time.time() < self._sync_deadline:
                time.sleep(self._sync_loop_period)
            self.sync_in_progress = False

            StoredDict.dump(self._file, self._cache, title=self._title)

        thred = threading.Thread(target=sync_agent)
        thred.start()

    def _queue_storage(self):
        """Set timer to store the revised dict."""
        # Reset the deadline.
        self._sync_deadline = time.time() + self._delay

        if not self.sync_in_progress:
            # Start the sync_agent (thread).
            self._delayed_sync_to_storage()

    def flush(self):
        """Force a write of the dictionary to disk"""
        if not self.sync_in_progress:
            StoredDict.dump(self._file, self._cache, title=self._title)
        self._sync_deadline = time.time()
        self.sync_in_progress = False

    def popitem(self):
        """
        Remove and return a (key, value) pair as a 2-tuple.

        Pairs are returned in LIFO (last-in, first-out) order.
        Raises KeyError if the dict is empty.
        """
        # self._queue_storage()  will be called by self.__delitem__()
        return self._cache.popitem()

    def reload(self):
        """Read dictionary from storage."""
        self._cache = StoredDict.load(self._file)

    @staticmethod
    def dump(file, contents, title=None):
        """Write dictionary to YAML file."""
        with open(file, "w") as f:
            if isinstance(title, str) and len(title) > 0:
                f.write(f"# {title}\n")
            f.write(f"# Dictionary contents written: {datetime.datetime.now()}\n\n")
            f.write(yaml.dump(contents.copy(), indent=2))

    @staticmethod
    def load(file):
        """Read dictionary from YAML file."""
        file = pathlib.Path(file)
        md = None
        if file.exists():
            md = yaml.load(open(file).read(), yaml.Loader)
        return md or {}  # In case file is empty.
