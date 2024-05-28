import datetime
from dataclasses import dataclass
from random import random
from time import sleep
from typing import Type

from helpers.winapi.mouse_events import send_click
from helpers.winapi.windows import get_title, if_window_exist, is_active_window_maxed
from src.observer.custom_script_abstract import CustomScriptAbstract
from helpers.winapi.processes import get_process_paths, get_process_windows


def get_caption_message_request(hwnd):
    title = get_title(hwnd)
    if not title.startswith('auto_click '):
        return None

    title = title.replace('auto_click ', '')
    msg = title.replace(' — Mozilla Firefox', '')

    return msg


def mouse_req_to_xy(req):
    # cords_txt = cords_txt.replace('translate(', '')
    # cords_txt = cords_txt.replace('px, ', ' ')
    # cords = [int(s) for s in cords_txt.split() if (s.isdigit() or s == '-')]
    return [int(float(s)) for s in req.split()]


def process_click(hwnd):
    msg = get_caption_message_request(hwnd)
    if not msg:
        return None

    # TODO other reqs
    cords = mouse_req_to_xy(msg)
    if cords:
        send_click(hwnd, cords[0], cords[1])
        return True
    else:
        return False


@dataclass
class TabInfo:
    last_text: str = ''
    total_clicks: int = 0
    last_click_ms: datetime.datetime = datetime.datetime.now()
    closed: bool = False
    initialized: bool = False


class BrowserObserver:
    known_windows = {}
    observations_count = 0

    def __init__(self, user_script: Type[CustomScriptAbstract], debug_messages = False):
        """
        proc_filters: process name must be exactly one of elements
        caption_filters: window caption (for browsers - tab caption) must include one of elements
        disable_if_maximized: safety feauture, freezes script while user have active window maximised
        freq_sec: observer checks intervals
        rnd_freq_sec: max extra addition to observer checks intervals
        """
        self.user_script = user_script
        self.debug_messages = debug_messages

    def cleanup_closed_tabs(self):
        # returns amount of removed tabs

        pop_keys = []
        for key in self.known_windows.keys():
            if self.known_windows[key].closed:
                pop_keys += [key]

            self.known_windows[key].closed = not if_window_exist(key)

        for key in pop_keys:
            self.known_windows.pop(key)

        return len(pop_keys)

    def provide_caption_commands(self, hwnd):
        # if sqrt(sites[hwnd].total) / 20 > random():
        # print ('Skipped')
        # continue

        if self.known_windows[hwnd].last_text == get_title(hwnd):
            return

        if process_click(hwnd):
            self.known_windows[hwnd].last_message_ms = datetime.datetime.now()
            self.known_windows[hwnd].total_messages_send += 1
            self.known_windows[hwnd].last_text = get_title(hwnd)

    def initialize_window(self, hwnd):
        if hwnd not in self.known_windows.keys():
            self.known_windows[hwnd] = TabInfo()

            self.known_windows[hwnd].closed = False
            self.known_windows[hwnd].initialized = False
            self.known_windows[hwnd].added = datetime.time()
            self.known_windows[hwnd].total_messages_send = 0

        elif not self.known_windows[hwnd].initialized:
            if self.user_script.on_initial_window_setup(hwnd):
                self.known_windows[hwnd].initialized = True

        return self.known_windows[hwnd].initialized

    def process_window(self, hwnd):
        if not self.initialize_window(hwnd):
            return

        initialized_windows = [key for key, val in self.known_windows.items() if val.initialized and not val.closed]
        n = initialized_windows.index(hwnd)
        self.user_script.on_custom_processing(hwnd, n, self.known_windows[hwnd].total_messages_send)

        self.provide_caption_commands(hwnd)

    def process_windows(self):
        count_changed = self.cleanup_closed_tabs()

        procs = get_process_paths(self.user_script.on_process_module_filter)
        for pid, name in procs:
            data = get_process_windows(pid)
            if not data:
                continue

            # proc_text = "PId {0:d}{1:s}windows:".format(pid, " (File: [{0:s}]) ".format(name) if name else " ")
            # print(proc_text)
            for hwnd, _ in data:
                # TODO not transparent enough
                req = get_caption_message_request(hwnd)
                if not req and not self.user_script.on_hwnd_filter(hwnd):
                    continue

                try:
                    self.process_window(hwnd)
                except Exception as e:
                    if self.debug_messages:
                        raise
                    else:
                        self.known_windows.pop(hwnd)
                        print(e)

    def run(self):
        while True:
            skip_next = self.user_script.on_loop_sleep()
            if not skip_next:
                self.process_windows()
            else:
                print('Userscrript requested skip, observer is idle.')
            self.observations_count += 1
