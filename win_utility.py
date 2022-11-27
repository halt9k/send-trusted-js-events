from win32gui import *
from send_hotkey import *
import ctypes

from winapi_utility import activate, click


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


def mute(hwnd):
    press_ord_key(hwnd, ord('M'), True)


def run_script(hwnd):
    # relys on userscript auto start by s
    press_ord_key(hwnd, ord('R'), False)


def setup_init(hwnd, n):
    sleep(0.2)
    mute(hwnd)
    sleep(0.2)
    run_script(hwnd)
    sleep(0.2)
    shrink(hwnd, n)
    print('shrink, hwnd: ' + str(hwnd))
    sleep(0.2)


def setup_window(hwnd, n):
    prev_hwnd = activate(hwnd)
    setup_init(hwnd, n)
    activate(prev_hwnd)


def process_click(hwnd, text):
    cords = caption_to_xy(text)
    if cords:
        click(hwnd, cords[0], cords[1])
    return cords


def caption_to_xy(text):
    if not text.startswith('auto_click '):
        return None

    cords_txt = text.replace('auto_click ', '')
    # cords_txt = cords_txt.replace('translate(', '')
    # cords_txt = cords_txt.replace('px, ', ' ')
    cords_txt = cords_txt.replace(' — Mozilla Firefox', '')
    # cords = [int(s) for s in cords_txt.split() if (s.isdigit() or s == '-')]
    return [int(float(s)) for s in cords_txt.split()]
