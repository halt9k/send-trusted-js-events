from dataclasses import dataclass
from random import random

from win_utility import *

from win_enum import enum_processes, enum_process_windows



@dataclass
class TabInfo:
    side: int = 0
    last_text: str = ''
    total_clicks: int = 0
    # last_click: (int, int) = (0, 0)
    closed: bool = False


browser_tabs = {}


def del_closed_tabs():
    global browser_tabs
    pop_keys = []
    for key in browser_tabs.keys():
        if browser_tabs[key].closed:
            pop_keys += [key]
        browser_tabs[key].closed = True

    for key in pop_keys:
        browser_tabs.pop(key)


def test_window_setup(hwnd):
    wh = get_width(hwnd)
    return wh in range(40, 400) and is_window_normal(hwnd)


def click_check():
    global browser_tabs
    del_closed_tabs()

    procs = enum_processes(process_name="firefox.exe")
    for pid, name in procs:
        data = enum_process_windows(pid)
        if not data:
            continue

        # proc_text = "PId {0:d}{1:s}windows:".format(pid, " (File: [{0:s}]) ".format(name) if name else " ")
        # print(proc_text)
        for hwnd, text in data:
            if test_window_setup(hwnd):
                continue

            if hwnd not in browser_tabs.keys():
                browser_tabs[hwnd] = TabInfo()
            browser_tabs[hwnd].closed = False

            n = list(browser_tabs.keys()).index(hwnd)
            setup_window(hwnd, n)


            if browser_tabs[hwnd].last_text == text:
                continue

            browser_tabs[hwnd].total_clicks += 1
            # if sqrt(sites[hwnd].total) / 20 > random():
            # print ('Skipped')
            # continue

            browser_tabs[hwnd].last_text = text
            process_click(hwnd, text)


click_check()
while not sleep(0.1 + random()/2.0):
    # print('cl')

    click_check()
    # print('cl_d')
