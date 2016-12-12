"""
Custom structures for sending and receiving event messages
"""
from ctypes import Structure, c_int
from .netlink import nlmsghdr
from .connector import cn_msg
from .cn_proc import proc_event

#custom types
class event_msg(Structure):
    """
    shared structure between request and response types
    """
    _fields_ = [
        ("hdr",nlmsghdr),
        ("msg",cn_msg)
    ]

class event_req_msg(Structure):
    """
    Request message
    """
    _fields_ = [
        ("req",event_msg),
        ("op",c_int)
    ]

class event_res_msg(Structure):
    """
    Response message
    """
    _fields_ = [
        ("res",event_msg),
        ("event",proc_event)
    ]
