"""
Handles registering for notification
"""
import socket
import os
from ctypes import sizeof
from .connector import CN_IDX_PROC,CN_VAL_PROC
from .cn_proc import proc_cn_mcast_op
from .msg import *
from .netlink import NLMSG_DONE,NLMSG_NOOP,NLMSG_ERROR,NLMSG_OVERRUN


notify_socket = None
current_cn_mcast_op = None
loop_read_events = True

def setup():
    if getattr(socket, "NETLINK_CONNECTOR", None) is None:
        socket.NETLINK_CONNECTOR = 11

def connect():
    global notify_socket
    setup()
    if notify_socket is None:
        notify_socket = socket.socket(socket.AF_NETLINK, socket.SOCK_DGRAM,
                            socket.NETLINK_CONNECTOR)
        notify_socket.bind((os.getpid(), CN_IDX_PROC))
        notify_socket.settimeout(5)

def set_netlink_header(nl_hdr,req_msg):
    nl_hdr.nlmsg_len = sizeof(req_msg)
    nl_hdr.nlmsg_type = NLMSG_DONE
    nl_hdr.nlmsg_flags = 0
    nl_hdr.nlmsg_seq = 0
    nl_hdr.nlmsg_pid = os.getpid()

def set_cn_msg(req_cn_msg):
    req_cn_id = req_cn_msg.id
    req_cn_id.idx = CN_IDX_PROC
    req_cn_id.val = CN_VAL_PROC
    req_cn_msg.seq = 0
    req_cn_msg.ack = 0
    req_cn_msg.len = sizeof(c_int)

def send_mcast_op_msg(mcast_op):
    global current_cn_mcast_op
    connect()
    req_msg = event_req_msg()
    evm = req_msg.req
    nl_hdr = evm.hdr 
    set_netlink_header(nl_hdr,req_msg)

    req_msg.op = mcast_op

    req_cn_msg = evm.msg
    set_cn_msg(req_cn_msg)

    resp_size = notify_socket.send(req_msg)
    if (sizeof(req_msg) != resp_size):
        raise RuntimeError("Failed to send", mcast_op)
    
    current_cn_mcast_op = mcast_op


def wait_events(callback):
    """
    Blocking method used to process events
    The callback is notified for each event
    Callback Args
        what - Type: proc_event.ewhat
        event_data - Type 1 of proc_event.event_data_type
            See proc_event._event_mapping_ for expected types

    """
    global loop_read_events
    loop_read_events = True
    start_listen()
    read_events_loop(callback)
    disconnect()

def read_events_loop(callback):
    while loop_read_events:
        try:
            read_event(callback)
        except KeyboardInterrupt:
            disconnect()
            raise

def read_event(callback):
    recv_data = notify_socket.recv(1024)
    res_msg = event_res_msg.from_buffer_copy(recv_data)
    res_evm = res_msg.res
    res_nlm_hdr = res_evm.hdr
    nl_msg_type = res_nlm_hdr.nlmsg_type
    if nl_msg_type == NLMSG_NOOP:
        return

    if nl_msg_type in (NLMSG_ERROR, NLMSG_OVERRUN):
        raise RuntimeError("Error from socket ",nl_msg_type)

    res_event = res_msg.event
    what_val = res_event.what
    events = res_event.get_events()
    for what,event_data in events:
        if what==proc_event.ewhat.PROC_EVENT_NONE:
            notify_socket.settimeout(None)
        callback(what,event_data)

def disconnect():
    """
    closes the connection
    """
    global notify_socket
    global current_cn_mcast_op
    if notify_socket is not None:
        print("Disconnecting proc_notify")
        notify_socket.close()
        notify_socket = None
        current_cn_mcast_op = None


def start_listen():
    """
    Starts listening for proc events
    """
    send_mcast_op_msg(proc_cn_mcast_op.PROC_CN_MCAST_LISTEN)

def start_ignore():
    send_mcast_op_msg(proc_cn_mcast_op.PROC_CN_MCAST_IGNORE)

def stop_event_loop():
    """
    Allows exiting the event loop
    Can be used inside a callback to stop the loop processing
    """
    global loop_read_events
    loop_read_events = False

