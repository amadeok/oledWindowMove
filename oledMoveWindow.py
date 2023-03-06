import os, threading, random
import msvcrt, ctypes, pyautogui
import psutil 
import win32pipe, win32file, pywintypes, win32api, win32con, win32gui,win32process
import pygetwindow as gw
from time import sleep

import getviswin as ge

import PySimpleGUI as sg
from enums import *
import mover
from logging import *
import pygame
from pynput.mouse import Listener

all = gw.getAllWindows()
all_ = [[t.title] for t in all]
# for count, elem in enumerate(all):
#     all_[count].append(elem.visible)
# print()
window = None


#print(win_list)


#SEC1_KEY = '-SECTION1-'

mover_list = []

def get_path_from_hwd(hwd):
    try:
        if hwd != 0:
            threadid,pid = win32process.GetWindowThreadProcessId(hwd)
            return psutil.Process(pid).exe() 
        else:
            return ""
    except: 
        return ""

def search_handle(hwnd, input_text):
    title = win32gui.GetWindowText(hwnd)
    path = get_path_from_hwd(hwnd)

    if input_text.lower() in title.lower() or input_text.lower() in path.lower():
        return hwnd
    return False
        
def find_handle_from_text(win_list, input_text, search_parent):
    for win in win_list:
        if win.title == "": continue

        ret = search_handle(win._hWnd, input_text)
        if ret: return ret

        if search_parent:
            try:
                parent_hwnd = win32gui.GetParent(win._hWnd)
                ret = search_handle(win._hWnd, input_text)
                if ret: return ret
            except Exception as e:
                print(e) 

    return None

    
def add_sub_row(text, row_counter, found=True):
    entry_c = mover_list[row_counter].entry_counter
    key=('-ROW2-',entry_c, row_counter)
    found_or_not = " found: " + str(found)  if found else " NOT found"
    row = [sg.pin(
        sg.Col([[
            sg.Button("X", border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), key=('-DEL2-', entry_c, row_counter)),
            sg.Input(text, expand_x=True, enable_events=True, key=('-DESC-', entry_c, row_counter)),
            sg.Input("", size=(1,1), enable_events=True, key=('-dir_choose-', entry_c, row_counter)),
            sg.Text(f'Row2 {entry_c}, {row_counter} , window {found_or_not}', key=('-STATUS-', entry_c, row_counter))]],
        key=key
        ))],
    
    window.extend_layout(window[('-ROW_PANEL2-', row_counter)], row)
    mover_list[row_counter].entry_counter+=1
    event, values = window.read(timeout=0.0001)
    window[key].bind("<Return>", "_Enter")
   # window[key].bind('<Control-z>', 'STRING TO APPEND')




def create_row(row_counter, row_number_view):
    mover_list.append(mover.mover(row_counter, window))

    arrows=(sg.SYMBOL_DOWN, sg.SYMBOL_UP)
    collapsed=False
    key = '-SECTION' + str(row_counter) + '-'
    def_speed = 60
    layout = [
            
            #[sg.Input('Input sec 1', key='-IN1-'), sg.Input(key='-IN11-')],
            [sg.Slider(range=(1, 3600), disable_number_display=True,  expand_x=True, enable_events=True, orientation="horizontal", key=("slider", row_counter), default_value=def_speed),
             sg.Text(int(def_speed*(def_speed/6)*(1/500)), size=(10,1), key=("slider_out", row_counter)),
            sg.Checkbox('Diagonal Motion', enable_events=True, default=True, key=("Diagonal", row_counter), size=(13,1))

             ],

             [sg.Combo(['Refresh'], enable_events=True,expand_x=True, size=(75,1), key=("selector", row_counter)), 
               sg.Checkbox('Auto', enable_events=True, key=("AutoCB", row_counter), default=False),
                sg.Checkbox('Parent', enable_events=True, key=("Parent", row_counter), default=True),
                sg.Checkbox('Group', enable_events=True, key=("Group", row_counter), default=True),

               ],
               #[ sg.Button("Show profile")],
            [sg.Column([], k=('-ROW_PANEL2-', row_counter))],

            [sg.Button('Pick top left', key=("-PTL", row_counter),  button_color='yellow on green'),
             sg.Button('Pick bottom right',key=("-PBR", row_counter), button_color='yellow on green'),
             sg.Button('Start',key=("start_stop", row_counter), button_color='yellow on green'),
            sg.Button('which',key=("which", row_counter), button_color='yellow on green'),

             #sg.Button('Button3 section 1', button_color='yellow on green')
             ]
             ]

    return [sg.pin(
        sg.Column([[
                sg.Button("X", border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), key=('-DEL-', row_counter)),
                sg.T((arrows[1] if collapsed else arrows[0]), enable_events=True, k=('-BUTTON-', row_counter)),
                sg.T(f"Instance {row_counter}" , enable_events=True, key=('-TITLE-', row_counter))],
                [sg.pin(sg.Column(layout, key=('-SECTION-', row_counter), visible=not collapsed, metadata=arrows))]], pad=(0,0),
                
            key=('-ROW-', row_counter)
            ))]



