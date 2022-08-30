from dataclasses import dataclass
from random import random

from win_func import *

from win_enum import enum_processes, enum_process_windows



@dataclass
class TabInfo:
    side: int = 0
    last_text: str = ''
    total_clicks: int = 0
    # last_click: (int, int) = (0, 0)
    closed: bool = False


sites = {}


def del_closed_tabs():
    global sites
    pop_keys = []
    for key in sites.keys():
        if sites[key].closed:
            pop_keys += [key]
        sites[key].closed = True

    for key in pop_keys:
        sites.pop(key)


def click_check():
    global sites
    del_closed_tabs()

    procs = enum_processes(process_name="firefox.exe")
    for pid, name in procs:
        data = enum_process_windows(pid)
        if not data:
            continue

        # proc_text = "PId {0:d}{1:s}windows:".format(pid, " (File: [{0:s}]) ".format(name) if name else " ")
        # print(proc_text)
        for handle, text in data:
            wh = get_width(handle)
            if (not wh in range(40, 400)) or (not is_window_normal(handle)):
                continue

            if handle not in sites.keys():
                sites[handle] = TabInfo()
            sites[handle].closed = False

            n = list(sites.keys()).index(handle)
            initialize_window(handle, n)

            if sites[handle].last_text == text:
                continue

            sites[handle].total_clicks += 1
            # if sqrt(sites[handle].total) / 20 > random():
            # print ('Skipped')
            # continue

            sites[handle].last_text = text
            click_by_caption(handle, text)



click_check()
while not sleep(0.1 + random()/2.0):
    # print('cl')

    click_check()
    # print('cl_d')
