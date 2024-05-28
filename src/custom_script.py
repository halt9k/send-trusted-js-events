from copy import copy
from dataclasses import dataclass
from random import random
from time import sleep

from win32con import VK_LCONTROL

from code_tools.virtual_methods import override
from helpers.winapi.hotkey_events import press_key, press_key_modified
from helpers.winapi.windows import shrink_and_arrange, get_window_state, get_title, activate, get_dims, \
    safe_sleep, WindowState, is_active_window_maxed
from observer.custom_script_abstract import CustomScriptAbstract

ARRANGE_WIDTH, ARRANGE_HEIGHT = 330, 510


@dataclass(init=True)
class UserObserverScript(CustomScriptAbstract):
    """
    proc_filters: list of exact allowed process module (exe) file names or None to disable
    caption_filters: list of text window titles must include or None to disable
    """
    disable_if_maximized: bool = True
    intervals_sec: float = 0.1
    random_intervals_sec: float = 0.3
    proc_filters: list = None
    caption_filters: list = None
    known_windows = copy({})
    keys_passed = copy({})

    @staticmethod
    def mute_tab(hwnd):
        with safe_sleep(0.1, hwnd, require_active=True):
            press_key_modified(hwnd, key_code=ord('M'), modifier_key_code=VK_LCONTROL)

    @staticmethod
    def is_shrinked(hwnd):
        w, h = get_dims(hwnd)
        return abs(w - ARRANGE_WIDTH) < 10 and abs(h - ARRANGE_HEIGHT) < 10

    # TODO what if fails, repeat?
    @override
    def on_initial_window_setup(self, hwnd) -> bool:
        if not self.is_shrinked(hwnd):
            return False

        if hwnd not in self.keys_passed:
            with activate(hwnd):
                self.mute_tab(hwnd)

                # relies on userscript auto start by s
                press_key(hwnd, ord('R'))
                self.keys_passed[hwnd] = True

        caption = get_title(hwnd)
        if caption.startswith("auto_click"):
            return True

        return False

    @override
    def on_custom_processing(self, hwnd, n, msg_count):
        shrink_and_arrange(hwnd, n, ARRANGE_WIDTH, ARRANGE_HEIGHT)
        sleep(0.1)

    @override
    def on_hwnd_filter(self, hwnd) -> bool:
        if hwnd in self.known_windows:
            return True

        caption = get_title(hwnd)
        if 'lichess.org' in caption:
            self.known_windows[hwnd] = True
            return True
        return False

    @override
    def on_process_module_filter(self, module: str) -> bool:
        return module.lower() in self.proc_filters

    @override
    def on_loop_sleep(self) -> bool:
        sleep(self.intervals_sec + random() * self.random_intervals_sec)
        if self.disable_if_maximized:
            return is_active_window_maxed(self.on_process_module_filter)
        else:
            return True