def on_click_tlc(x, y, button, pressed):
    mover_list[curr_row].top_left_coor = coor(x, y)
    mover_list[curr_row].update_active_area()
    listener.stop()

def on_click_brc(x, y, button, pressed):
    mover_list[curr_row].bottom_right_coor = coor(x, y)
    mover_list[curr_row].update_active_area()
    listener.stop()

def open_window():
    layout = [[sg.Text("New Window", key="new"), sg.Button("Get Size", enable_events=True)
               ]]
    window = sg.Window("OledPreviewWin", layout, resizable=True, size=(mover_list[curr_row].active_area.width, mover_list[curr_row].active_area.height))
    x = mover_list[curr_row].active_area.topleft[0]
    y = mover_list[curr_row].active_area.topleft[1]
   # window.move(x, y) 
    # sleep(1)
    # window2 = gw.getWindowsWithTitle ('OledPreviewWin')
    # if len(window2):
    #     window2[0].moveTo(x,y)

    choice = None
    moved = False
    while True:
        event, values = window.read(timeout=0.5)
        
        if not moved: 
            window.move(x, y) 
        moved = True

        if event == "Get Size":
            loc = window.current_location()
            size = window.current_size_accurate()
  
            #mover_list[curr_row].update_active_area()
            mover_list[curr_row].active_area = pygame.Rect(loc[0], loc[1], size[0], size[1])
            mover_list[curr_row].top_left_coor = mover_list[curr_row].active_area.topleft
            mover_list[curr_row].bottom_right_coor = mover_list[curr_row].active_area.bottomright
            update_sug(curr_row)

        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        
    window.close()



def update_speed(id):
    event, values = window.read(timeout=0.0001)

    a = values[('slider', id)]
    a2 = int(a*(a/6)*(1/500))
    if a2 == 0: a2 = 1
    window[("slider_out", id)].update(a2)
    mover_list[id].pixels_per_min = a2


def update_sug(id):
    mover_list[id].get_suggest_window_list()
    window[("selector", id)].update(values=mover_list[id].suggest_win_list_str)#, value=values['-COMBO-'])

def init(id):
    window[("selector", id)].bind("<Return>", "_Enter")
    window[("selector", id)].bind("<FocusIn>", "FocusIn")

    update_speed(id)
    update_sug(id)


def add_to_sub_row(handle, row, text):
    m = mover_list[row]
    if handle:
        win = gw.Window(handle)
        m.win_list.append([win, ("-ROW2-", len(m.win_list), m.id), True, m.direction if m.group_windows else m.get_random_direction()])
        add_sub_row(text, row, found=win.title)
    else:
        m.win_list.append([None, ("-ROW2-", len(m.win_list), m.id), True, m.direction if m.group_windows else m.get_random_direction()])
        add_sub_row(text, row, found=False)


def hide_all_sub(row, keylist=None, only_hide=False):
    for c, elem in enumerate(mover_list[row].win_list):
        if elem and not elem[2]:
            window[elem[1]].update(visible=False)
            mover_list[row].win_list[c][0] = None
            print("none" if not elem[0] else elem[0].title, " ", elem[1])
    return

    list_ = window.key_dict if not keylist else keylist
    for elem in list_:
        if elem[0] == "-ROW2-" and elem[2] == curr_row:
            
            if not only_hide:
                mover_list[curr_row].win_list[elem[1]] = None
                window[elem].update(visible=False)
            else:
                if  mover_list[curr_row].win_list[elem[1]] == None:
                    window[elem].update(visible=False)


