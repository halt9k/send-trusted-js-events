import win32api
import win32con

from win32gui import *
from send_hotkey import *
import ctypes


def shrink(hwnd, n):
    user32 = ctypes.windll.user32
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

    (wl, wt, wr, wb) = GetWindowRect(hwnd)
    ww = wr-wl
    wh = wb-wt

    sw, sh = screensize

    r = n % 2
    c = n // 2
    MoveWindow(hwnd, sw - ww * (c + 1), sh - wh * (r + 1), ww, wh, True)


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

def get_width(hwnd):
    return GetWindowRect(hwnd)[2] - GetWindowRect(hwnd)[0]


def mute(hwnd):
    PressOrdKey(hwnd, ord('M'), True)

def activate(hwnd):
    SetFocus(hwnd)


def run_script(hwnd):
    # relys on userscript auto start by s
    PressOrdKey(hwnd, ord('R'), False)


def initialize_window(hwnd, n):
    if GetWindowRect(hwnd)[1] > 10:
        return

    sleep(0.2)
    shrink(hwnd, n)
    sleep(0.2)
    mute(hwnd)
    sleep(0.2)
    run_script(hwnd)


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


def click(hwnd, xx, yy):
    # l, t, r, b = win32gui.GetClientRect(hwnd)
    px, py = ScreenToClient(hwnd, (xx, yy))
    # x,y = xx+px, yy+py
    x, y = px, py
    win32api.PostMessage(hwnd, WM_LBUTTONDOWN, 1, make_lparam(x, y))
    win32api.PostMessage(hwnd, WM_LBUTTONUP, 0, make_lparam(x, y))
    SetWindowText(hwnd, 'click_done')
    print('client ' + str(x) + ' ' + str(y) + ' screen ' + str(xx) + ' ' + str(yy))


def click_by_caption(handle, text):
    # print("    {0:d}: [{1:s}]".format(handle, text))
    if text.startswith('auto_click '):
        cords_txt = text.replace('auto_click ', '')
        # cords_txt = cords_txt.replace('translate(', '')
        # cords_txt = cords_txt.replace('px, ', ' ')
        cords_txt = cords_txt.replace(' — Mozilla Firefox', '')
        # cords = [int(s) for s in cords_txt.split() if (s.isdigit() or s == '-')]
        cords = [int(float(s)) for s in cords_txt.split()]
        click(handle, cords[0], cords[1])
