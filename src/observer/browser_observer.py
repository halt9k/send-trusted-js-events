import datetime
from dataclasses import dataclass
from random import random
from time import sleep

from helpers.winapi.mouse_events import send_click
from helpers.winapi.windows import get_caption, if_window_exist, is_active_window_maxed
from custom_scripts import initial_window_setup, arrage_window, is_arranged
from helpers.winapi.processes import get_procs_and_captions, enum_process_windows


def process_click(hwnd):
    cords = caption_to_xy(get_caption(hwnd))
    if cords:
        send_click(hwnd, cords[0], cords[1])
    return cords


def caption_to_xy(text):
    if not text.startswith('auto_click '):
        return None

    cords_txt = text.replace('auto_click ', '')
    # cords_txt = cords_txt.replace('translate(', '')
    # cords_txt = cords_txt.replace('px, ', ' ')
    # TODO
    cords_txt = cords_txt.replace(' — Mozilla Firefox', '')
    # cords = [int(s) for s in cords_txt.split() if (s.isdigit() or s == '-')]
    return [int(float(s)) for s in cords_txt.split()]


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

    def __init__(self, proc_filters: [], caption_filters: [], disable_if_maximized, intervals_sec, rnd_intervals_sec):
        """
        proc_filters: process name must be exactly one of elements
        caption_filters: window caption (for browsers - tab caption) must include one of elements
        disable_if_maximized: safety feauture, freezes script while user have active window maximised
        freq_sec: observer checks intervals
        rnd_freq_sec: max extra addition to observer checks intervals
        """

        self.process_name_filters = proc_filters
        # TODO
        self.caption_filters = caption_filters
        self.intervals_sec = intervals_sec
        self.random_intervals_sec = rnd_intervals_sec
        self.disable_if_maximized_window = disable_if_maximized

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

    def process_window(self, hwnd, force_rearrange):
        if not is_arranged(hwnd):
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
            initial_window_setup(hwnd)

        if force_rearrange or self.known_browser_tabs[hwnd].total_clicks == 0:
            n = list(self.known_browser_tabs.keys()).index(hwnd)
            arrage_window(hwnd, n)

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

        if self.disable_if_maximized_window and is_active_window_maxed(self.process_name_filters):
            print('Active window is maxed, observer paused.')
            return

        procs = get_procs_and_captions(proc_name_filters=self.process_name_filters)
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
