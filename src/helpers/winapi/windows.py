from contextlib import contextmanager
from time import sleep

import win32con
import win32gui
from win32gui import *
from win32gui import GetWindowText, GetForegroundWindow, GetWindowRect

from helpers.winapi.hotkey_events import *
import ctypes

from helpers.winapi.processes import get_process_paths, get_process_windows


def shrink(hwnd, n):
    user32 = ctypes.windll.user32
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    sw, sh = screensize

    wl, wt, wr, wb = GetWindowRect(hwnd)
    ww = wr-wl
    wh = wb-wt

    arrange_row = n % 2
    arrange_col = n // 2

    x, y = sw - ww * (arrange_col + 1), sh - wh * (arrange_row + 1)
    alreday_moved = (x == wl and y == wt)
    if not alreday_moved:
        MoveWindow(hwnd, sw - ww * (arrange_col + 1), sh - wh * (arrange_row + 1), ww, wh, True)
        return True
    return False


@contextmanager
def safe_sleep(delay, hwnd, require_active=False):
    # reminder: during sleep windows can be closed, moved, trayed, switched
    sleep(delay)

    if not if_window_exist(hwnd):
        raise Exception(f'Window closed while sleep: {hwnd}')

    if require_active and GetForegroundWindow() != hwnd:
        raise Exception(f'Window went inactive while sleep: {hwnd}')
    yield


def is_window_state_normal(handle):
    normal = False
    minimized = False

    tup = win32gui.GetWindowPlacement(handle)
    if tup[1] == win32con.SW_SHOWMAXIMIZED:
        minimized = False
    elif tup[1] == win32con.SW_SHOWMINIMIZED:
        minimized = True
    elif tup[1] == win32con.SW_SHOWNORMAL:
        normal = True
    return normal


def is_window_state_maxed(handle):
    tup = win32gui.GetWindowPlacement(handle)
    return tup[1] == win32con.SW_SHOWMAXIMIZED


def get_caption(hwnd):
    return GetWindowText(hwnd)


def if_window_exist(hwnd):
    return win32gui.IsWindow(hwnd)


def activate(hwnd, post_delay=0.1):
    prev_hwnd = GetForegroundWindow()
    win32gui.SetForegroundWindow(hwnd)

    sleep(post_delay)

    if GetForegroundWindow() == hwnd:
        return prev_hwnd
    else:
        raise Exception(f'Window activation failed: {hwnd}')


def get_dims(hwnd):
    wh = GetWindowRect(hwnd)[2] - GetWindowRect(hwnd)[0]
    ht = GetWindowRect(hwnd)[3] - GetWindowRect(hwnd)[1]
    return wh, ht


def is_active_window_maxed(process_name_filters) -> bool:
    handle = GetForegroundWindow()
    if not handle:
        return False

    procs = get_process_paths(proc_name_filters=process_name_filters)
    handles = [get_process_windows(x[0]) for x in procs]
    handles_with_windows = [x for x in handles if x != []]
    flatten = [x[0] for y in handles_with_windows for x in y]

    if handle not in flatten:
        return False

    return is_window_state_maxed(handle)