layout = [  [sg.Text('Add and "Delete" Rows From a Window', font='15')],
            [sg.Column([create_row(0, 1)], k='-ROW_PANEL-')],
            [sg.Text("Exit", enable_events=True, key='-EXIT-', tooltip='Exit Application'),
            sg.Text("Refresh", enable_events=True, key='-REFRESH-', tooltip='Exit Application'),
            sg.Text('+', enable_events=True, k='-ADD_ITEM-', tooltip='Add Another Item'),
            sg.Button("prev", border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), key=('-winp-')),
            ],
            
]


window = sg.Window('Dynamically Adding Elements', 
    layout,  use_default_focus=False, font='15', finalize=True)

mover_list[0].ui_ref = window
init(0)

row_counter = 0
row_number_view = 1
curr_row = 0

window2 = None




while True:

    event, values = window.read()
    #print(event)
    if event == sg.WIN_CLOSED or event == '-EXIT-':
        break
    
    if type(event) == tuple:
        if type(event[0]) == tuple:
            curr_row = event[0][1]
            if event[0][0] == "selector":
                mov = mover_list[curr_row]
                if event[1] == "FocusIn":
                    print("focus in")
                    mover_list[curr_row].get_suggest_window_list()
                    window[("selector", curr_row)].update(values=mover_list[curr_row].suggest_win_list_str)
                else:
                    text = window[event[0]].get()

                    handle = find_handle_from_text(gw.getAllWindows(), text, window[("Parent", curr_row)])
                    #wins = gw.getWindowsWithTitle(text)
                    add_to_sub_row(handle, curr_row, text)



        else:
            curr_row = event[len(event)-1]
            if event[0] == '-DEL-':
                row_number_view -= 1
                mover_list[event[1]] = None
                cur_key = '-SECTION' + str(event[1]) + '-'
                window['-ROW-', event[1]].update(visible=False)

            elif event[0] == '-BUTTON-':
                window[('-SECTION-', event[1])].update(visible=not window[('-SECTION-', event[1])].visible)
                pass
               # window[SEC1_KEY].update(visible=not window[SEC1_KEY].visible)
               # window[SEC1_KEY+'-BUTTON-'].update(window[SEC1_KEY].metadata[0] if window[SEC1_KEY].visible else window[SEC1_KEY].metadata[1])

            if "PTL" in event[0]:
                with Listener(on_click=on_click_tlc) as listener:
                    listener.join()
                    window[event].update(mover_list[event[1]].top_left_coor)
                update_sug(event[1])

            elif "PBR" in event[0]:
                with Listener(on_click=on_click_brc) as listener:
                    listener.join()
                    window[event].update(mover_list[event[1]].bottom_right_coor)
                update_sug(event[1])

            elif "start_stop" in event[0]:
                if mover_list[event[1]].loop_running:
                    mover_list[event[1]].stop = True
                else:
                    mover_list[event[1]].start_loop()
                sleep(0.1)
            elif event[0 ] == "which":
                print("\n")
                for key in window.key_dict:
                    if "-ROW2-" in key and window[key].visible:
                        print(key)
            elif "selector" in event[0]:
                text = window[event].get()  # use the combo key
                if text == "Refresh":
                    values=mover_list[curr_row].get_suggest_window_list()
                    window[event].update(values=mover_list[curr_row].suggest_win_list_str)#, value=values['-COMBO-'])
                else:
                    wins = gw.getWindowsWithTitle(text)
                    if len(wins):
                        add_to_sub_row(wins[0]._hWnd, curr_row, text)
                    #add_sub_row(combo, event[1])
                    #mover_list[event[1]].win_list.append(gw.getWindowsWithTitle(combo)[0])
            elif event[0] == '-DEL2-':
                window['-ROW2-', event[1], event[2]].update(visible=False)
                #mover_list[event[1]].win_list_str.pop(event[2])
                mover_list[event[2]].win_list[event[1]][0] = None
                a = 0
            elif event[0] == 'AutoCB':
                if values[event]:
                    values=mover_list[curr_row].get_window_list()
                # window[("selector", row_counter)].update(values=mover_list[curr_row].raw_win_list_str)#, value=values['-COMBO-'])
                    #hide_all_sub()
                    cur_list = mover_list[curr_row].win_list[:]
                    keylist = window.key_dict.copy()
                    for c, win in enumerate(cur_list):
                      #  add_to_sub_row(win._hWnd if win else None, curr_row, win.title if win else "")
                        if win:
                            if win[0] and not win[2]:
                                add_sub_row(win[0].title, curr_row, found=True)
                            #else:
                                #add_sub_row("None", curr_row, found=False)

                                #window[win[1]].update(visible=False)
                            pass#add_sub_row("", curr_row, found=False)
                            #window[("-ROW2-", c, curr_row)].update(visible=False)
                           # del window.AllKeysDict[("-ROW2-", c, curr_row)]
                   # hide_all_sub(keylist=keylist, only_hide=True)


                        #if win:
                        #    add_sub_row(win.title, row_counter)
                else:
                    #window[("selector", row_counter)].update(values=[])#, value=values['-COMBO-'])
                    hide_all_sub(curr_row)

                update_sug(row_counter)
            elif event[0] == "Diagonal":
                m = mover_list[curr_row]
                val = values[event]
                if val:
                    m.direction_mode = m.DIAGONAL
                else:        
                    m.direction_mode = m.NON_DIAGONAL
                    
                if m.group_windows:
                    m.direction = m.get_random_direction()
                else:
                    for win in m.win_list:
                        win[3] = m.get_random_direction()
                
                # print(list_) 
            # elif event[0] == "Refresh":
            #     mover_list[event[1]].get_suggest_window_list()
            #     window[("selector", event[1])].update(values=mover_list[event[1]].suggest_win_list_str)#, value=values['-COMBO-'])
            elif event[0] == "slider":
                mover_list[event[1]].break_sleep = True
                # a = values[('slider', event[1])]
                # a2 = int(a*a*(1/1000))
                # window[("slider_out", event[1])].update(a2)
                # mover_list[event[1]].pixels_per_min = a2
                update_speed(event[1])
            elif event[0] == "-DESC-":
                text = window[event].get()
                if len(text) >= 3:
                    handle = find_handle_from_text(gw.getAllWindows(), text, window[("Parent", curr_row)])
                    if handle:
                        win = gw.Window(handle)
                        window[('-STATUS-',event[1], event[2])].update(f'Row2 {event[1]}, {event[2]} , window found: ' + win.title)
                        mover_list[curr_row].win_list[event[1]][0] = win
                    else:
                        window[('-STATUS-',event[1], event[2])].update(f'Row2 {event[1]}, {event[2]} , window NOT found')
                        mover_list[curr_row].win_list[event[1]][0] = None
                else:
                    window[('-STATUS-',event[1], event[2])].update(f'Row2 {event[1]}, {event[2]} , window NOT found')
                    mover_list[curr_row].win_list[event[1]][0] = None

            elif event[0] == "Group":
                mover_list[curr_row].group_windows = window[event].get()

            elif event[0] == "-dir_choose-":
                m = mover_list[curr_row]
                d = None
                if m.direction_mode == m.DIAGONAL:
                    d = {"a":Directions.BOTTOM_LEFT, "w":Directions.TOP_LEFT, "d":Directions.TOP_RIGHT, "s":Directions.BOTTOM_RIGHT }
                else:
                    d = {"a":Directions.LEFT, "w":Directions.TOP, "d":Directions.RIGHT, "s":Directions.BOTTOM }
                val = window[event].get()
                if val in d.keys():
                    m.win_list[event[1]][3] = d[val]
                window[event].update("")

                #values[event] = ""



    else:
        if event.startswith("-winp"):
            if window2 == None:
                open_window()
                
        if event.startswith("-SECTION"):
            n = event.split("|")[0]
            if "PTL" in event:
                pass
            #window[n].update(visible=not window[n].visible)
            #window[n+'|-BUTTON-'].update(window[n].metadata[0] if window[n].visible else window[n].metadata[1])

        if event == '-ADD_ITEM-':
            row_counter += 1
            row_number_view += 1
            print("Actual Row Number: ", row_counter)
            print("Displayed Row Number: ", row_number_view)
            # Allows you to add items to a layout
            # These items cannot be deleted, but can be made invisible
            window.extend_layout(window['-ROW_PANEL-'], [create_row(row_counter, row_number_view)])
            event, values = window.read(timeout=0.0001)
            
            init(row_counter)

            # window[("selector", row_counter)].bind("<Return>", "_Enter")
            # update_speed(row_counter)
            # update_sug(row_counter)


window.close()



#m = mover.mover()
#m.main_loop()

exit()

sg.theme('DarkAmber')   # Add a touch of color
# All the stuff inside your window.
layout = [  [sg.Text('Some text on Row 1')],
            [sg.Text('Enter something on Row 2'), sg.InputText()],
            [sg.Button('Ok'), sg.Button('Cancel')] ]

# Create the Window
window = sg.Window('Window Title', layout)
# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break
    print('You entered ', values[0])

window.close()




