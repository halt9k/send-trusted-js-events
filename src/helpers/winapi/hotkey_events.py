from win32con import *
from win32api import *
from time import sleep

from helpers.winapi.windows import unsafe_sleep

''' Future experiments
SendInput = ctypes.windll.user32.SendInput
PUL = ctypes.POINTER(ctypes.c_ulong)


class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]


class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class InputI(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", InputI)]


def press_key_si(hwnd, hex_keycode):
    # press_key_si(0x012)  # Alt
    # press_key_si(0x09)  # Tab

    extra = ctypes.c_ulong(0)
    ii_ = InputI()
    ii_.ki = KeyBdInput(hex_keycode, 0x48, 0, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(hwnd, ctypes.pointer(x), ctypes.sizeof(x))
    time.sleep(0.2)


def release_key_si(hwnd, hex_key_code):
    # release_key_si(0x012)  # ~Alt
    # release_key_si(0x09)  # ~Tab

    extra = ctypes.c_ulong(0)
    ii_ = InputI()
    ii_.ki = KeyBdInput(hex_key_code, 0x48, 0x0002, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(hwnd, ctypes.pointer(x), ctypes.sizeof(x))
    time.sleep(0.2)


def press_sys_key(hwnd, key_code):
    virtual_key = ctypes.windll.user32.MapVirtualKeyA(key_code, 0)
    PostMessage(hwnd, WM_KEYDOWN, key_code, 0x0001 | virtual_key << 16)
    sleep(0.01)
    PostMessage(hwnd, WM_KEYUP, key_code, 0x0001 | virtual_key << 16 | 0xC0 << 24)
'''


def press_key(hwnd, key_code, delay_sec=0.1):
    """ key_code: can be ord('M'), ord('r'), ... """

    PostMessage(hwnd, WM_KEYDOWN, key_code, 0)
    PostMessage(hwnd, WM_KEYUP, key_code, 0)


def press_key_modified(hwnd, key_code, modifier_key_code, delay_sec=0.1):
    # TODO can it send without focus?
    """ modifier_key_code: usually will be win32con.VK_*, like VK_LSHIFT, VK_RSHIFT, VK_LCONTROL, VK_RCONTROL """

    # PostMessage may not work in combo
    with unsafe_sleep(delay_sec, hwnd, require_active=True, keep_state=True):
        keybd_event(modifier_key_code, 0, 0, 0)
    press_key(hwnd, key_code, delay_sec)
    with unsafe_sleep(delay_sec, hwnd, require_active=True, keep_state=True):
        keybd_event(modifier_key_code, 0, KEYEVENTF_KEYUP, 0)

