#/usr/bin/env python

"""
Python ZeroMQ pair connection example

:see: http://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/patterns/pair.html
:seealso: https://stackoverflow.com/questions/23855563/simple-client-server-zmq-in-python-to-send-multiple-lines-per-request
"""

# Copyright (c) 2017-, UChicago Argonne, LLC.  See LICENSE file.

# example that shows polling for input
# http://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/multisocket/zmqpoller.html


import numpy
import zmq

__all__ = ['ZMQ_Pair', 'server_example', 'client_example']


class ZMQ_Pair(object):
    """
    example 0MQ Pair connection: one server, only one client
    """
    
    port = "5556"
    socket_type = zmq.PAIR
    host = "*"
    eot_signal_text = b"END OF TRANSMISSION"
    eot_signal_text = b"HANGUP"
    
    def __init__(self, host=None, port=None):
        self.port = str(port or self.port)
        self.host=host or self.host
        
        kw = dict(host=self.host, port=self.port)
        self.addr = "tcp://{host}:{port}".format(**kw)
        
        self.context = zmq.Context()
        self.socket = self.context.socket(self.socket_type)
        if self.host == "*":
            self.socket.bind(self.addr)
        else:
            self.socket.connect(self.addr)
    
    def receive(self):
        return self.socket.recv()
    
    def send_string(self, msg):
        self.socket.send_string(str(msg))
    
    def send(self, chunk):
        self.socket.send(chunk)
    
    def end(self):
        """send an "end" message to the other end of the ZMQ pair"""
        self.send_string(self.eot_signal_text.decode())


def server_example():
    """
    ::
    
        from zmq_pair import server_example
        server_example()
    
    """
    from zmq_pair import ZMQ_Pair
    import socket

    listener = ZMQ_Pair()
    print("0MQ server Listening now: {}".format(str(listener)))
    print("  host: {}".format(listener.host))
    print("  port: {}".format(listener.port))
    print("  addr: {}".format(listener.addr))
    serverhost = socket.gethostname() or 'localhost' 
    print("  serverhost: {}".format(serverhost))
    print("#"*40)
    while True:
        msg = listener.receive()
        #print(msg.decode())
        if len(msg) < 12:
            print(type(msg), msg.decode())
        else:
            print(type(msg), "length={}".format(len(msg)))
        if str(msg) == str(listener.eot_signal_text):
            break
    print("\n 0MQ server stopped listening")


def client_example(filename, host=None):
    """
    ::

        from zmq_pair import client_example
        client_example("zmq_pair.py")   # on localhost
        # or
        client_example("zmq_pair.py", "10.0.2.2") # on VM

    """
    from zmq_pair import ZMQ_Pair

    talker = ZMQ_Pair(host or "localhost")
    print("Starting 0MQ client: {}".format(str(talker)))
    print("  host: {}".format(talker.host))
    print("  port: {}".format(talker.port))
    print("  addr: {}".format(talker.addr))
    print("#"*40)
    # send this file over 0mq as an example
    with open(filename, 'r') as f:
        for line in f:
            talker.send_string(line.rstrip("\n"))
    talker.send_string(talker.eot_signal_text.decode())
    print("\nEnding 0MQ client")


def mona_zmq_sender(sender, key, document, detector):
    '''
    send documents from BlueSky events for the MONA project via a ZMQ pair
    
    This code is called from a BlueSky callback
    
    EXAMPLE::
    
        from ophyd import SingleTrigger, SimDetector, ImagePlugin
        from APS_BlueSky_tools.zmq_pair import ZMQ_Pair, mona_zmq_sender
        
        class MyPlainSimDetector(SimDetector, SingleTrigger):
            image = Component(ImagePlugin, suffix="image1:")

        class MonaCallback0MQ(object):
           """
           My BlueSky 0MQ talker to send *all* documents emitted
           """
           
           def __init__(self, host=None, port=None, detector=None):
               self.talker = ZMQ_Pair(host or "localhost", port or "5556")
               self.detector = detector
           
           def end(self):
               """ZMQ client tells the server to end the connection"""
               self.talker.end()
        
           def receiver(self, key, document):
               """receive from RunEngine, send from 0MQ talker"""
               mona_zmq_sender(self.talker, key, document, self.detector)
       
        zmq_talker = MonaCallback0MQ(detector=plainsimdet.image)
        RE.subscribe(zmq_talker.receiver)
        adsimple = MyPlainSimDetector('13SIM1:', name='adsimple')
        adsimple.read_attrs = ['cam']
        RE(bp.count([adsimple], num=2))
        RE(bp.count([adsimple], num=5))
        zmq_talker.end()
    
    '''
    import json
    sender.send_string(key)
    sender.send_string(json.dumps(document))
    if key == "event" and detector is not None:
        # Is it faster to pick this up by EPICS CA?
        # Using 0MQ, no additional library is needed
        image = detector.image
        sender.send_string("image")
        sender.send_string(str(image.shape))
        sender.send_string(str(image.dtype))
        sender.send(image)
    

