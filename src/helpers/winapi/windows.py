import ctypes
from contextlib import contextmanager
from enum import Enum
from time import sleep

import win32con
import win32gui
from winxpgui import IsWindow
import pyautogui

from helpers.winapi.processes import get_module_paths, get_process_windows


class MissingWindowFocusException(Exception):
    pass


class WindowState(Enum):
    MAX = win32con.SW_SHOWMAXIMIZED
    MIN = win32con.SW_SHOWMINIMIZED
    NORM = win32con.SW_SHOWNORMAL


def get_dims(hwnd):
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    w = right - left
    h = bottom - top
    return w, h


def shrink_and_arrange(hwnd, n, shrinked_width, shrinked_height):
    """ resizes window (browser tab)
    and arranges them in two rows starting from right bottom corner n = 1 """

    user32 = ctypes.windll.user32
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    sw, sh = screensize

    wl, wt, wr, wb = win32gui.GetWindowRect(hwnd)
    w = shrinked_width if shrinked_width else wr - wl
    h = shrinked_height if shrinked_height else wb - wt

    arrange_row = n % 2
    arrange_col = n // 2
    x = sw - w * (arrange_col + 1)
    y = sh - h * (arrange_row + 1)

    alreday_moved = (x == wl and y == wt)
    if alreday_moved:
        return False

    win32gui.MoveWindow(hwnd, x, y, w, h, True)
    print(f'Hwnd shrink requested: {hwnd}')
    return True


@contextmanager
def unsafe_sleep(delay, hwnd, require_active=False, keep_state=False):
    # reminder: during sleep windows can be closed, moved, trayed, switched

    if require_active and win32gui.GetForegroundWindow() != hwnd:
        raise MissingWindowFocusException(f'Window inactive at sleep start: {hwnd}')

    state = get_window_state(hwnd) if keep_state else None

    print(f"Sleep {delay}")
    sleep(delay)

    if not if_window_exist(hwnd):
        raise Exception(f'Window closed while sleep: {hwnd}')

    if keep_state and state != get_window_state(hwnd):
        raise Exception(f'Window changed state while sleep: {hwnd}')

    if require_active and win32gui.GetForegroundWindow() != hwnd:
        raise MissingWindowFocusException(f'Window went inactive while sleep: {hwnd}')
    yield


@contextmanager
def activate(hwnd, post_delay=0.15):
    prev_hwnd = win32gui.GetForegroundWindow()

    if prev_hwnd != hwnd:
        pyautogui.press("alt")
        win32gui.SetForegroundWindow(hwnd)

        sleep(post_delay)

    if win32gui.GetForegroundWindow() == hwnd:
        yield
        win32gui.SetForegroundWindow(prev_hwnd)
    else:
        raise MissingWindowFocusException(f'Window activation failed: {hwnd}')


def get_window_state(hwnd) -> WindowState:
    place = win32gui.GetWindowPlacement(hwnd)
    state = WindowState(place[1])
    return state


def get_title(hwnd):
    return win32gui.GetWindowText(hwnd)


def if_window_exist(hwnd):
    return IsWindow(hwnd)


def is_active_window_maxed(proc_filter_func) -> bool:
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        return False

    procs = get_module_paths(proc_filter_func)
    handles = [get_process_windows(x[0]) for x in procs]
    handles_with_windows = [x for x in handles if x != []]
    flatten = [x[0] for y in handles_with_windows for x in y]

    if hwnd not in flatten:
        return False

    return get_window_state(hwnd) == WindowState.MAX
