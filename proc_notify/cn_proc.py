"""
    Structures from cn_proc.h
"""
from enum import IntEnum,unique
from ctypes import Structure,Union,c_int,c_uint32,c_uint64,c_char,c_uint

@unique
class proc_cn_mcast_op(IntEnum):
    PROC_CN_MCAST_LISTEN = 1
    PROC_CN_MCAST_IGNORE = 2

class proc_event(Structure):
    @unique
    class ewhat(IntEnum):
        PROC_EVENT_NONE = 0x00000000
        PROC_EVENT_FORK = 0x00000001
        PROC_EVENT_EXEC = 0x00000002
        PROC_EVENT_UID  = 0x00000004
        PROC_EVENT_GID  = 0x00000040
        PROC_EVENT_SID  = 0x00000080
        PROC_EVENT_PTRACE = 0x00000100
        PROC_EVENT_COMM = 0x00000200
        PROC_EVENT_COREDUMP = 0x40000000
        PROC_EVENT_EXIT = 0x80000000

    class event_data_type(Union):
        """
        Union for all event message types
        """
        class ack_type(Structure):
            _fields_=[
                ("err",c_uint32)
            ]
        class fork_proc_event(Structure):
            _fields_=[
                ("parent_pid",c_int),
                ("parent_tgid",c_int),
                ("child_pid",c_int),
                ("child_tgid",c_int)
            ]
        class exec_proc_event(Structure):
            _fields_=[
                ("process_pid",c_int),
                ("process_tgid",c_int)
            ]
        class id_proc_event(Structure):
            class r_type(Union):
                _fields_=[
                    ("ruid",c_uint32),
                    ("rgid",c_uint32)
                ]
            class e_type(Union):
                _fields_=[
                    ("euid",c_uint32),
                    ("egid",c_uint32)
                ]
            _fields_=[
                ("process_pid",c_int),
                ("process_tgid",c_int),
                ("r",r_type),
                ("e",e_type)
            ]
        class sid_proc_event(Structure):
            _fields_=[
                ("process_pid",c_int),
                ("process_tgid",c_int)
            ]
        class ptrace_proc_event(Structure):
            _fields_=[
                ("process_pid",c_int),
                ("process_tgid",c_int),
                ("tracer_pid",c_int),
                ("tracer_tgid",c_int)
            ]
        class comm_proc_event(Structure):
            _pack_=1
            _fields_=[
                ("process_pid",c_int),
                ("process_tgid",c_int),
                ("comm",c_char * 16)
            ]
        class coredump_proc_event(Structure):
            _fields_=[
                ("process_pid",c_int),
                ("process_tgid",c_int)
            ]
        class exit_proc_event(Structure):
            _fields_=[
                ("process_pid",c_int),
                ("process_tgid",c_int),
                ("exit_code",c_uint32),
                ("exit_signal",c_uint32)
            ]

        _fields_=[
            ("ack",ack_type),
            ("fork",fork_proc_event),
            ("exec",exec_proc_event),
            ("id",id_proc_event),
            ("sid",sid_proc_event),
            ("ptrace",ptrace_proc_event),
            ("comm",comm_proc_event),
            ("coredump",coredump_proc_event),
            ("exit",exit_proc_event)
        ]
    _pack_= 1
    _fields_=[
        ("what",c_uint),
        ("cpu",c_uint32),
        ("timestamp_ns",c_uint64),
        ("event_data",event_data_type)
    ]

    _event_mapping_=dict([
        (ewhat.PROC_EVENT_NONE,"ack"),
        (ewhat.PROC_EVENT_FORK,"fork"),
        (ewhat.PROC_EVENT_EXEC,"exec"),
        (ewhat.PROC_EVENT_UID,"id"),
        (ewhat.PROC_EVENT_GID,"id"),
        (ewhat.PROC_EVENT_SID,"sid"),
        (ewhat.PROC_EVENT_PTRACE,"ptrace"),
        (ewhat.PROC_EVENT_COMM,"comm"),
        (ewhat.PROC_EVENT_COREDUMP,"coredump"),
        (ewhat.PROC_EVENT_EXIT,"exit")
        ])

    def get_event_data_field(self):
        return proc_event._event_mapping_[self.what]

    def get_events(self):
        """
        Used to identify all event types and matches the event message
        A single notification can support multiple types
        Returns: generator
        Generator will contain what and event_data
        """
        for proc_what in proc_event.ewhat:
                if proc_what == self.what| proc_what & self.what: 
                    event_data_field = self.get_event_data_field()
                    event_data = getattr(self.event_data,event_data_field)
                    yield proc_what,event_data

