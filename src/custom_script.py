from copy import copy
from dataclasses import dataclass
from random import random
from time import sleep

from win32con import VK_LCONTROL

from code_tools.virtual_methods import override
from helpers.winapi.hotkey_events import press_key, press_modifier, press_char
from helpers.winapi.windows import shrink_and_arrange, get_window_state, get_title, switch_focus_window, \
    is_active_window_maxed, is_window_closed, safe_call, get_dims
from observer.userscript_bridge import try_get_caption_request
from observer.custom_script_abstract import CustomScriptAbstract

ARRANGE_WIDTH, ARRANGE_HEIGHT = 350, 500
ERR = 30


@dataclass(init=True)
class UserObserverScript(CustomScriptAbstract):
    """
    proc_filters: list of exact allowed process module (exe) file names or None to disable
    caption_filters: list of text window titles must include or None to disable
    disable_if_maximized: safety feauture, freezes script while user have active window maximised
    intervals_sec: sleep intervals
    random_intervals_sec: extra addition to sleep intervals
    """
    disable_if_maximized: bool = True
    intervals_sec: float = 0.1
    random_intervals_sec: float = 0.3
    proc_filters: list = None
    initial_caption_filters: list = None
    known_windows = {}
    keys_passed = {}

    @staticmethod
    def mute_tab(hwnd):
        with press_modifier(hwnd, modifier_key_code=VK_LCONTROL):
            press_char(hwnd, 'm')

    @staticmethod
    def is_shrinked(hwnd):
        w, h = get_dims(hwnd)
        return abs(w - ARRANGE_WIDTH) < ERR and abs(h - ARRANGE_HEIGHT) < ERR

    @override
    def on_initial_window_setup(self, hwnd) -> bool:
        if not self.is_shrinked(hwnd):
            return False

        if hwnd not in self.keys_passed:
            with switch_focus_window(hwnd):
                self.mute_tab(hwnd)
                # relies on userscript auto start by s
                press_char(hwnd, 'r', only_down=False)
            self.keys_passed[hwnd] = True

        req = try_get_caption_request(hwnd)
        if req:
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

        if try_get_caption_request(hwnd):
            print(f'Adding possibly earlier abadoned window {hwnd} since a request detected.')
            self.known_windows[hwnd] = True
            return True

        caption = get_title(hwnd)
        contains = [f for f in self.initial_caption_filters if f in caption]
        if len(contains) > 0:
            self.known_windows[hwnd] = True
            return True
        return False

    @override
    def on_process_module_filter(self, module: str) -> bool:
        return module.lower() in self.proc_filters

    def cleanup(self):
        self.known_windows = {k: v for k, v in self.known_windows.items() if not is_window_closed(k)}
        self.keys_passed = {k: v for k, v in self.keys_passed.items() if not is_window_closed(k)}

    @override
    def on_loop_sleep(self) -> bool:
        sleep(self.intervals_sec + random() * self.random_intervals_sec)
        self.cleanup()
        if self.disable_if_maximized:
            return safe_call(lambda: is_active_window_maxed(self.on_process_module_filter), False)
        else:
            return True
