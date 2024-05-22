from win32con import VK_LCONTROL

from helpers.winapi.hotkey_events import press_key, press_key_modified
from helpers.winapi.windows import shrink, is_window_state_normal, get_caption, activate, get_dims, \
    safe_sleep


def initial_window_setup(hwnd):
    # for callback from observer script when it notifies a new window

    with safe_sleep(0.1, hwnd):
        activate(hwnd)

    with safe_sleep(0.1, hwnd, require_active=True):
        mute(hwnd)

    # relys on userscript auto start by s
    with safe_sleep(0.1, hwnd, require_active=True):
        press_key(hwnd, ord('R'))


def mute(hwnd):
    with safe_sleep(0.1, hwnd, require_active=True):
        press_key_modified(hwnd, key_code=ord('M'), modifier_key_code=VK_LCONTROL)


def is_arranged(hwnd):
    # tricky: not updated on tabs, must be checked again after activation
    caption = get_caption(hwnd)
    if caption.startswith('lichess.org'):
        return False

    if not is_window_state_normal(hwnd):
        return False

    wh, ht = get_dims(hwnd)
    return wh in range(200, 450) and ht in range(300, 800)


def arrage_window(hwnd, n):
    # periodic call for all windows from observer script
    # for example, can be used to shrink and arrange them in tiles pattern

    safe_sleep(hwnd, 0.1)

    # TODO not here
    is_normal = is_window_state_normal(hwnd)
    if not is_arranged(hwnd):
        raise Exception('Window embedded back while sleep')
    if is_normal != is_window_state_normal(hwnd):
        raise Exception('Window changed pos while sleep')

    print('shrink, hwnd: ' + str(hwnd))
    shrink(hwnd, n)
