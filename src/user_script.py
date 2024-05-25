from dataclasses import dataclass
from random import random
from time import sleep

from win32con import VK_LCONTROL

from code_tools.virtual_methods import override
from helpers.winapi.hotkey_events import press_key, press_key_modified
from helpers.winapi.windows import shrink_and_arrange, get_window_state, get_caption, activate, get_dims, \
    safe_sleep, WindowState, is_active_window_maxed
from observer.custom_script import CustomScriptAbstract

ARRANGE_WIDTH, ARRANGE_HEIGHT = 330, 510


def mute_tab(hwnd):
    with safe_sleep(0.1, hwnd, require_active=True):
        press_key_modified(hwnd, key_code=ord('M'), modifier_key_code=VK_LCONTROL)


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


@dataclass(init=True)
class UserObserverScript(CustomScriptAbstract):
    disable_if_maximized: bool = True
    intervals_sec: float = 0.1
    random_intervals_sec: float = 0.3

    # TODO what if fails, repeat?
    @override
    def on_initial_window_setup(self, hwnd) -> bool:
        caption = get_caption(hwnd)
        if not 'lichess.org' in caption:
            return False

        with safe_sleep(0.1, hwnd):
            if not activate(hwnd):
                return False

        with safe_sleep(0.1, hwnd, require_active=False):
            mute_tab(hwnd)

        # relies on userscript auto start by s
        press_key(hwnd, ord('R'))

        return True

    @override
    def on_hwnd_filter(self, hwnd) -> bool:
        raise NotImplementedError()

    @override
    def on_process_module_filter(self, module: str) -> bool:
        raise NotImplementedError()

    @override
    def on_loop_sleep(self) -> bool:
        sleep(self.intervals_sec + random() * self.random_intervals_sec)
        if self.disable_if_maximized:
            return is_active_window_maxed(self.process_name_filters)
        else:
            return True
