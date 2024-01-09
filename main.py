from dataclasses import dataclass
from random import random

import win32gui

from get_proc_windows import get_procs_and_captions, enum_process_windows
from win_utility import *
import datetime

from winapi_helpers import get_dims, is_window_state_normal, get_caption, is_window_state_maxed


@dataclass
class TabInfo:
    side: int = 0
    last_text: str = ''
    total_clicks: int = 0
    last_click_ms: datetime.datetime = datetime.datetime.now()
    # last_click: (int, int) = (0, 0)
    closed: bool = False


browser_tabs = {}
new_window = False


def del_closed_tabs():
    global browser_tabs
    pop_keys = []
    for key in browser_tabs.keys():
        if browser_tabs[key].closed:
            pop_keys += [key]
        browser_tabs[key].closed = True

    for key in pop_keys:
        browser_tabs.pop(key)


def process_window(hwnd, rearrange):
    if not is_popup(hwnd):
        return rearrange

    if hwnd not in browser_tabs.keys():
        browser_tabs[hwnd] = TabInfo()
        rearrange = True
    browser_tabs[hwnd].closed = False

    init_failed = browser_tabs[hwnd].total_clicks == 0 and not rearrange
    if rearrange or init_failed:
        n = list(browser_tabs.keys()).index(hwnd)
        setup_window(hwnd, n)

    if browser_tabs[hwnd].last_text == get_caption(hwnd):
        return rearrange

    browser_tabs[hwnd].total_clicks += 1
    # if sqrt(sites[hwnd].total) / 20 > random():
    # print ('Skipped')
    # continue

    browser_tabs[hwnd].last_text = get_caption(hwnd)
    if process_click(hwnd):
        browser_tabs[hwnd].last_click_ms = datetime.datetime.now()

    return rearrange


def is_active_tab_maxed() -> bool:
    handle = GetForegroundWindow()
    if not handle:
        return False

    procs = get_procs_and_captions(filter_by_module_name="firefox.exe")
    handles = [enum_process_windows(x[0]) for x in procs]
    handles_with_windows = [x for x in handles if x != []]
    flatten = [x[0] for y in handles_with_windows for x in y]

    if handle not in flatten:
        return False

    print ('Active tab is maxed: ' + str(is_window_state_maxed(handle)))
    return is_window_state_maxed(handle)


def click_check():
    global browser_tabs, new_window
    del_closed_tabs()

    if is_active_tab_maxed():
        return

    procs = get_procs_and_captions(filter_by_module_name="firefox.exe")
    for pid, name in procs:
        data = enum_process_windows(pid)
        if not data:
            continue

        # proc_text = "PId {0:d}{1:s}windows:".format(pid, " (File: [{0:s}]) ".format(name) if name else " ")
        # print(proc_text)
        for hwnd, _ in data:
            # hwnd may became obsolete on any internal step
            rearrange = new_window
            new_window = False
            try:
                rearrange = process_window(hwnd, rearrange)
                if rearrange:
                    new_window = True
            except Exception as e:
                browser_tabs.pop(hwnd)
                print(e)


click_check()
while not sleep(0.1 + random() / 2.0):
    # print('cl')

    click_check()
    # print('cl_d')
