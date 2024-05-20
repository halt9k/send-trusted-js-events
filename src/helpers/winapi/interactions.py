from time import sleep

import win32api
import win32con
import win32gui

from win32gui import GetForegroundWindow, GetWindowRect, ScreenToClient, SetWindowText, GetWindowText

MOUSEEVENTF_MOVE = 0x0001  # mouse move
MOUSEEVENTF_ABSOLUTE = 0x8000  # absolute move
MOUSEEVENTF_MOVEABS = MOUSEEVENTF_MOVE + MOUSEEVENTF_ABSOLUTE
MOUSEEVENTF_LEFTDOWN = 0x0002  # left button down
MOUSEEVENTF_LEFTUP = 0x0004  # left button up
MOUSEEVENTF_CLICK = MOUSEEVENTF_LEFTDOWN + MOUSEEVENTF_LEFTUP
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202


def make_lparam(x, y):
    return (y << 16) | (x & 0xFFFF)


def if_window_exist(hwnd):
    return win32gui.IsWindow(hwnd)


def activate(hwnd):
    prev_hwnd = GetForegroundWindow()
    win32gui.SetForegroundWindow(hwnd)
    sleep(0.1)

    if GetForegroundWindow() == hwnd:
        return prev_hwnd
    else:
        raise Exception('Window activation failed')


def get_dims(hwnd):
    wh = GetWindowRect(hwnd)[2] - GetWindowRect(hwnd)[0]
    ht = GetWindowRect(hwnd)[3] - GetWindowRect(hwnd)[1]
    return wh, ht


def click(hwnd, xx, yy):
    # l, t, r, b = win32gui.GetClientRect(hwnd)
    px, py = ScreenToClient(hwnd, (xx, yy))
    # x,y = xx+px, yy+py
    x, y = px, py
    win32api.PostMessage(hwnd, WM_LBUTTONDOWN, 1, make_lparam(x, y))
    win32api.PostMessage(hwnd, WM_LBUTTONUP, 0, make_lparam(x, y))
    SetWindowText(hwnd, 'click_done')
    print('client ' + str(x) + ' ' + str(y) + ' screen ' + str(xx) + ' ' + str(yy))


def is_window_state_normal(handle):
    normal = False
    minimised = False

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