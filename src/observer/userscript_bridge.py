from enum import Enum
from typing import Any, Callable

from helpers.winapi.mouse_events import send_click
from helpers.winapi.windows import get_title

# Common for UserScript and Observer
# Expected browser tab titles set by UserScript:
# REQ CLICK X Y
# REQ KEYS a b ... z A B ... Z Ctrl
# Expected browser tab titles set by Observer:
# REQ DONE


REQ_CLICK, REQ_KYES = 'REQ CLICK ', 'REQ KEYS '
req_handlers = {REQ_CLICK: None, REQ_KYES: None}
DONE = 'DONE'
ERASE_TEXT = [' — Mozilla Firefox']


def process_click(hwnd: int, args: str) -> bool:
    # coords_txt = cords_txt.replace('translate(', '')
    # coords_txt = coords_txt.replace('px, ', ' ')
    # coords = [int(s) for s in cords_txt.split() if (s.isdigit() or s == '-')]
    coords = [int(float(s)) for s in args.split()]
    if not coords:
        return False

    assert len(coords) == 2
    send_click(hwnd, coords[0], coords[1])
    return True


# TODO other reqs
def process_hotkey(hwnd, args: str) -> bool:
    raise NotImplementedError


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
    msg = msg.replace(req, '')
    for rep in ERASE_TEXT:
        msg = msg.replace(rep, '')

    req_handler: Callable[[int, str], bool] = req_handlers[req]
    if not req_handler:
        raise NotImplementedError

    print(f'Delivering trusted input to {hwnd}, command is {msg}')
    return req_handler(hwnd, msg)


req_handlers[REQ_CLICK] = process_click
