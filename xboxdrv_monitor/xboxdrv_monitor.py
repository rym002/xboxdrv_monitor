#!/usr/bin/python
import psutil
import json
import os
import re
import signal
import sys
from subprocess import Popen
import proc_notify


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

def start_controllers(controllers,mapping_configs,proc):
    stop_xboxdrv()
    for controller in controllers:
        config=get_config_cmd(controller)
        for mapping_config in mapping_configs:
            config.extend(get_config_cmd(mapping_config))
        start_xboxdrv(config)
    if proc!=None:
        proc.wait()
        start_default_controllers(controllers)

def start_xboxdrv(config):
    command="/usr/bin/xboxdrv"
    full_command=[command]
    full_command.extend(config)
    print("starting",full_command)
    process=Popen(full_command)
    print(process.pid)

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

def start_default_controllers(controllers):
    start_controllers(controllers,[],None)

def scan_process_mapping():
    for mapping in config["mapping"]:
        mapping_match=False
        for p in psutil.process_iter():
            mapping_match = is_matching_proc(mapping,p)
            if mapping_match:
                start_controllers(controllers,mapping["config"],p)
                break
        if mapping_match==True:
            break

def proc_callback(what,event_message):
    ewhat = proc_notify.proc_event.ewhat
    if what == ewhat.PROC_EVENT_EXEC:
        pid = event_message.process_pid
        if psutil.pid_exists(pid):
            try:
                proc = psutil.Process(pid)
                for mapping in config["mapping"]:
                    if is_matching_proc(mapping,proc):
                        proc_notify.disconnect()
                        start_controllers(controllers,mapping["config"],proc)
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
        config=load_config_file()
        controllers=config["controller"]

        start_default_controllers(controllers)
        scan_process_mapping()
        proc_notify.wait_events(proc_callback)
    except KeyboardInterrupt:
        stop_xboxdrv()

