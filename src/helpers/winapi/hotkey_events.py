from contextlib import contextmanager

from win32con import *
from win32api import *

from helpers.winapi.windows import unsafe_sleep


def press_key(hwnd, key_code, delay_sec=0.1):
    """
    Can send standard keys, requres focus when multiple tabs opened
    key_code: can be ord('M'), ord('r'), ...
    """

    # specifically for browsers with multiple tabs,
    # PostMessage requres focus active or it may send to the wrong tab
    with unsafe_sleep(0, hwnd, require_active=True, keep_state=True):
        PostMessage(hwnd, WM_KEYDOWN, key_code, 0)
    with unsafe_sleep(delay_sec, hwnd, require_active=True, keep_state=True):
        PostMessage(hwnd, WM_KEYUP, key_code, 0)


@contextmanager
def press_modifier(hwnd, modifier_key_code, delay_sec=0.1):
    """
    Can send Ctrl + * hotkeys, requres focus when multiple tabs opened
    modifier_key_code: usually will be win32con.VK_*, like VK_LSHIFT, VK_RSHIFT, VK_LCONTROL, VK_RCONTROL
    """

    with unsafe_sleep(delay_sec, hwnd, require_active=True, keep_state=True):
        # PostMessage not catched in combo
        keybd_event(modifier_key_code, 0, 0, 0)
    yield
    with unsafe_sleep(delay_sec, hwnd, require_active=True, keep_state=True):
        keybd_event(modifier_key_code, 0, KEYEVENTF_KEYUP, 0)

