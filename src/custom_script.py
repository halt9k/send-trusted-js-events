from copy import copy
from dataclasses import dataclass
from random import random
from time import sleep

from code_tools.virtual_methods import override
from helpers.winapi.hotkey_events import press_key, press_modifier
from helpers.winapi.windows import shrink_and_arrange, get_window_state, get_title, switch_focus_window, \
    is_active_window_maxed, is_window_closed, safe_call
from observer.userscript_bridge import try_get_caption_request
from observer.custom_script_abstract import CustomScriptAbstract


@dataclass(init=True)
class UserObserverScript(CustomScriptAbstract):
    """
    disable_if_maximized: safety feauture, freezes script while user have active window maximised
    intervals_sec: sleep intervals
    proc_filters: list of exact allowed process module (exe) file names or None to disable
    """
    disable_if_maximized: bool = True
    intervals_sec: float = 0.1
    proc_filters: list = None

    @override
    def on_initial_window_setup(self, hwnd) -> bool:
        return True

    @override
    def on_custom_processing(self, hwnd, n, msg_count):
        pass

    @override
    def on_hwnd_filter(self, hwnd) -> bool:
        return True

    @override
    def on_process_module_filter(self, module: str) -> bool:
        return module.lower() in self.proc_filters

    @override
    def on_loop_sleep(self) -> bool:
        sleep(self.intervals_sec)
        if self.disable_if_maximized:
            return safe_call(is_active_window_maxed, True)(self.on_process_module_filter)
        else:
            return True
