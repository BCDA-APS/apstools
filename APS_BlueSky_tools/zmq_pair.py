#/usr/bin/env python

"""
Python ZeroMQ pair connection example

:see: http://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/patterns/pair.html
:seealso: https://stackoverflow.com/questions/23855563/simple-client-server-zmq-in-python-to-send-multiple-lines-per-request
"""

# Copyright (c) 2017-, UChicago Argonne, LLC.  See LICENSE file.

# example that shows polling for input
# http://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/multisocket/zmqpoller.html


import collections
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
    
    def receive_json(self):
        return self.socket.recv_json()
    
    def send(self, chunk):
        return self.socket.send(chunk)
    
    def send_json(self, chunk):
        return self.socket.send_json(chunk)
    
    def send_string(self, msg):
        return self.socket.send_string(str(msg))
    
    def end(self):
        """send an "end" message to the other end of the ZMQ pair"""
        #self.send_string(self.eot_signal_text.decode())
        self.send_json({"key": "end", 
                        "document": self.eot_signal_text.decode()})


_cache_ = {}


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


def mona_zmq_sender(
        sender, key, 
        document, 
        detector, 
        signal_name=None,
        rotation_name=None):
    '''
    send documents from BlueSky events for the MONA project via a ZMQ pair
    
    This is the ZMQ client end of the pipe
    
    This code is called from a BlueSky callback
    
    .. TODO: EXAMPLE::
    
        --update-- --needed--
    
    It may be faster for the ZMQ receiver to pick up the image 
    from EPICS directly but by passing the image with a BlueSky 
    event, BlueSky can synchronize the image with the associated 
    rotation angle.  Also, when BlueSky gathers and sends all 
    the information, the client needs only a minimum number of 
    support packages to support the pipe (zmq) and packaging 
    protocols (json).
    '''
    global _cache_
    sender.send_json({"key": key, 
                      "document": document})
    if key == "start":
        _cache_ = {}
        uid = document["uid"]
        nm = key + "_" + uid[:8]
        _cache_["prescan_phase"] = True
        _cache_["primary_descriptor_uid"] = None
        _cache_[nm] = document
    elif key == "descriptor":
        uid = document["uid"]
        nm = key + "_" + uid[:8]
        _cache_[nm] = document
        if document.get("name") == 'primary':
            _cache_["primary_descriptor_uid"] = uid
    elif key == "event" and None not in (detector, signal_name, rotation_name):
        primary_descriptor_uid = _cache_.get("primary_descriptor_uid")
        if document["descriptor"] == primary_descriptor_uid:
            # do not send images in prescan phase
            _cache_["prescan_phase"] = False

        # only certain events have the rotation angle
        rotation = document["data"].get(rotation_name)
        if rotation is not None:
            # cache the rotation angle and its timestamp
            _cache_["rotation"] = rotation
            ts = document["timestamps"].get(rotation_name)
            _cache_["rotation_time"] = ts

        if _cache_.get("prescan_phase", True):
            return

        image_number = document["data"].get(signal_name)
        rotation = _cache_.get("rotation")
        if None in (image_number, rotation):
            return

        rotation_time = _cache_["rotation_time"]
        image_time = document["timestamps"].get(signal_name)
        MOTOR_STILL_TOO_LONG_s = 0.1
        if image_time - rotation_time > MOTOR_STILL_TOO_LONG_s:
            return

        # pump out the image
        sender.socket.send_json(
            dict(
                key = "image",
                dtype = str(detector.image.dtype),
                shape = detector.image.shape,
                image_timestamp = image_time,
                rotation = _cache_["rotation"],
                rotation_timestamp = rotation_time,
                document = "... see next message ...",

            ), zmq.SNDMORE
        )
        # binary image is not serializable in JSON, send separately
        sender.socket.send(detector.image)
    elif key == "stop":
        _cache_ = {}


def mona_zmq_receiver(filename):
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
        md = listener.receive_json()
        key = md.get("key")
        if key is None:
            print("no 'key' in message")
            continue
        if key == "start":
            print(key, md["document"])
        elif key == "descriptor":
            print(key, md["document"])
        elif key == "event":
            # print(key, md["document"])
            pass
        elif key == "image":
            #print(key, md)
            dtype = md["dtype"]
            shape = md["shape"]
            image = memoryview(listener.receive())
            image = numpy.frombuffer(image, dtype=dtype).reshape(shape)
            print("image", md["rotation"], md["image_timestamp"]-md["rotation_timestamp"])
        elif key == "bulk_events":
            #print(key, md["document"])
            pass
        elif key == "stop":
            print(key, md["document"])
        elif key == "end":
            # TODO: verify with md["document"] == listener.eot_signal_text
            # BUT document is str while listener.eot_signal_text is bytes
            print("EOT received")
            # TODO: should we disconnect()?
            break
    print("Connection ended")


