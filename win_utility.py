from win32gui import *
from send_hotkey import *
import ctypes

from winapi_helpers import activate, click, get_caption, is_window_state_normal, get_dims


def shrink(hwnd, n):
    user32 = ctypes.windll.user32
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

    (wl, wt, wr, wb) = GetWindowRect(hwnd)
    ww = wr-wl
    wh = wb-wt

    sw, sh = screensize

    r = n % 2
    c = n // 2

    wwl, wwt = sw - ww * (c + 1), sh - wh * (r + 1)
    alreday_moved = (wwl == wl and wwt == wt)
    if not alreday_moved:
        MoveWindow(hwnd, sw - ww * (c + 1), sh - wh * (r + 1), ww, wh, True)
        return True
    return False


def mute(hwnd):
    press_ord_key(hwnd, ord('M'), True)


def run_script(hwnd):
    # relys on userscript auto start by s
    press_ord_key(hwnd, ord('R'), False)


def is_popup(hwnd):
    # tricky: not updated on tabs, must be checked again after activation
    caption = get_caption(hwnd)
    if caption.startswith('lichess.org'):
        return False

    if not is_window_state_normal(hwnd):
        return False

    wh, ht = get_dims(hwnd)
    return wh in range(200, 450) and ht in range(300, 800)


def safe_sleep(hwnd, delay):
    is_normal = is_window_state_normal(hwnd)

    sleep(delay)

    if not is_popup(hwnd):
        raise Exception('Window embedded back while sleep')
    if is_normal != is_window_state_normal(hwnd):
        raise Exception('Window changed pos while sleep')


def setup_init(hwnd):
    safe_sleep(hwnd, 0.1)
    activate(hwnd)
    mute(hwnd)
    safe_sleep(hwnd, 0.1)
    activate(hwnd)
    run_script(hwnd)


def rearrage_window_tile(hwnd, n):
    safe_sleep(hwnd, 0.1)
    print('shrink, hwnd: ' + str(hwnd))
    if not shrink(hwnd, n):
        return


def process_click(hwnd):
    cords = caption_to_xy(get_caption(hwnd))
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
