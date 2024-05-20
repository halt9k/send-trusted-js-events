from dataclasses import dataclass
from random import random

from helpers.winapi.processes import get_procs_and_captions, enum_process_windows
from helpers.winapi.interactions_2 import *
import datetime

from helpers import os  # noqa: F401
from helpers.winapi.interactions import get_caption, is_window_state_maxed, if_window_exist


@dataclass
class TabInfo:
    side: int = 0
    last_text: str = ''
    total_clicks: int = 0
    last_click_ms: datetime.datetime = datetime.datetime.now()
    # last_click: (int, int) = (0, 0)
    closed: bool = False
    initialized: bool = False


browser_tabs = {}
new_window = False


def del_closed_tabs():
    global browser_tabs

    pop_keys = []
    for key in browser_tabs.keys():
        if browser_tabs[key].closed:
            pop_keys += [key]

        browser_tabs[key].closed = not if_window_exist(key)

    for key in pop_keys:
        browser_tabs.pop(key)

    return len(pop_keys)


def process_window(hwnd, force_rearrange):
    global browser_tabs

    if not is_popup(hwnd):
        return

    if hwnd not in browser_tabs.keys():
        browser_tabs[hwnd] = TabInfo()
        force_rearrange = True

        browser_tabs[hwnd].closed = False
        browser_tabs[hwnd].initialized = False
        browser_tabs[hwnd].added = datetime.time()

    last_capt = browser_tabs[hwnd].last_text
    if last_capt.startswith("auto_click"):
        browser_tabs[hwnd].initialized = True

    if not browser_tabs[hwnd].initialized:
        setup_init(hwnd)

    if force_rearrange or browser_tabs[hwnd].total_clicks == 0:
        n = list(browser_tabs.keys()).index(hwnd)
        rearrage_window_tile(hwnd, n)

    if browser_tabs[hwnd].last_text == get_caption(hwnd):
        return

    browser_tabs[hwnd].total_clicks += 1
    # if sqrt(sites[hwnd].total) / 20 > random():
    # print ('Skipped')
    # continue

    browser_tabs[hwnd].last_text = get_caption(hwnd)
    if process_click(hwnd):
        browser_tabs[hwnd].last_click_ms = datetime.datetime.now()


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
    count_changed = del_closed_tabs()

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
            try:
                process_window(hwnd, count_changed)
            except Exception as e:
                browser_tabs.pop(hwnd)
                print(e)


click_check()
while not sleep(0.1 + random() / 2.0):
    # print('cl')

    click_check()
    # print('cl_d')
