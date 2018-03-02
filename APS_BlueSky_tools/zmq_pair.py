#/usr/bin/env python

"""
Python ZeroMQ pair connection example

:see: http://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/patterns/pair.html
:seealso: https://stackoverflow.com/questions/23855563/simple-client-server-zmq-in-python-to-send-multiple-lines-per-request
"""

# Copyright (c) 2017-, UChicago Argonne, LLC.  See LICENSE file.

# example that shows polling for input
# http://learning-0mq-with-pyzmq.readthedocs.io/en/latest/pyzmq/multisocket/zmqpoller.html


import json
import numpy
import time
import zmq

__all__ = ['ZMQ_Pair', 'mona_zmq_sender', 'mona_zmq_receiver']

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
            self.send_json(dict(key="connect", client=hostname()))
    
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
        self.send_json({"key": "end", 
                        "document": self.eot_signal_text.decode()})


def hostname():
    import socket
    return socket.gethostname() or 'localhost' 


_cache_ = {}


def mona_zmq_sender(
        sender, key, 
        document, 
        detector, 
        signal_name=None,
        rotation_name=None,
        max_motor_still_time=0.1,
        **kwds
        ):
    '''
    send documents from BlueSky events for the MONA project via a ZMQ pair
    
    This is the ZMQ client end of the pipe
    
    This code is called from a BlueSky callback
    
    PARAMETERS
    
    sender : obj
        instance of ZMQ_Pair()
    key : str
        name of BlueSky stream document
    document : dict
        BlueSky JSON document with stream information
    detector : obj
        ophyd area detector image Device with image data
    signal_name : str
        name of ophyd Signal that notifies a new image is available
    rotation_name : str
        name of ophyd Motor that is the rotation axis
    max_motor_still_time : float
        maximum timestamp difference between (image-motor)
        when images will be sent over the ZMQ connection.
        This suppresses extra images at the end of the scan
        as well as multiple images while the motor waits
        at one location with no updates.
        Default: 0.1 s
        
        .. note:: Likely there is a better way to solve #13 than this.


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
        _cache_[uid] = document

        #sender.socket.send_json(dict(key="DEVELOPER", message=str(document.get("name"))))

        if document.get("name") == 'primary':
            _cache_["primary_descriptor_uid"] = uid
    elif key == "event" and None not in (detector, signal_name, rotation_name):
        primary_descriptor_uid = _cache_.get("primary_descriptor_uid")
        #sender.socket.send_json(
        #    dict(
        #        key="DEVELOPER", 
        #        message="event document",
        #        descriptor_name=_cache_[document["descriptor"]]
        #        )
        #    )
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
            # No image?, No angle? nothing to do.
            return

        rotation_time = _cache_["rotation_time"]
        image_time = document["timestamps"].get(signal_name)

        if (image_time - rotation_time) > max_motor_still_time:
            # motor has not updated in a while, no image
            return

        # sender.socket.send_json(dict(key="DEVELOPER", message="image next"))

        # pump out the image
        sender.socket.send_json(
            dict(
                key = "image",
                dtype = str(detector.image.dtype),
                shape = detector.image.shape,
                image_number = image_number,
                image_timestamp = image_time,
                sending_timestamp = time.time(),
                rotation = _cache_["rotation"],
                rotation_timestamp = rotation_time,
                document = "... see next message ...",

            ), zmq.SNDMORE
        )
        # binary image is not serializable in JSON, send separately
        sender.socket.send(detector.image)
    elif key == "stop":
        _cache_ = {}


def mona_zmq_receiver(*args, **kwds):
    """receive data from BlueSky data acquisition"""
    listener = ZMQ_Pair()
    print("0MQ server Listening now: {}".format(str(listener)))
    print("  host: {}".format(listener.host))
    print("  port: {}".format(listener.port))
    print("  addr: {}".format(listener.addr))
    print("  serverhost: {}".format(hostname()))
    print("#"*40)
    stream = None

    while True:
        md = listener.receive_json()
        key = md.get("key")
        if key is None:
            print("no 'key' in message")
            continue
        if key == "start":
            #print(key, md["document"])
            uid = md["document"]["uid"]
            fname = "/tmp/{}.txt".format(uid[:8])
            stream = []
            stream.append((key, md["document"]))
        elif key == "descriptor":
            #print(key, md["document"])
            if stream is not None:
                stream.append((key, md["document"]))
        elif key == "event":
            if stream is not None:
                stream.append((key, md["document"]))
                # print(key, md["document"])
                pass
        elif key == "image":
            md["receiving_timestamp"] = time.time()
            #print(key, md)
            dtype = md["dtype"]
            shape = md["shape"]
            #print("... getting image ...")
            image = memoryview(listener.receive())
            image = numpy.frombuffer(image, dtype=dtype).reshape(shape)
            print("image", 
                  md["image_number"],
                  "%.6f" % md["rotation"], 
                  "%.4f" % (md["image_timestamp"]-md["rotation_timestamp"]))
            if stream is not None:
                stream.append((key, md))
        elif key == "bulk_events":
            if stream is not None:
                stream.append((key, md))
            #print(key, md["document"])
            pass
        elif key == "stop":
            #print(key, md["document"])
            if stream is not None:
                stream.append((key, md["document"]))
                with open(fname, "w") as fp:
                    for entry in stream:
                        key, doc = entry
                        fp.write(key + " " + str(json.dumps(doc)) + "\n")
                stream = None
                print("wrote", fname)
        elif key == "end":
            # TODO: should we disconnect()?
            break
        elif key == "connect":
            print("  client: {}".format(md["client"]))
            print("#"*40)
        else:
            print("!!!! md: {}".format(json.dumps(md)))
    print("Connection ended")


if __name__ == "__main__":
    mona_zmq_receiver()
