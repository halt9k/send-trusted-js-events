from enum import Enum
from typing import Any, Callable

from win32con import VK_LCONTROL, VK_RETURN

from helpers.winapi.hotkey_events import press_key, press_modifier, press_char
from helpers.winapi.mouse_events import send_click
from helpers.winapi.windows import get_title, set_title, switch_focus_window

# Common for UserScript and Observer
# Expected browser tab titles set by UserScript:
# REQ CLICK X Y
# REQ KEYS a b ... z A B ... Z Ctrl
# Expected browser tab titles set by Observer:
# REQ DONE


REQ_CLICK, REQ_KEYS = 'REQ CLICK ', 'REQ KEYS '
req_handlers = {REQ_CLICK: None, REQ_KEYS: None}
DONE = 'DONE'
ERASE_TEXT = [' — Mozilla Firefox', ' - Google Chrome']
CTRL_MODIFIER = 'Ctrl+'


def process_click(hwnd: int, args: str) -> bool:
    coords = [int(float(s)) for s in args.split()]
    if not coords:
        raise Exception("Incorrect command")

    assert len(coords) == 2
    return send_click(hwnd, coords[0], coords[1])


def process_hotkey(hwnd: int, args: str) -> bool:
    hotkeys = [s for s in args.split()]
    for char in hotkeys:
        if char == 'Space':
            char = ' '

        if len(char) == 1:
            with switch_focus_window(hwnd):
                press_char(hwnd, char)
        elif char == 'Enter':
            press_key(hwnd, VK_RETURN, True)
        elif CTRL_MODIFIER in char:
            assert len(char) == 6
            char = char[-1]
            with switch_focus_window(hwnd), press_modifier(hwnd, VK_LCONTROL):
                press_char(hwnd, char)
        else:
            raise NotImplementedError
    return True


def try_get_caption_request(hwnd):
    title: str = get_title(hwnd)
    found_keys = [key for key in req_handlers.keys() if title.startswith(key)]

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
