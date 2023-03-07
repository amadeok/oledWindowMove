# Feel free to contribute more demos back ;-)

import win32gui, win32con, win32api
import time, math, random

def _MyCallback( hwnd, extra ):
    hwnds, classes = extra
    hwnds.append(hwnd)
    classes[win32gui.GetClassName(hwnd)] = 1

def TestEnumWindows():
    windows = []
    classes = {}
    win32gui.EnumWindows(_MyCallback, (windows, classes))
    print ("Enumerated a total of %d windows with %d classes" % (len(windows),len(classes)))
    if "tooltips_class32" not in classes:
        print ("Hrmmmm - I'm very surprised to not find a 'tooltips_class32' class.")


def OnPaint_1(hwnd, msg, wp, lp):
    dc, ps=win32gui.BeginPaint(hwnd)
    win32gui.SetGraphicsMode(dc, win32con.GM_ADVANCED)
    br=win32gui.CreateSolidBrush(win32api.RGB(255,0,0))
    win32gui.SelectObject(dc, br)
    angle=win32gui.GetWindowLong(hwnd, win32con.GWL_USERDATA)
    win32gui.SetWindowLong(hwnd, win32con.GWL_USERDATA, angle+2)
    r_angle=angle*(math.pi/180)
    win32gui.SetWorldTransform(dc,
        {'M11':math.cos(r_angle), 'M12':math.sin(r_angle), 'M21':math.sin(r_angle)*-1, 'M22':math.cos(r_angle),'Dx':250,'Dy':250})
    win32gui.MoveToEx(dc,250,250)
    win32gui.BeginPath(dc)
    win32gui.Pie(dc, 10, 70, 200, 200, 350, 350, 75, 10)
    win32gui.Chord(dc, 200, 200, 850, 0, 350, 350, 75, 10)
    win32gui.LineTo(dc, 300,300)
    win32gui.LineTo(dc, 100, 20)
    win32gui.LineTo(dc, 20, 100)
    win32gui.LineTo(dc, 400, 0)
    win32gui.LineTo(dc, 0, 400)
    win32gui.EndPath(dc)
    win32gui.StrokeAndFillPath(dc)
    win32gui.EndPaint(hwnd, ps)
    return 0
wndproc_1={win32con.WM_PAINT:OnPaint_1}

def OnPaint_2(hwnd, msg, wp, lp):
    dc, ps=win32gui.BeginPaint(hwnd)
    win32gui.SetGraphicsMode(dc, win32con.GM_ADVANCED)
    l,t,r,b=win32gui.GetClientRect(hwnd)
    
    for x in range(25):
        vertices=(
            {'x':int(random.random()*r), 'y':int(random.random()*b), 'Red':int(random.random()*0xff00), 'Green':0, 'Blue':0, 'Alpha':0},
            {'x':int(random.random()*r), 'y':int(random.random()*b), 'Red':0, 'Green':int(random.random()*0xff00), 'Blue':0, 'Alpha':0},
            {'x':int(random.random()*r), 'y':int(random.random()*b), 'Red':0, 'Green':0, 'Blue':int(random.random()*0xff00), 'Alpha':0},
            )
        mesh=((0,1,2),)
        win32gui.GradientFill(dc,vertices, mesh, win32con.GRADIENT_FILL_TRIANGLE)
    win32gui.EndPaint(hwnd, ps)
    return 0
wndproc_2={win32con.WM_PAINT:OnPaint_2}

def TestSetWorldTransform():
    wc = win32gui.WNDCLASS()
    wc.lpszClassName = 'test_win32gui_1'
    wc.style =  win32con.CS_GLOBALCLASS|win32con.CS_VREDRAW | win32con.CS_HREDRAW
    wc.hbrBackground = win32con.COLOR_WINDOW+1
    wc.lpfnWndProc=wndproc_1
    class_atom=win32gui.RegisterClass(wc)       
    hwnd = win32gui.CreateWindow(wc.lpszClassName,
        'Spin the Lobster!',
        win32con.WS_CAPTION|win32con.WS_VISIBLE,
        100,100,900,900, 0, 0, 0, None)
    for x in range(500):
        win32gui.InvalidateRect(hwnd,None,True)
        win32gui.PumpWaitingMessages()
        time.sleep(0.01)
    win32gui.DestroyWindow(hwnd)
    win32gui.UnregisterClass(wc.lpszClassName, None)