def __PREVIOUS__mona_zmq_receiver(filename):
    """
    receive documents from BlueSky events for the MONA project
    
    This is the ZMQ server end of the pipe
    
    create a ZMQ pair server before starting BlueSky
    
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
        get messages from 0MQ and convert them back to original form
        
        Messages are in the form of (key, buffer) pairs
        where key is one of (start descriptor event stop bulk_events image)
        and buffer is json for all except image, which is binary data.
        """
        # TODO: Can ZMQ tell us if the connection has been dropped?
        msg = listener.receive()
        if str(msg) == str(listener.eot_signal_text):
            # TODO: propagate end() message to clients
            return ()
        key = msg.decode()
        if key in ("start", "descriptor", "event", "stop", "bulk_events"):
            document = listener.receive().decode()
            try:
                return key, json.loads(document)
            except Exception as msg:
                print(msg)
                return ()
        elif key == "image":
            s = listener.receive().decode().rstrip(')').lstrip('(').split(',')
            shape = tuple(map(int, s))
            dtype = listener.receive().decode()
            image_number = int(listener.receive().decode())
            image_timestamp = float(listener.receive().decode())
            rotation = float(listener.receive().decode())
            rotation_timestamp = float(listener.receive().decode())

            # see: https://stackoverflow.com/questions/28995937/convert-python-byte-string-to-numpy-int#28996024
            image = listener.receive()
            image = numpy.fromstring(image, dtype=dtype).reshape(shape)
            return key, {
                "image": image,
                "image_number": image_number,
                "image_timestamp": image_timestamp,
                "rotation": rotation,
                "rotation_timestamp": rotation_timestamp}

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
    
    doc_stream = []
    
    while True:
        try:
            results = process_message()
        except Exception as msg:
            print(msg)
            continue
        if len(results) == 0:
            # TODO: propagate end() message to clients
            break
        key, document = results
        if key == "start":
            uid = document["uid"]
            entry_name = "entry_" + uid[:8]
            local_image_number = 0

            nexus = h5py.File(filename, "a")
            nexus.attrs["default"] = entry_name

            nxentry = nexus.create_group(entry_name)
            nxentry.attrs["NX_class"] = "NXentry"
            nxentry.attrs["default"] = "data"
            ds = nxentry.create_dataset("experiment_identifier", data=uid)
            ds.attrs["meaning"] = "UUID"

            docs_group = nxentry.require_group("BlueSky_document_stream")
            docs_group.attrs["NX_class"] = "NXnote"

            item_name = key+"_" + document["uid"][:8]
            doc_stream.append(item_name)
            nxnote = docs_group.create_group(item_name)
            nxnote.attrs["NX_class"] = "NXnote"
            nxnote.create_dataset("json", data=json.dumps(document))

            nxdata = nxentry.create_group("data")
            nxdata.attrs["NX_class"] = "NXdata"
        elif key == "stop":
            item_name = key+"_" + document["uid"][:8]
            doc_stream.append(item_name)
            nxnote = docs_group.create_group(item_name)
            nxnote.attrs["NX_class"] = "NXnote"
            nxnote.create_dataset("json", data=json.dumps(document))
            docs_group.attrs["document_sequence"] = "\n".join(doc_stream)
            nexus.close()
            doc_stream = []
        elif key in ("event", "descriptor"):
            item_name = key+"_" + document["uid"][:8]
            doc_stream.append(item_name)
            nxnote = docs_group.create_group(item_name)
            nxnote.attrs["NX_class"] = "NXnote"
            nxnote.create_dataset("json", data=json.dumps(document))
        elif key == "image":
            data_name = "image_{}".format(local_image_number)
            try:
                ds = nxdata.create_dataset(
                    data_name, 
                    data = document["image"],
                    compression = hdf5_data_compression,
                    )
            except ValueError as err:
                print("err", err)
                print("image size", len(document["image"]))
                print("compression", hdf5_data_compression)
                continue
            ds.attrs["units"] = "counts"
            ds.attrs["local_image_number"] = local_image_number
            ds.attrs["AD_image_number"] = document["image_number"]
            ds.attrs["image_timestamp"] = document["image_timestamp"]
            ds.attrs["rotation"] = document["rotation"]
            ds.attrs["rotation_timestamp"] = document["rotation_timestamp"]
            if local_image_number == 0:
                nxdata.attrs["signal"] = data_name
            local_image_number += 1
        else:
            pass

    print("\n 0MQ server stopped listening")


if __name__ == "__main__":
    mona_zmq_receiver("/tmp/mona_receiver.hdf5")
#     server_example()
