#!/usr/bin/env python3

import os

import win32api as wapi
import win32con as wcon
import win32gui as wgui
import win32process as wproc


# Callback
def enum_windows_proc(wnd, param):
    pid = param.get("pid", None)
    data = param.get("data", None)
    if pid is None or wproc.GetWindowThreadProcessId(wnd)[1] == pid:
        text = wgui.GetWindowText(wnd)
        if text:
            style = wapi.GetWindowLong(wnd, wcon.GWL_STYLE)
            if style & wcon.WS_VISIBLE:
                if data is not None:
                    data.append((wnd, text))
                # else:
                # print("%08X - %s" % (wnd, text))


def enum_process_windows(pid=None):
    data = []
    param = {
        "pid": pid,
        "data": data,
    }
    wgui.EnumWindows(enum_windows_proc, param)
    return data


def filter_procs(processes, proc_name_filters=None):
    if proc_name_filters is None:
        return processes

    proc_name_filters = [nm.lower() for nm in proc_name_filters]

    filtered = []
    for pid, _ in processes:
        try:
            proc = wapi.OpenProcess(wcon.PROCESS_ALL_ACCESS, 0, pid)
        except:
            # print("Process {0:d} couldn't be opened: {1:}".format(pid, traceback.format_exc()))
            continue

        try:
            file_name = wproc.GetModuleFileNameEx(proc, None)
        except:
            # print("Error getting process name: {0:}".format(traceback.format_exc()))
            wapi.CloseHandle(proc)
            continue
        base_name = file_name.split(os.path.sep)[-1]
        if base_name.lower() in proc_name_filters:
            filtered.append((pid, file_name))
        wapi.CloseHandle(proc)
    return tuple(filtered)


def get_procs_and_captions(proc_name_filters=None):
    procs = [(pid, None) for pid in wproc.EnumProcesses()]
    filtered = filter_procs(procs, proc_name_filters)
    return filtered
