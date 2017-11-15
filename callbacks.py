
"""
Callbacks that might be useful at the APS using BlueSky

.. autosummary::
   
   ~DocumentCollectorCallback
   ~ImageZMQCallback

"""

import logging
from zmq_pair import ZMQ_Pair


logger = logging.getLogger(__name__).addHandler(logging.NullHandler())


class DocumentCollectorCallback(object):
    """
    BlueSky callback to collect *all* documents from most-recent plan
    
    Will reset when it receives a *start* document.
    
    EXAMPLE::
    
        doc_collector = DocumentCollectorCallback()
        RE.subscribe(doc_collector)
        ...
        RE(some_plan())
        print(doc_collector.uids)
        print(doc_collector.documents["stop"])
    
    """
    data_event_names = "descriptor event bulk_events".split()
    
    def __init__(self):
        self.documents = {}     # key: name, value: document
        self.uids = []          # chronological list of UIDs as-received

    def receiver(self, key, document):
        """keep all documents from recent plan in memory"""
        if "uid" in document:
            self.uids.append(document["uid"])
        logger = logging.getLogger(__name__)
        logger.debug("{} document  uid={}".format(key, document["uid"]))
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
            txt = "custom_callback encountered: {}\n{}"
            logger.warn(txt.format(key, document))
            if key not in self.documents:
                self.documents[key] = []
            self.documents[key].append(document)
        return


class ImageZMQCallback(object):
    """
    BlueSky callback: send *all* documents through a 0MQ pair connection
    
    note: under development, expected to change frequently without notice
    note: for APS MONA project
    """
    
    def __init__(self, host=None, port=None, detector=None):
        self.talker = ZMQ_Pair(host or "localhost", port or "5556")
        self.detector = detector
    
    def end(self):
        self.talker.send_string(self.talker.eot_signal_text.decode())

    def receiver(self, key, document):
        """receive from RunEngine, send from 0MQ talker"""
        self.talker.send_string(key)
        self.talker.send_string(document)
        if key == "event" and self.detector is not None:
            # other end of 0MQ pair shoudl reconstruct the numpy array 
            # based on the rank and shape
            # image = np.array(bytes).reshape(shape=shape)
            # https://docs.scipy.org/doc/numpy/reference/generated/numpy.reshape.html
            self.talker.send_string("rank")
            self.talker.send_string(str(len(self.detector.image.shape)))
            self.talker.send_string("shape")
            self.talker.send_string(str(self.detector.image.shape))
            self.talker.send_string("image")
            self.talker.send(self.detector.image)
