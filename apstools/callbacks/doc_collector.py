"""
Document Collector
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~DocumentCollectorCallback
   ~document_contents_callback
"""

import logging
from typing import Any, Dict, List, Union

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def document_contents_callback(key: str, doc: dict[str, Any]) -> None:
    """
    prints document contents -- use for diagnosing a document stream
    """
    print(key)
    for k, v in doc.items():
        print(f"\t{k}\t{v}")


class DocumentCollectorCallback(object):
    """
    Bluesky callback to collect *all* documents from most-recent plan

    .. index:: Bluesky Callback; DocumentCollectorCallback

    Will reset when it receives a *start* document.

    EXAMPLE::

        from apstools.callbacks import DocumentCollectorCallback
        doc_collector = DocumentCollectorCallback()
        RE.subscribe(doc_collector.receiver)
        ...
        RE(some_plan())
        print(doc_collector.uids)
        print(doc_collector.documents["stop"])

    """

    data_event_names: list[str] = "descriptor event resource datum bulk_events".split()

    def __init__(self) -> None:
        self.documents: dict[str, Union[dict[str, Any], list[dict[str, Any]]]] = {}  # key: name, value: document
        self.uids: list[str] = []  # chronological list of UIDs as-received

    def receiver(self, key: str, document: dict[str, Any]) -> None:
        """keep all documents from recent plan in memory"""
        token = document.get("uid") or document.get("datum_id")
        if token is None:
            raise KeyError("No uid in '{}' document".format(key))
        self.uids.append(token)
        logger = logging.getLogger(__name__)
        logger.debug("%s document  uid=%s", key, str(token))  # lgtm [py/clear-text-logging-sensitive-data]
        if key == "start":
            self.documents = {key: document}
        elif key in self.data_event_names:
            if key not in self.documents:
                self.documents[key] = []
            self.documents[key].append(document)
        elif key == "stop":
            self.documents[key] = document
            print("exit status:", document["exit_status"])
            for item in self.data_event_names:
                if item in self.documents:
                    print(f"# {len(self.documents[item])}(s):")
        else:
            txt = "custom_callback encountered: %s\n%s"
            logger.warning(txt, key, document)
            if key not in self.documents:
                self.documents[key] = []
            self.documents[key].append(document)
        return


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
