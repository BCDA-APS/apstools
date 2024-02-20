"""
Document Collector
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~DocumentCollectorCallback
   ~document_contents_callback
"""

import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def document_contents_callback(key, doc):
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

    data_event_names = "descriptor event resource datum bulk_events".split()

    def __init__(self):
        self.documents = {}  # key: name, value: document
        self.uids = []  # chronological list of UIDs as-received

    def receiver(self, key, document):
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
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2024, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
