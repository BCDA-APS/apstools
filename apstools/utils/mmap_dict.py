"""
MMap
====

A dictionary where the keys are also accessible as attributes.
"""

from collections.abc import MutableMapping


class MMap(MutableMapping):
    """
    Dictionary with keys accessible as attributes (read-only).

    All keys are accessible for read and write by dictionary-style references
    ('mmap["key"]' or 'mmap.get(key)').

    Since dictionary keys are accessible as attributes, the names of existing
    attributes (such as 'clear', 'items', keys', values', ...) are reserved and
    cannot be used as dictionary keys.

    EXAMPLE::

        >>> mmap = MMap(a=1, b=2)
        >>> mmap
        MMap(a=1, b=2)
        >>> mmap["a]
        1
        >>> mmap["a"] = 2
        >>> mmap.a
        2
        >>> mmap.a = 3
        AttributeError: Unknown: attribute='a'
        >>> mmap
        MMap(a=2, b=2)
        >>> mmap["clear"] = 5
        KeyError: "key='clear' is a reserved name."
    """

    _db = {}
    attribute_names = dir(dict) + "_db".split()

    def __init__(self, **kwargs):
        self.clear()
        self.update(**kwargs)

    def clear(self):
        self._db = {}

    def __delitem__(self, key):
        del self._db[key]

    def __dir__(self):
        all = dir(super())
        all += "_db clear update keys items values get pop popitem".split()
        all += list(self)
        return sorted(set(all))

    def __getattr__(self, key):
        return self._db[key]

    def __getitem__(self, key):
        return self._db[key]

    def __iter__(self):
        yield from self._db

    def __len__(self):
        return len(self._db)

    def __repr__(self):
        d = ", ".join([f"{k}={v!r}" for k, v in self._db.items()])
        return f"{self.__class__.__name__}({d})"

    def __setattr__(self, attribute, value):
        if attribute not in self.attribute_names:
            raise AttributeError(f"Unknown: {attribute=!r}")
        super().__setattr__(attribute, value)

    def __setitem__(self, key, value):
        if key in self.attribute_names:
            raise KeyError(f"{key=!r} is a reserved name.")
        self._db[key] = value
