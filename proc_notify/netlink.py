"""
Structures from netlink.h
"""
from ctypes import Structure,c_uint32,c_uint16

#netlink.h types
NLMSG_NOOP=0x1
NLMSG_ERROR=0x2
NLMSG_DONE=0x3
NLMSG_OVERRUN=0x4

class nlmsghdr(Structure):
    _fields_=[
        ("nlmsg_len",c_uint32),
        ("nlmsg_type",c_uint16),
        ("nlmsg_flags",c_uint16),
        ("nlmsg_seq",c_uint32),
        ("nlmsg_pid",c_uint32)
    ]
