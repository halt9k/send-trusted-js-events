from time import sleep

from win32con import VK_LCONTROL

from helpers.winapi.hotkey_events import press_key, press_key_modified
from helpers.winapi.windows import shrink_and_arrange, get_window_state, get_caption, activate, get_dims, \
    safe_sleep, WindowState


ARRANGE_WIDTH, ARRANGE_HEIGHT = 330, 510


def mute_tab(hwnd):
    with safe_sleep(0.1, hwnd, require_active=True):
        press_key_modified(hwnd, key_code=ord('M'), modifier_key_code=VK_LCONTROL)


# TODO what if fails, repeat?
def initial_window_setup(hwnd) -> bool:
    # for callback from observer script when it notifies a new window
    caption = get_caption(hwnd)
    if not caption.startswith('lichess.org'):
        return False

    with safe_sleep(0.1, hwnd):
        activate(hwnd)

    with safe_sleep(0.1, hwnd, require_active=True):
        mute_tab(hwnd)

    # relys on userscript auto start by s
    with safe_sleep(0.1, hwnd, require_active=True):
        press_key(hwnd, ord('R'))

    return True


def is_arranged(hwnd):
    # tricky: not updated on tabs, must be checked again after activation
    caption = get_caption(hwnd)
    # TODO fix
    if caption.startswith('lichess.org'):
        return False

    if get_window_state(hwnd) != WindowState.NORM:
        return False

    w, h = get_dims(hwnd)
    return abs(w - ARRANGE_WIDTH) < 10 and abs(h - ARRANGE_HEIGHT) < 10


def arrage_window(hwnd, n):
    # periodic call for all windows from observer script
    # for example, can be used to shrink and arrange them in tiles pattern

    # TODO not here
    if not is_arranged(hwnd):
        raise Exception('Window embedded back while sleep')

    print(f'Starting to shrink hwnd: {hwnd}')
    shrink_and_arrange(hwnd, n, ARRANGE_WIDTH, ARRANGE_HEIGHT)
    sleep(0.1)
