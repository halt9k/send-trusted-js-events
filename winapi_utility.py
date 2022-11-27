import win32api
import win32con
import win32gui

from win32gui import GetForegroundWindow, GetWindowRect, ScreenToClient, SetWindowText

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


def activate(hwnd):
    prev_hwnd = GetForegroundWindow()
    win32gui.SetForegroundWindow(hwnd)

    if GetForegroundWindow() == hwnd:
        return prev_hwnd
    else:
        raise Exception('Window activation failed')


def get_width(hwnd):
    return GetWindowRect(hwnd)[2] - GetWindowRect(hwnd)[0]


def click(hwnd, xx, yy):
    # l, t, r, b = win32gui.GetClientRect(hwnd)
    px, py = ScreenToClient(hwnd, (xx, yy))
    # x,y = xx+px, yy+py
    x, y = px, py
    win32api.PostMessage(hwnd, WM_LBUTTONDOWN, 1, make_lparam(x, y))
    win32api.PostMessage(hwnd, WM_LBUTTONUP, 0, make_lparam(x, y))
    SetWindowText(hwnd, 'click_done')
    print('client ' + str(x) + ' ' + str(y) + ' screen ' + str(xx) + ' ' + str(yy))


def is_window_normal(handle):
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