def TestGradientFill():
    wc = win32gui.WNDCLASS()
    wc.lpszClassName = 'test_win32gui_2'
    wc.style =  win32con.CS_GLOBALCLASS|win32con.CS_VREDRAW | win32con.CS_HREDRAW
    wc.hbrBackground = win32con.COLOR_WINDOW+1
    wc.lpfnWndProc=wndproc_2
    class_atom=win32gui.RegisterClass(wc)       
    hwnd = win32gui.CreateWindowEx(0, class_atom,'Kaleidoscope',
        win32con.WS_CAPTION|win32con.WS_VISIBLE|win32con.WS_THICKFRAME|win32con.WS_SYSMENU,
        100,100,900,900, 0, 0, 0, None)
    s=win32gui.GetWindowLong(hwnd,win32con.GWL_EXSTYLE)
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, s|win32con.WS_EX_LAYERED)
    win32gui.SetLayeredWindowAttributes(hwnd, 0, 175, win32con.LWA_ALPHA)
    for x in range(30):
        win32gui.InvalidateRect(hwnd,None,True)
        win32gui.PumpWaitingMessages()
        time.sleep(0.3)
    win32gui.DestroyWindow(hwnd)
    win32gui.UnregisterClass(class_atom,None)

print ("Enumerating all windows...")
TestEnumWindows()
print ("Testing drawing functions ...")
TestSetWorldTransform()
TestGradientFill()
print ("All tests done!")
exit()


import PySimpleGUI as sg

"""
    Demo - "Collapsible" sections of windows
    This demo shows one techinique for creating a collapsible section (Column) within your window.
    To open/close a section, click on the arrow or name of the section.
    Section 2 can also be controlled using the checkbox at the top of the window just to
    show that there are multiple way to trigger events such as these.
    
    Feel free to modify to use the fonts and sizes of your choosing.  It's 1 line of code to make the section.
    It could have been done directly in the layout.
    Copyright 2021 PySimpleGUI.org
"""


def Collapsible(layout, key, title='', arrows=(sg.SYMBOL_DOWN, sg.SYMBOL_UP), collapsed=False):
    """
    User Defined Element
    A "collapsable section" element. Like a container element that can be collapsed and brought back
    :param layout:Tuple[List[sg.Element]]: The layout for the section
    :param key:Any: Key used to make this section visible / invisible
    :param title:str: Title to show next to arrow
    :param arrows:Tuple[str, str]: The strings to use to show the section is (Open, Closed).
    :param collapsed:bool: If True, then the section begins in a collapsed state
    :return:sg.Column: Column including the arrows, title and the layout that is pinned
    """
    return sg.Column([[sg.T((arrows[1] if collapsed else arrows[0]), enable_events=True, k=key+'-BUTTON-'),
                       sg.T(title, enable_events=True, key=key+'-TITLE-')],
                      [sg.pin(sg.Column(layout, key=key, visible=not collapsed, metadata=arrows))]], pad=(0,0))


SEC1_KEY = '-SECTION1-'
SEC2_KEY = '-SECTION2-'

section1 = [[sg.Input('Input sec 1', key='-IN1-')],
            [sg.Input(key='-IN11-')],
            [sg.Button('Button section 1',  button_color='yellow on green'),
             sg.Button('Button2 section 1', button_color='yellow on green'),
             sg.Button('Button3 section 1', button_color='yellow on green')]]

section2 = [[sg.I('Input sec 2', k='-IN2-')],
            [sg.I(k='-IN21-')],
            [sg.B('Button section 2',  button_color=('yellow', 'purple')),
             sg.B('Button2 section 2', button_color=('yellow', 'purple')),
             sg.B('Button3 section 2', button_color=('yellow', 'purple'))]]

layout =   [[sg.Text('Window with 2 collapsible sections')],
            [sg.Checkbox('Blank checkbox'), sg.Checkbox('Hide Section 2', enable_events=True, key='-OPEN SEC2-CHECKBOX-')],
            #### Section 1 part ####
            [Collapsible(section1, SEC1_KEY,  'Section 1', collapsed=True)],
            #### Section 2 part ####
            [Collapsible(section2, SEC2_KEY, 'Section 2', arrows=( sg.SYMBOL_TITLEBAR_MINIMIZE, sg.SYMBOL_TITLEBAR_MAXIMIZE))],
            [sg.Button('Button1'),sg.Button('Button2'), sg.Button('Exit')]]

window = sg.Window('Visible / Invisible Element Demo', layout)

while True:             # Event Loop
    event, values = window.read()
    print(event, values)
    if event == sg.WIN_CLOSED or event == 'Exit':
        break

    if event.startswith(SEC1_KEY):
        window[SEC1_KEY].update(visible=not window[SEC1_KEY].visible)
        #window[SEC1_KEY+'-BUTTON-'].update(window[SEC1_KEY].metadata[0] if window[SEC1_KEY].visible else window[SEC1_KEY].metadata[1])

    if event.startswith(SEC2_KEY) or event == '-OPEN SEC2-CHECKBOX-':
        window[SEC2_KEY].update(visible=not window[SEC2_KEY].visible)
        window[SEC2_KEY+'-BUTTON-'].update(window[SEC2_KEY].metadata[0] if window[SEC2_KEY].visible else window[SEC2_KEY].metadata[1])
        window['-OPEN SEC2-CHECKBOX-'].update(not window[SEC2_KEY].visible)

window.close()
