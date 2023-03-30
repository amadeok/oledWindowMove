import pygetwindow as gw
import sys, win32gui,win32process, os

#w = gw.getWindowsWithTitle("SVP - Control Panel")[0]

import win32gui
l = []

print (sys.argv)
x = int(sys.argv[1])
y = int(sys.argv[2])
input_text = sys.argv[3]

def enumHandler(hwnd, lParam):
    if input_text.lower() in win32gui.GetWindowText(hwnd).lower():
        l.append([hwnd, win32process.GetWindowThreadProcessId(hwnd)[1]])

win32gui.EnumWindows(enumHandler, None)
pid = os.getpid()
print("pid ", pid)
for w_ in l:
    
    w = gw.Window(w_[0])
    print(w.title, w_[1])
    if " ".join(elem for elem in sys.argv[1:-1]) in w.title: continue
    w.moveTo(x, y)