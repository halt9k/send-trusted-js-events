from datetime import datetime
from dataclasses import dataclass
from typing import Type, Dict

import pywintypes

from helpers.winapi.windows import get_title, is_window_closed
from observer.userscript_bridge import process_caption
from src.observer.custom_script_abstract import CustomScriptAbstract
from helpers.winapi.processes import get_module_paths, get_process_windows


@dataclass
class TabInfo:
    last_finished_title: str = ''
    requests_finished: int = 0
    last_message_ms: datetime = datetime.now()
    initialized: bool = False
    added: datetime = None


class BrowserObserver:
    known_windows: Dict[int, TabInfo] = {}
    observations_count = 0

    def __init__(self, user_script: CustomScriptAbstract,
                 ignore_exceptions: [Type[Exception]],
                 ignore_pywin_exceptions: [str]):
        """
        expected_exceptions: which python exceptions to ignore
        expected_pywin_exceptions: which pywintype.error descriptions to ignore
        """
        self.user_script = user_script
        self.ignore_exceptions = ignore_exceptions
        self.ignore_pywin_exceptions = ignore_pywin_exceptions

    def cleanup_closed_tabs(self):
        # returns amount of removed tabs

        pop_keys = []
        for key in self.known_windows.keys():
            if is_window_closed(key):
                pop_keys += [key]

        for key in pop_keys:
            self.known_windows.pop(key)

        return len(pop_keys)

    def deliver_caption_requests(self, hwnd):
        title = get_title(hwnd)
        if self.known_windows[hwnd].last_finished_title == title:
            return

        if process_caption(hwnd):
            self.known_windows[hwnd].last_message_ms = datetime.now()
            self.known_windows[hwnd].requests_finished += 1
            self.known_windows[hwnd].last_finished_title = title

    def initialize_window(self, hwnd):
        if hwnd not in self.known_windows.keys():
            self.known_windows[hwnd] = TabInfo()

            self.known_windows[hwnd].initialized = False
            self.known_windows[hwnd].added = datetime.now()

        elif not self.known_windows[hwnd].initialized:
            if self.user_script.on_initial_window_setup(hwnd):
                self.known_windows[hwnd].initialized = True

        return self.known_windows[hwnd].initialized

    def process_hwnd(self, hwnd):
        if not self.initialize_window(hwnd):
            return

        initialized_windows = [key for key, val in self.known_windows.items() if val.initialized]
        n = initialized_windows.index(hwnd)
        self.user_script.on_custom_processing(hwnd, n, self.known_windows[hwnd].requests_finished)

        self.deliver_caption_requests(hwnd)

    def process_hwnd_safely(self, hwnd):
        if not self.user_script.on_hwnd_filter(hwnd):
            return

        try:
            self.process_hwnd(hwnd)
        except Exception as e:
            ignore = type(e) in self.ignore_exceptions or \
                     (type(e) is pywintypes.error and e.strerror in self.ignore_pywin_exceptions)
            if ignore:
                self.known_windows.pop(hwnd)
                print(f"Expected exception during hwnd processing {hwnd}, hwnd will be reinitialised. ")
                print(e)
            else:
                raise

    def process_running_modules(self):
        count_changed = self.cleanup_closed_tabs()

        proc_paths = get_module_paths(self.user_script.on_process_module_filter)
        for pid, name in proc_paths:
            proc_hwnds = get_process_windows(pid)
            if not proc_hwnds:
                continue

            # proc_text = "PId {0:d}{1:s}windows:".format(pid, " (File: [{0:s}]) ".format(name) if name else " ")
            # print(proc_text)
            for hwnd, _ in proc_hwnds:
                self.process_hwnd_safely(hwnd)

    def run(self):
        while True:
            skip_next = self.user_script.on_loop_sleep()
            if not skip_next:
                self.process_running_modules()
            else:
                print('Userscrript requested skip, observer is idle.')
            if self.observations_count % 100 == 0:
                print(f'Obserwer is active. Observations count: {self.observations_count}')
            self.observations_count += 1
