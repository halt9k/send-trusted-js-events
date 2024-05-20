import datetime
from dataclasses import dataclass
from random import random
from time import sleep

from win32gui import GetForegroundWindow

from helpers.winapi.interactions import if_window_exist, get_caption, is_window_state_maxed
from helpers.winapi.interactions_2 import is_popup, setup_init, rearrage_window_tile, process_click
from helpers.winapi.processes import get_procs_and_captions, enum_process_windows


@dataclass
class TabInfo:
    last_text: str = ''
    total_clicks: int = 0
    last_click_ms: datetime.datetime = datetime.datetime.now()
    closed: bool = False
    initialized: bool = False


class BrowserObserver:
    known_browser_tabs = {}
    new_window = False
    cheks_done = 0

    def __init__(self, proc_name_filter, disable_if_maximized, intervals_sec, random_interval_extra_sec):
        # disable_if_maximized: safety feauture, stops sending anything in case if user have browser window full screen

        self.intervals_sec = intervals_sec
        self.random_intervals_sec = random_interval_extra_sec
        self.disable_if_maximized_window = disable_if_maximized
        self.proc_name_filter = proc_name_filter

    def cleanup_closed_tabs(self):
        # returns amount of removed tabs

        pop_keys = []
        for key in self.known_browser_tabs.keys():
            if self.known_browser_tabs[key].closed:
                pop_keys += [key]

            self.known_browser_tabs[key].closed = not if_window_exist(key)

        for key in pop_keys:
            self.known_browser_tabs.pop(key)

        return len(pop_keys)

    def is_active_tab_maxed(self) -> bool:
        handle = GetForegroundWindow()
        if not handle:
            return False

        procs = get_procs_and_captions(filter_by_module_name=self.proc_name_filter)
        handles = [enum_process_windows(x[0]) for x in procs]
        handles_with_windows = [x for x in handles if x != []]
        flatten = [x[0] for y in handles_with_windows for x in y]

        if handle not in flatten:
            return False

        print('Active tab is maxed: ' + str(is_window_state_maxed(handle)))
        return is_window_state_maxed(handle)

    def process_window(self, hwnd, force_rearrange):
        if not is_popup(hwnd):
            return

        if hwnd not in self.known_browser_tabs.keys():
            self.known_browser_tabs[hwnd] = TabInfo()
            force_rearrange = True

            self.known_browser_tabs[hwnd].closed = False
            self.known_browser_tabs[hwnd].initialized = False
            self.known_browser_tabs[hwnd].added = datetime.time()

        last_capt = self.known_browser_tabs[hwnd].last_text
        if last_capt.startswith("auto_click"):
            self.known_browser_tabs[hwnd].initialized = True

        if not self.known_browser_tabs[hwnd].initialized:
            setup_init(hwnd)

        if force_rearrange or self.known_browser_tabs[hwnd].total_clicks == 0:
            n = list(self.known_browser_tabs.keys()).index(hwnd)
            rearrage_window_tile(hwnd, n)

        if self.known_browser_tabs[hwnd].last_text == get_caption(hwnd):
            return

        self.known_browser_tabs[hwnd].total_clicks += 1
        # if sqrt(sites[hwnd].total) / 20 > random():
        # print ('Skipped')
        # continue

        self.known_browser_tabs[hwnd].last_text = get_caption(hwnd)
        if process_click(hwnd):
            self.known_browser_tabs[hwnd].last_click_ms = datetime.datetime.now()

    def process_windows(self):
        count_changed = self.cleanup_closed_tabs()

        if self.disable_if_maximized_window and self.is_active_tab_maxed():
            return

        procs = get_procs_and_captions(filter_by_module_name=self.proc_name_filter)
        for pid, name in procs:
            data = enum_process_windows(pid)
            if not data:
                continue

            # proc_text = "PId {0:d}{1:s}windows:".format(pid, " (File: [{0:s}]) ".format(name) if name else " ")
            # print(proc_text)
            for hwnd, _ in data:
                try:
                    self.process_window(hwnd, count_changed)
                except Exception as e:
                    self.known_browser_tabs.pop(hwnd)
                    print(e)

    def run(self):
        self.process_windows()
        while not sleep(self.intervals_sec + random() * self.random_intervals_sec):
            self.cheks_done += 1
            self.process_windows()
