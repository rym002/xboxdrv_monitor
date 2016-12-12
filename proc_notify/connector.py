"""
Structures from connector.h
"""
from ctypes import Structure,c_uint32,c_uint16,c_uint8

#connector.h types
CN_IDX_PROC=0x1
CN_VAL_PROC=0x1

class cb_id(Structure):
    _fields_=[
        ("idx",c_uint32),
        ("val",c_uint32)
    ]

class cn_msg(Structure):
    _fields_=[
        ("id",cb_id),
        ("seq",c_uint32),
        ("ack",c_uint32),
        ("len",c_uint16),
        ("flags",c_uint16),
        ("data",c_uint8 * 0)
    ]

