from dataclasses import dataclass
from random import random

from win_enum import enum_processes, enum_process_windows
from win_utility import *
import datetime

from winapi_utility import get_width, is_window_normal


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


def is_popup(hwnd):
    # tricvky: not updated on tabs, must be checked again after activation
    wh = get_width(hwnd)
    return is_window_normal(hwnd) and (wh in range(100, 450))


def process_window(hwnd, text, rearrange):
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

    if browser_tabs[hwnd].last_text == text:
        return rearrange

    browser_tabs[hwnd].total_clicks += 1
    # if sqrt(sites[hwnd].total) / 20 > random():
    # print ('Skipped')
    # continue

    browser_tabs[hwnd].last_text = text
    if process_click(hwnd, text):
        browser_tabs[hwnd].last_click_ms = datetime.datetime.now()

    return rearrange


def click_check():
    global browser_tabs, new_window
    del_closed_tabs()

    procs = enum_processes(process_name="firefox.exe")
    for pid, name in procs:
        data = enum_process_windows(pid)
        if not data:
            continue

        # proc_text = "PId {0:d}{1:s}windows:".format(pid, " (File: [{0:s}]) ".format(name) if name else " ")
        # print(proc_text)
        for hwnd, text in data:
            # hwnd may became obsolete on any internal step
            rearrange = new_window
            new_window = False
            try:
                rearrange = process_window(hwnd, text, rearrange)
                if rearrange:
                    new_window = True
            except Exception as e:
                print(e)


click_check()
while not sleep(0.1 + random() / 2.0):
    # print('cl')

    click_check()
    # print('cl_d')
