import win32api

from win32gui import ClientToScreen

from helpers.winapi.windows import get_dims

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
    """ Sends a click to hwnd relative to window corner """

    w, h = get_dims(hwnd)

    if x > w or y > h:
        print(f'Click request outside of window: xy: {x} {y}, wh: {w} {h}')
        return

    sx, sy = ClientToScreen(hwnd, (x, y))
    print(f'Sending mouse click to client xy: {x} {y}  Screen xy: {sx} {sy}')
    win32api.PostMessage(hwnd, WM_LBUTTONDOWN, 1, make_lparam(x, y))
    win32api.PostMessage(hwnd, WM_LBUTTONUP, 0, make_lparam(x, y))

