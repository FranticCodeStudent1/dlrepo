import ctypes
from ctypes import wintypes
import os
import time

user32 = ctypes.WinDLL('user32', use_last_error=True)

INPUT_MOUSE    = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_UNICODE     = 0x0004
KEYEVENTF_SCANCODE    = 0x0008

MAPVK_VK_TO_VSC = 0

# msdn.microsoft.com/en-us/library/dd375731
VK_LBUTTON = 0x01
VK_RBUTTON = 0x02
VK_MBUTTON = 0x04
VK_BACK = 0x08
VK_TAB = 0x09
VK_RETURN = 0x0D
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_CAPITAL = 0x14
VK_ESCAPE = 0x1B
VK_SPACE = 0x20
VK_LEFT = 0x25
VK_UP = 0x26
VK_RIGHT = 0x27
VK_DOWN = 0x28
VK_PRTSC = 0x2C
VK_DELETE = 0x2E
VK_NUM = [0x30, 0x32, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39]
VK_ALPHABET = {
    "a": 0x41,
    "b": 0x42,
    "c": 0x43,
    "d": 0x44,
    "e": 0x45,
    "f": 0x46,
    "g": 0x47,
    "h": 0x48,
    "i": 0x49,
    "j": 0x4A,
    "k": 0x4B,
    "l": 0x4C,
    "m": 0x4D,
    "n": 0x4E,
    "o": 0x4F,
    "p": 0x50,
    "q": 0x51,
    "r": 0x52,
    "s": 0x53,
    "t": 0x54,
    "u": 0x55,
    "v": 0x56,
    "w": 0x57,
    "x": 0x58,
    "y": 0x59,
    "z": 0x5A,
}
VK_LWIN = 0x5B
VK_RWIN = 0x5C
VK_DECIMAL = 0x6E
VK_SHIFT = 0xA0
VK_CONTROL = 0xA2

#Mouse codes
ME_LKEY = 0x02
ME_LUP = 0x04
ME_RKEY = 0x08
ME_RUP = 0x10

# C struct definitions

wintypes.ULONG_PTR = wintypes.WPARAM

class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx", wintypes.LONG),
                ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk", wintypes.WORD),
                ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

    def __init__(self, *args, **kwds):
        super(KEYBDINPUT, self).__init__(*args, **kwds)
        # some programs use the scan code even if KEYEVENTF_SCANCODE
        # isn't set in dwFflags, so attempt to map the correct code.
        if not self.dwFlags & KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk, MAPVK_VK_TO_VSC, 0)

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg",    wintypes.DWORD),
                ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD))

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT))
    _anonymous_ = ("_input",)
    _fields_ = (("type",   wintypes.DWORD),
                ("_input", _INPUT))

LPINPUT = ctypes.POINTER(INPUT)

def _check_count(result, func, args):
    if result == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    return args

user32.SendInput.errcheck = _check_count
user32.SendInput.argtypes = (wintypes.UINT, # nInputs
                             LPINPUT,       # pInputs
                             ctypes.c_int)  # cbSize

# Functions

def PressKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=hexKeyCode))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=hexKeyCode, dwFlags=KEYEVENTF_KEYUP))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def SendKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=hexKeyCode))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))
    x = INPUT(type=INPUT_KEYBOARD, ki=KEYBDINPUT(wVk=hexKeyCode, dwFlags=KEYEVENTF_KEYUP))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

def SendString(string):
    x = 0
    alph = "abcdefghijklmnopqrstuvwxyz"
    alphcapital = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    num = "0123456789"
    for x in range(len(string)):
        if string[x] in (alph or num or alphcapital):
            if string[x] in alphcapital:
                index = alphcapital.find(string[x])
                PressKey(VK_SHIFT)
                SendKey(VK_ALPHABET[alph[index]])
                ReleaseKey(VK_SHIFT)
            if string[x] in alph:
                SendKey(VK_ALPHABET[string[x]])
            if string[x] in num:
                SendKey(VK_NUM[int(string[x])])
        es = string[x]
        if es.isspace() == True:
            SendKey(VK_SPACE)
        if string[x] == ".":
            SendKey(VK_DECIMAL)

def MouseClick(hexMouseCode):
    x = INPUT(type=INPUT_MOUSE, mi=MOUSEINPUT(dwFlags=hexMouseCode))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))
    if hexMouseCode == ME_LKEY:
        hexMouseCode = ME_LUP
    else:
        hexMouseCode = ME_RUP
    x = INPUT(type=INPUT_MOUSE, mi=MOUSEINPUT(dwFlags=hexMouseCode))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))
