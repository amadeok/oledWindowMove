import ctypes
from sys import platform as sys_platform
if sys_platform == 'win32':
    from win32gui import EnumWindows, GetWindowText, IsWindowVisible, IsIconic
    from win32process import GetWindowThreadProcessId

def get_visible_windows():
    if sys_platform == 'win32':
        class TITLEBARINFO(ctypes.Structure):
            _fields_ = [("cbSize", ctypes.wintypes.DWORD), ("rcTitleBar", ctypes.wintypes.RECT),
                    ("rgstate", ctypes.wintypes.DWORD * 6)]
        visible_windows = []
        def callback(hwnd, _):
            # Title Info Initialization
            title_info = TITLEBARINFO()
            title_info.cbSize = ctypes.sizeof(title_info)
            ctypes.windll.user32.GetTitleBarInfo(hwnd, ctypes.byref(title_info))

            # DWM Cloaked Check
            isCloaked = ctypes.c_int(0)
            ctypes.WinDLL("dwmapi").DwmGetWindowAttribute(hwnd, 14, ctypes.byref(isCloaked), ctypes.sizeof(isCloaked))

            # Variables
            title = GetWindowText(hwnd)

            # Append HWND to list
            if not IsIconic(hwnd) and IsWindowVisible(hwnd) and title != '' and isCloaked.value == 0:
                if not (title_info.rgstate[0] & 32768): #STATE_SYSTEM_INVISIBLE 
                    _, cpid = GetWindowThreadProcessId(hwnd)
                    visible_windows.append({'title' : title, 'pid' : cpid, 'hwnd' : hwnd})
        EnumWindows(callback, None)
        return visible_windows
    elif sys_platform == 'linux':
        return
    