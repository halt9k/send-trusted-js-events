import win32api

from win32gui import ClientToScreen, ScreenToClient, GetWindowRect
from winxpgui import GetClientRect

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
    """
    Sends a click to hwnd relative to window corner,
    does not require focus (on some web pages?)
    """

    # PostMessage expects relative to Client which offsets from window corner
    l, t, r, b = GetWindowRect(hwnd)
    cx, cy = ScreenToClient(hwnd, (x + l, y + t))

    cl, ct, cr, cb = GetClientRect(hwnd)
    cw, ch = cr - cl, cb - ct

    if not cl < cx < cr or not ct < cy < cb:
        print(f'Warning: click request outside of client area, skipped. cx cy: {cx} {cy}')
        # print(f'Relative to window: x y: {x} {y}')
        # print(f'Relative to client: cx cy: {cx} {cy}, cw ch: {cw} {ch}')
        return False

    print(f'Sending mouse click to Window xy: {x} {y} Client xy: {cx} {cy}')
    win32api.PostMessage(hwnd, WM_LBUTTONDOWN, 1, make_lparam(cx, cy))
    win32api.PostMessage(hwnd, WM_LBUTTONUP, 0, make_lparam(cx, cy))
    return True
