"""
MMap
====

A dictionary where the keys are also accessible as attributes.
"""

from collections.abc import MutableMapping
from typing import Any
from typing import Iterator


class MMap(MutableMapping[str, Any]):
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

    You can retrieve the value of a key by any of these dictionary methods::

        mmap["a"]
        mmap.get("a")
        # Or supply a default if the key does not exist.
        # Here, the default is 1.2345
        mmap.get("a", 1.2345)

    and by any attribute method::

        mmap.a
        getattr(mmap, "a")
        # Or supply a default if the key does not exist.
        getattr(mmap, "a", 1.2345)
    """

    _db: dict[str, Any] = {}
    attribute_names: list[str] = dir(dict) + "_db".split()

    def __init__(self, **kwargs: Any) -> None:
        self.clear()
        self.update(**kwargs)

    def clear(self) -> None:
        self._db = {}

    def __delitem__(self, key: str) -> None:
        del self._db[key]

    def __dir__(self) -> list[str]:
        all = dir(super())
        all += "_db clear update keys items values get pop popitem".split()
        all += list(self)
        return sorted(set(all))

    def __getattr__(self, key: str) -> Any:
        return self._db[key]

    def __getitem__(self, key: str) -> Any:
        return self._db[key]

    def __iter__(self) -> Iterator[str]:
        yield from self._db

    def __len__(self) -> int:
        return len(self._db)

    def __repr__(self) -> str:
        d = ", ".join([f"{k}={v!r}" for k, v in self._db.items()])
        return f"{self.__class__.__name__}({d})"

    def __setattr__(self, attribute: str, value: Any) -> None:
        if attribute not in self.attribute_names:
            raise AttributeError(f"Unknown: {attribute=!r}")
        super().__setattr__(attribute, value)

    def __setitem__(self, key: str, value: Any) -> None:
        if key in self.attribute_names:
            raise KeyError(f"{key=!r} is a reserved name.")
        self._db[key] = value
