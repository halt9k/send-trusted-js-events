import ctypes
import time
from win32con import *
from win32api import *
from time import sleep


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


class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]


def PressKeySI(hwnd, hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(hexKeyCode, 0x48, 0, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(hwnd, ctypes.pointer(x), ctypes.sizeof(x))
    time.sleep(0.2)


def ReleaseKeySI(hwnd, hex_key_code):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(hex_key_code, 0x48, 0x0002, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(hwnd, ctypes.pointer(x), ctypes.sizeof(x))
    time.sleep(0.2)


# PressKeySI(0x012)  # Alt
# PressKeySI(0x09)  # Tab
# ReleaseKeySI(0x09)  # ~Tab
# ReleaseKeySI(0x012)  # ~Alt

# key = ord('M')
# key = win32con.VK_*
def press_ord_key(hwnd, key, ctrl):
    if ctrl:
        keybd_event(VK_LCONTROL, 0, 0, 0)
        sleep(0.01)

    PostMessage(hwnd, WM_KEYDOWN, key, 0)
    sleep(0.01)
    PostMessage(hwnd, WM_KEYUP, key, 0)

    if ctrl:
        sleep(0.01)
        keybd_event(VK_LCONTROL, 0, KEYEVENTF_KEYUP, 0)


def PressSysKey(hwnd, key, ctrl):
    virtual_key = ctypes.windll.user32.MapVirtualKeyA(key, 0)
    PostMessage(hwnd, WM_KEYDOWN, key, 0x0001 | virtual_key << 16)
    sleep(0.01)
    PostMessage(hwnd, WM_KEYUP, key, 0x0001 | virtual_key << 16 | 0xC0 << 24)
