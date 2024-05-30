from enum import Enum
from typing import Any, Callable

from win32con import VK_LCONTROL

from helpers.winapi.hotkey_events import press_key, press_modifier
from helpers.winapi.mouse_events import send_click
from helpers.winapi.windows import get_title, set_title

# Common for UserScript and Observer
# Expected browser tab titles set by UserScript:
# REQ CLICK X Y
# REQ KEYS a b ... z A B ... Z Ctrl
# Expected browser tab titles set by Observer:
# REQ DONE


REQ_CLICK, REQ_KEYS = 'REQ CLICK ', 'REQ KEYS '
req_handlers = {REQ_CLICK: None, REQ_KEYS: None}
DONE = 'DONE'
ERASE_TEXT = [' — Mozilla Firefox']
CTRL_MODIFIER = 'Ctrl+'


def process_click(hwnd: int, args: str) -> bool:
    coords = [int(float(s)) for s in args.split()]
    if not coords:
        return False

    assert len(coords) == 2
    send_click(hwnd, coords[0], coords[1])
    return True


def ensure_simple_key_code(key_code):
    return 'a' < key_code < 'z' or 'A' < key_code < 'Z'


# TODO other reqs
def process_hotkey(hwnd: int, args: str) -> bool:
    hotkeys = [s for s in args.split()]
    for key in hotkeys:
        if ensure_simple_key_code(key):
            press_key(hwnd, ord(key))
        elif CTRL_MODIFIER in key:
            assert len(key) == 6
            key = key[-1]
            ensure_simple_key_code(key)
            with press_modifier(hwnd, VK_LCONTROL):
                press_key(hwnd, ord(key))
        else:
            raise NotImplementedError
    return True



def try_get_caption_request(hwnd):
    title = get_title(hwnd)
    found_keys = [key for key in req_handlers.keys() if key in title]

    if len(found_keys) > 2:
        raise Exception("Userscript placed ambiguous caption commands")
    elif len(found_keys) == 1:
        return found_keys[0]
    else:
        return None


def process_caption(hwnd) -> bool:
    """ Returns True is request was detected and delivered"""

    req = try_get_caption_request(hwnd)
    if not req:
        return False

    msg = get_title(hwnd)
    for rep in ERASE_TEXT:
        msg = msg.replace(rep, '')
    args = msg.replace(req, '')

    req_handler: Callable[[int, str], bool] = req_handlers[req]
    if not req_handler:
        raise NotImplementedError

    print(f'Delivering trusted input to {hwnd}, command is {msg}')
    res = req_handler(hwnd, args)
    if res:
        set_title(hwnd, DONE)
    return res


req_handlers[REQ_CLICK] = process_click
req_handlers[REQ_KEYS] = process_hotkey
