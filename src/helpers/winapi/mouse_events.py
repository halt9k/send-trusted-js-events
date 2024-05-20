import win32api

from win32gui import ScreenToClient, SetWindowText

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


def send_click(hwnd, x, y):
    """ Sends a click to hwnd, but using absolute position """

    # l, t, r, b = win32gui.GetClientRect(hwnd)
    cx, cy = ScreenToClient(hwnd, (x, y))
    # x, y = xx + px, yy + py

    win32api.PostMessage(hwnd, WM_LBUTTONDOWN, 1, make_lparam(cx, cy))
    win32api.PostMessage(hwnd, WM_LBUTTONUP, 0, make_lparam(cx, cy))
    SetWindowText(hwnd, 'click_done')
    print(f'Client x: {cx} y: {cy}  Screen x: {x} y: {y}')


