
"""
collect *all* documents from most-recent plan

.. autosummary::
   
   ~DocumentCollectorCallback
"""

__all__ = ["DocumentCollectorCallback",]


import logging
logger = logging.getLogger(__name__)


class DocumentCollectorCallback(object):
    """
    Bluesky callback to collect *all* documents from most-recent plan
    
    Will reset when it receives a *start* document.
    
    EXAMPLE::
    
        from apstools.callbacks import DocumentCollector
        doc_collector = DocumentCollectorCallback()
        RE.subscribe(doc_collector.receiver)
        ...
        RE(some_plan())
        print(doc_collector.uids)
        print(doc_collector.documents["stop"])
    
    """
    data_event_names = "descriptor event resource datum bulk_events".split()
    
    def __init__(self):
        self.documents = {}     # key: name, value: document
        self.uids = []          # chronological list of UIDs as-received

    def receiver(self, key, document):
        """keep all documents from recent plan in memory"""
        uid = document.get("uid") or document.get("datum_id")
        if uid is None:
            raise KeyError("No uid in '{}' document".format(key))
        self.uids.append(uid)
        logger = logging.getLogger(__name__)
        logger.debug("%s document  uid=%s", key, str(uid))
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
                    print(
                        "# {}(s):".format(item), 
                        len(self.documents[item])
                    )
        else:
            txt = "custom_callback encountered: %s\n%s"
            logger.warning(txt, key, document)
            if key not in self.documents:
                self.documents[key] = []
            self.documents[key].append(document)
        return
