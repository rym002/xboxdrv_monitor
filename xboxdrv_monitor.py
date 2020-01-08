#!/usr/bin/python
import psutil
import json
import os
import re
import signal
import sys
from subprocess import Popen
import proc_notify


class ProcMapping:
    def __init__(self,proc,controller_mapping_configs,num_controllers):
        self.proc = proc
        self.controller_mapping_configs = controller_mapping_configs
        self.num_controllers = num_controllers

def getconfig_path(file_name):
    return config["config_path"] + "/" + file_name + ".ini"

def get_config_cmd(file_name):
    return ["--config" , getconfig_path(file_name)]

def load_config_file():
    config_file = open('/etc/xboxdrv/controller.json','r')
    config=json.load(config_file)
    return config

def is_matching_proc(mapping,proc):
    ret=False
    if "proc_name" not in mapping:
        print("skipping missing proc_name",mapping)
        return ret

    if mapping["proc_name"]==proc.name():
        ret=True
        if "proc_cmd" in mapping:
            for mapping_proc_cmd in mapping["proc_cmd"]:
                match=False
                for cmd in proc.cmdline():
                    if re.match(mapping_proc_cmd,cmd):
                        match=True
                        break
                if match==False:
                    ret=False
                    break
    return ret

def start_controllers(controller_mapping_configs,proc,num_controllers,do_wait):
    stop_xboxdrv()
    print("Starting controllers for ",proc," do_wait=", do_wait)

    for controller in controllers[:num_controllers]:
        controller_config=get_config_cmd(controller)
        for controller_mapping_config in controller_mapping_configs:
            controller_config.extend(get_config_cmd(controller_mapping_config))
        start_xboxdrv(controller_config)
    if do_wait:
        proc.wait()
        start_no_wait_controller()
    else:
        pid = proc.pid
        if pid not in no_wait_procs:
            proc_mapping = ProcMapping(proc,controller_mapping_configs,num_controllers)
            no_wait_procs[pid] = proc_mapping

def start_xboxdrv(controller_config):
    command="/usr/bin/xboxdrv"
    full_command=[command]
    full_command.extend(controller_config)
    print("starting",full_command)
    process=Popen(full_command)

def stop_xboxdrv():
    print("Stopping xboxdrv")
    for proc in psutil.process_iter():
        if "xboxdrv"==proc.name():
            print("killing",proc)
            try:
                proc.terminate()
                proc.wait()
            except psutil.AccessDenied:
                print(format(psutil.AccessDenied))

def start_no_wait_controller():
    for pid, proc_mapping in no_wait_procs.items():
        proc = proc_mapping.proc
        if proc.is_running():
            start_controllers(proc_mapping.controller_mapping_configs,proc,proc_mapping.num_controllers,False)
            break
        else:
            del no_wait_procs[pid]

    exit_no_wait_procs()

def get_num_controllers(mapping):
    ret_val = len(controllers)
    if default_num_controllers!=None:
       ret_val=default_num_controllers 
    if "num_controllers" in mapping:
        ret_val = mapping["num_controllers"]
    return ret_val

def get_wait_proc(mapping):
    do_wait = True
    if "nowait_proc" in mapping:
        do_wait = not mapping["nowait_proc"]
    return do_wait

def get_mapping_config(mapping):
    ret = []
    if "config" in mapping:
        ret = mapping["config"]
    return ret

def scan_process_mapping():
    for mapping in config["mapping"]:
        mapping_match=False
        for p in psutil.process_iter():
            mapping_match = is_matching_proc(mapping,p)
            if mapping_match:
                num_controllers = get_num_controllers(mapping)
                do_wait = get_wait_proc(mapping)
                mapping_config = get_mapping_config(mapping)
                start_controllers(mapping_config,p,num_controllers,do_wait)
                break
        if mapping_match==True:
            break

def proc_callback(what,event_message):
    if what in callback_mapping:
        cb = callback_mapping[what]
        cb(what,event_message)

def proc_exit_callback(what,event_message):
    pid = event_message.process_pid
    if pid in no_wait_procs:
        del no_wait_procs[pid]
        exit_no_wait_procs()

def exit_no_wait_procs():
    if not no_wait_procs:
        stop_xboxdrv()

def proc_exec_callback(what,event_message):
        pid = event_message.process_pid
        if psutil.pid_exists(pid):
            try:
                proc = psutil.Process(pid)
                for mapping in config["mapping"]:
                    if is_matching_proc(mapping,proc):
                        num_controllers = get_num_controllers(mapping)
                        do_wait = get_wait_proc(mapping)
                        mapping_config = get_mapping_config(mapping)
                        if do_wait:
                            proc_notify.disconnect()

                        start_controllers(mapping_config,proc,num_controllers,do_wait)

                        if do_wait:
                            proc_notify.start_listen()
                        break
            except psutil.NoSuchProcess:
                pass

def signal_handler(signum,frame):
    stop_xboxdrv()
    proc_notify.disconnect()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM,signal_handler)
    try:
        config = load_config_file()
        controllers = config["controller"]
        default_num_controllers = config["num_controllers"]
        no_wait_procs = {}
        ewhat = proc_notify.proc_event.ewhat
        callback_mapping = {
            ewhat.PROC_EVENT_EXEC:proc_exec_callback,
            ewhat.PROC_EVENT_EXIT:proc_exit_callback
        }

        scan_process_mapping()
        proc_notify.wait_events(proc_callback)
    except KeyboardInterrupt:
        stop_xboxdrv()