def mona_zmq_receiver(filename):
    """
    create a ZMQ pair server to receive documents from BlueSky events for the MONA project
    
    This code runs on the data processing stream computer *before* BlueSky starts.
    The BlueSky callback will attempt to connect with this server as a client
    using the ZMQ PAIR protocol.  BlueSky will then emit documents,
    some of which contain images to be reconstructed, until BlueSky sends an
    "end" document signalling this server that no more events will be sent.
    
    This example code writes the collected images into a NeXus HDF5 data file.
    Drop that for production, it's just a demo and diagnostic.
    
    EXAMPLE::
    
        mona_zmq_receiver("/tmp/mona_receiver.hdf5")
    
    """
    from zmq_pair import ZMQ_Pair
    import datetime
    import h5py
    import json
    import socket
    
    hdf5_data_compression = "gzip"
    # hdf5_data_compression = "lzf"
    
    def process_message():
        """
        """
        msg = listener.receive()
        if str(msg) == str(listener.eot_signal_text):
            return ()
        key = msg.decode()
        if key in ("start", "descriptor", "event", "stop", "bulk_events"):
            document = listener.receive().decode()
            return key, json.loads(document)
        elif key == "image":
            s = listener.receive().decode().rstrip(')').lstrip('(').split(',')
            shape = tuple(map(int, s))
            dtype = listener.receive().decode()
            # see: https://stackoverflow.com/questions/28995937/convert-python-byte-string-to-numpy-int#28996024
            msg = listener.receive()
            image = numpy.fromstring(msg, dtype=dtype).reshape(shape)
            return key, image

    listener = ZMQ_Pair()
    print("0MQ server Listening now: {}".format(str(listener)))
    print("  host: {}".format(listener.host))
    print("  port: {}".format(listener.port))
    print("  addr: {}".format(listener.addr))
    serverhost = socket.gethostname() or 'localhost' 
    print("  serverhost: {}".format(serverhost))
    print("#"*40)

    nexus = h5py.File(filename, "w")
    nexus.attrs["filename"] = filename
    nexus.attrs["file_time"] = str(datetime.datetime.now())
    nexus.attrs["creator"] = "BlueSky ZMQ Callback"
    nexus.attrs["H5PY_VERSION"] = h5py.__version__
    nexus.close()
    
    while True:
        results = process_message()
        if len(results) == 0:
            break
        key, document = results
        if key == "start":
            uid = document["uid"]
            entry_name = "entry_" + uid[:8]
            image_number = 0

            nexus = h5py.File(filename, "a")
            nexus.attrs["default"] = entry_name

            nxentry = nexus.create_group(entry_name)
            nxentry.attrs["NX_class"] = "NXentry"
            nxentry.attrs["default"] = "data"
            ds = nxentry.create_dataset("experiment_identifier", data=uid)
            ds.attrs["meaning"] = "UUID"

            nxnote = nxentry.create_group(key + "_document")
            nxnote.attrs["NX_class"] = "NXnote"
            nxnote.create_dataset("json", data=json.dumps(document))

            nxdata = nxentry.create_group("data")
            nxdata.attrs["NX_class"] = "NXdata"
        elif key == "stop":
            nxnote = nxentry.create_group(key + "_document")
            nxnote.attrs["NX_class"] = "NXnote"
            nxnote.create_dataset("json", data=json.dumps(document))
            nexus.close()
        elif key in ("event", "descriptor"):
            item_name = key+"_" + document["uid"][:8]
            nxnote = nxentry.create_group(item_name)
            nxnote.attrs["NX_class"] = "NXnote"
            nxnote.create_dataset("json", data=json.dumps(document))
        elif key == "image":
            data_name = "image_{}".format(image_number)
            ds = nxdata.create_dataset(
                data_name, 
                data = document,
                compression = hdf5_data_compression,
                )
            ds.attrs["units"] = "counts"
            if image_number == 0:
                nxdata.attrs["signal"] = data_name
            image_number += 1
        else:
            pass

    print("\n 0MQ server stopped listening")


if __name__ == "__main__":
    mona_zmq_receiver("/tmp/mona_receiver.hdf5")
#     server_example()
