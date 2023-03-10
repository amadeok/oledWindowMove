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
curr_file = ""
row_counter = 0
row_number_view = 1
curr_row = 0
window2 = None
mover_list = []
window = None
exit_program = False
def_file = os.getcwd() + "\\" + "default.json"
conf_path = os.getcwd() + "\\" + "conf"
settings_file = ""
prev_pos = None

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
    sg.user_settings_set_entry( " ".join(str(e) for e in ('-DESC-', entry_c, row_counter)), text)

    mover_list[row_counter].entry_counter+=1
    

    #event, values = window.read(timeout=0.0001)
    #window[key].bind("<Return>", "_Enter")
   # window[key].bind('<Control-z>', 'STRING TO APPEND')

def convert_speed(x):
    return  ((x**3)/12 * 0.000001)
    #def_speed*(def_speed/6)*(1/500)

def create_row(row_counter, row_number_view):
   # mover_list.append(mover.mover(row_counter, window))

    arrows=(sg.SYMBOL_DOWN, sg.SYMBOL_UP)
    collapsed=False
    def_speed = 60
    layout = [
            
            #[sg.Input('Input sec 1', key='-IN1-'), sg.Input(key='-IN11-')],
            [sg.Slider(range=(1, 4800), disable_number_display=True,  expand_x=True, enable_events=True, orientation="horizontal", key=("slider", row_counter), default_value=def_speed),
             sg.Text(f"{int(convert_speed(def_speed))} pixels per min", size=(12,1), key=("slider_out", row_counter)),
             sg.Input("x", size=(2,1), enable_events=True, key=('pixel_mult', row_counter)),

            sg.Checkbox('Diagonal Motion', enable_events=True, default=True, key=("Diagonal", row_counter), size=(13,1)),

             ],
             [  sg.Radio('Group all', f"RADIO{row_counter}", enable_events=True, default=True, key=("-group_all-", row_counter)),
                sg.Radio('Group overlapping', f"RADIO{row_counter}", enable_events=True, default=False, key=("-group_overlapping-", row_counter)),
                sg.Radio('Ignore overlapping', f"RADIO{row_counter}", enable_events=True, default=False, key=("-ignore_overlapping-", row_counter)),
                sg.Input(key=('-group-', row_counter), enable_events=False, visible=False),
                sg.Input(key=('-row2_list-', row_counter), enable_events=False, visible=False),

                ],

             [sg.Combo(['Refresh'], enable_events=True,expand_x=True, size=(75,1), key=("selector", row_counter)), 
                sg.Checkbox('Parent', enable_events=True, key=("Parent", row_counter), default=True),
                sg.Checkbox('Auto', enable_events=True, key=("AutoCB", row_counter), default=False),

                sg.Checkbox('Auto All', enable_events=True, key=("auto_all", row_counter), default=False),

               # sg.Checkbox('Group', enable_events=True, key=("Group", row_counter), default=True),


               ],
               #[ sg.Button("Show profile")],
            [sg.Column([], k=('-ROW_PANEL2-', row_counter))],

            [sg.Button('Pick top left', key=("-PTL", row_counter),  button_color='yellow on green'),
             sg.Button('Pick bottom right',key=("-PBR", row_counter), button_color='yellow on green'),
             sg.Button('Start',key=("start_stop", row_counter), button_color='yellow on green'),
            sg.Button('which',key=("which", row_counter), button_color='yellow on green'),
            sg.Button("Prev", border_width=0, button_color=(sg.theme_text_color(), sg.theme_background_color()), key=('-winp-', row_counter)),

           # sg.Text("Choose a file: ", enable_events=True), sg.FileBrowse(key="-IN-", change_submits=True, enable_events=True),

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

def open_window(id):
    m = mover_list[id]
    layout = [[sg.Text("New Window", key="new"), sg.Button("Get Size", enable_events=True)   ]]
    window = sg.Window("OledPreviewWin", layout, resizable=True, size=(m.active_area.width, 
                                                                       m.active_area.height))
    x = m.active_area.topleft[0]
    y = m.active_area.topleft[1]
    moved = False
    while True:
        event, values = window.read(timeout=0.5)
        if not moved: 
            window.move(x, y) 
        moved = True

        if event == "Get Size":
            loc = window.current_location()
            size = window.current_size_accurate()
            #m.update_active_area()
            m.active_area = pygame.Rect(loc[0], loc[1], size[0], size[1])
            m.top_left_coor = m.active_area.topleft
            m.bottom_right_coor = m.active_area.bottomright
            update_sug(id)

        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        
    window.close()

def update_speed(id):
    event, values = window.read(timeout=0.0001)
    
    a = values[('slider', id)]
    a2 = int(convert_speed(a)) # int(a*(a/6)*(1/500))
    if a2 == 0: a2 = 1
    window[("slider_out", id)].update(f"{a2} pixels per min ")
    mover_list[id].pixels_per_min = a2



def update_sug(id):
    mover_list[id].get_suggest_window_list()
    window[("selector", id)].update(values=mover_list[id].suggest_win_list_str)#, value=values['-COMBO-'])

def init(id):
    window[("selector", id)].bind("<Return>", "_Enter")
    window[("selector", id)].bind("<FocusIn>", "FocusIn")

    for m in mover_list:
        if m:
            val = window["bounce_input"].get()
            if val.isdigit():
                m.bounce_pixel = int(val)
            #window["bounce_input"].update(val)

            val = window["ov_perc"].get()
            if val.isdigit():
                m.overlap_perc = int(val)
            


    update_speed(id)
    update_sug(id)


def add_to_sub_row(handle, row, text):
    m = mover_list[row]
    try:
        mover.move_win(handle, 0, 0)
    except:
        handle = None
    w = win_(gw.Window(handle) if handle else None, ("-ROW2-", len(m.win_list), m.id), 
             True, m.direction if m.group_windows == GROUP_ALL else m.get_random_direction())
    
    m.win_list.append(w)
    add_sub_row(text, row, found=w.win.title if handle else False)



def hide_all_sub(row, keylist=None, only_hide=False):
    for c, elem in enumerate(mover_list[row].win_list):
        if elem and not elem.added_manually:#elem[2]:
            window[elem.key].update(visible=False)
            mover_list[row].win_list[c].win = None
            print("none" if not elem.win else elem.win.title, " ", elem.key)
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

def add_instance(dummy):
    global row_counter; global row_number_view


    if not dummy:
        mover_list.append(mover.mover(row_counter, window))

        window.extend_layout(window['-ROW_PANEL-'], [create_row(row_counter, row_number_view)])
        event, values = window.read(timeout=0.0001)
        
        init(row_counter)
    else:
        mover_list.append(None)

    row_counter += 1
    row_number_view += 1
    print("Actual Row Number: ", row_counter, " ", dummy)
    print("Displayed Row Number: ", row_number_view, " " , dummy)

def update_auto_all(id, disable):
    mover_list[id].auto_all = disable
    for k in window.key_dict:
        if  last_elem(k) == id:
            if k[0] == "-DESC-" or  k[0] == "selector" or k[0] == "AutoCB":
                window[k].update(disabled=disable)



def update_group_mode():
    event, values = window.read(timeout=0.0001)

    for i, m in enumerate(mover_list):
        if m:
            val = window[("-group-", i)].get()
            if len(val):
                window[(val, i)].update(True)
                m.group_windows = group_dict[val]
            
            diag = sg.user_settings_get_entry("Diagonal " + str(i))
            if diag != None:
                m.direction_mode = int(diag)
            m.direction = m.get_random_direction()

            val = sg.user_settings_get_entry("-PTL " + str(i))
            if val:
                m.top_left_coor = coor(val[0], val[1])

            val = sg.user_settings_get_entry("-PBR " + str(i))
            if val:
                m.bottom_right_coor = coor(val[0], val[1])
                m.update_active_area()

            val = sg.user_settings_get_entry('auto_all ' + str(i))
            if val != None:
                m.auto_all = val
            
            update_auto_all(i, val if val else False)            

            init(i)

def last_elem(l):
    return l[len(l)-1]


def find_instances_nb():
    settings = sg.user_settings()
    dummy_l = [True for x in range(100)]
    max_inst_nb = 0

    entry_list = [[] for x in range(100)]

    for k, value in settings.items():
        k_split = k.split(" ")
        if len(k_split) > 1:
            instance_id = int(last_elem(k_split))
            if instance_id > max_inst_nb:
                max_inst_nb = instance_id
            dummy_l[instance_id] = False

            if len(k_split) == 3:
                entry_list[instance_id].append((k_split[0], value))
        

    i = 0
    while i <= max_inst_nb:
        add_instance(dummy_l[i])
        i+=1

    for i, elem in enumerate(entry_list):
        if i >= len(mover_list):
            break

        parent = sg.user_settings_get_entry("Parent " + str(i))
        if mover_list[i]:
            mover_list[i].direction_mode = sg.user_settings_get_entry("Diagonal " + str(i))
            mover_list[i].group_windows = sg.user_settings_get_entry("-group- " + str(i))

        for entry in elem:

            handle = find_handle_from_text(gw.getAllWindows(), entry[1], parent)

            add_to_sub_row(handle, i, entry[1])
    

def read_settings():

    find_instances_nb()
    k = None
    settings = sg.user_settings()
    for k, value in settings.items():
        k_split = k.split(" ")
        if len(k_split) > 1:
            k_ = ()
            for a in k_split:
                k_ += ((int(a) if a.isdigit() else a),)
        else:
            k_ = k
        #if len(k_) == 2:

        if type(value) == tuple:
            window[k_].update(coor(value[0], value[1]))
        else:
            window[k_].update(value)

    update_group_mode()

def read_save_file(file_path):
    cur = sg.user_settings()
    if file_path == "":
        file_path = def_file
    if not os.path.isfile(file_path):
        with open(file_path, "w+") as f:
            f.write('{"-group- 1": "-group_overlapping-", "bounce_input": "5", "ov_perc": "50", "pixel_mult 1": 1}')
            
    # if not os.path.isfile(settings_file):
    #     with open(settings_file, "w+") as f:
    #         f.write('{"-group- 1": "-group_overlapping-", "bounce_input": "5", "ov_perc": "50", "pixel_mult 1": 1}')

    settings = sg.user_settings_load(file_path)
    #a = sg.user_settings_get_entry("-PTL 0")
    s = os.path.basename(file_path)
    window["-save_name-"].update(s)
    read_settings()

    bounce_input = window["bounce_input"].get()
    ov_perc = window["ov_perc"].get()

    for m in mover_list:
        if m:
            if bounce_input.isdigit():
                m.bounce_pixel = int(bounce_input)
            if ov_perc.isdigit():
                m.overlap_perc = int(ov_perc)
    

def get_layout():
    return   [  [sg.Text('Add and "Delete" Rows From a Window', font='15')],
                [sg.Column([], k='-ROW_PANEL-')], #[create_row(0, 1)
                [sg.Button("Exit", enable_events=True, key='-EXIT-', tooltip='Exit Application'),
                #sg.Text("Refresh", enable_events=True, key='-REFRESH-', tooltip='Exit Application'),
                sg.Button('New instance', enable_events=True, k='-ADD_ITEM-', tooltip='Add Another Item'),
                sg.Input(key='_FILEBROWSE_', enable_events=True, visible=False),
                sg.Text("Choose a file: ", key='-save_name-', enable_events=True),
                sg.FileBrowse("Load settings", target='_FILEBROWSE_'),
                sg.Input(key='save_settings', enable_events=True, visible=False),
                sg.FileSaveAs("New settings", target='save_settings', 
                              enable_events=True,file_types=(('JSON', '.json'),),),
                sg.Text('Bounce:', enable_events=False, k='-bounce-'),
                sg.Input(key='bounce_input', size=(2,1),  enable_events=True, visible=True),
                sg.Text('Overlap %:', enable_events=False, k='-bounce-'),
                sg.Input(key='ov_perc', size=(2,1), enable_events=True, visible=True),


                ],
                ]

exists = os.path.isfile( conf_path)

if exists:
    with open(conf_path, "r") as f:
        settings_file = f.read()
        if not os.path.isfile(settings_file):
            settings_file = def_file
        

else:
    with open(conf_path, "w+") as f:
        f.write(def_file)
        settings_file = def_file


while True:
    mover_list.clear()
    row_counter = 0
    row_number_view = 1

    window = sg.Window('Oled Window Mover', 
    get_layout(),  use_default_focus=False, font='15', finalize=True)

    if prev_pos:
        h = gw.getWindowsWithTitle('Oled Window Mover')[0]
        win32gui.MoveWindow(h._hWnd, prev_pos[0], prev_pos[1], h.width, h.height, True)
        #win32gui.LineTo(h._hWnd, 0, 1000)
    read_save_file(settings_file)

    while True:

        event, values = window.read()
        #print(event)

        if event == sg.WIN_CLOSED or event == '-EXIT-':
            exit_program = True
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
                    window['-ROW-', event[1]].update(visible=False)

                    settings = sg.user_settings()
                    d =  settings.copy()
                    for k, value in d.items():
                        k_s = k.split(" ")
                        
                        if len(k_s) > 1:
                            if int(last_elem(k_s)) == curr_row:
                                sg.user_settings_delete_entry(k)               
                        else:
                            sg.user_settings_delete_entry(k)  

                elif event[0] == '-BUTTON-':
                    window[('-SECTION-', event[1])].update(visible=not window[('-SECTION-', event[1])].visible)
                    
                if "PTL" in event[0]:
                    var = None
                    with Listener(on_click=on_click_tlc) as listener:
                        listener.join()
                        var = mover_list[event[1]].top_left_coor
                        window[event].update(var)
                    update_sug(event[1])
                    sg.user_settings_set_entry( " ".join(str(e) for e in event), (var.x, var.y))

                elif "PBR" in event[0]:
                    var = None
                    with Listener(on_click=on_click_brc) as listener:
                        listener.join()
                        var = mover_list[event[1]].bottom_right_coor
                        window[event].update(var)
                    update_sug(event[1])
                    sg.user_settings_set_entry( " ".join(str(e) for e in event), (var.x, var.y))

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
                # window[('-ignore_overlapping-', 0)].update(True)

                elif "selector" in event[0]:
                    text = window[event].get()  # use the combo key
                    if text == "Refresh":
                        values=mover_list[curr_row].get_suggest_window_list()
                        window[event].update(values=mover_list[curr_row].suggest_win_list_str)#, value=values['-COMBO-'])
                    else:
                        wins = gw.getWindowsWithTitle(text)
                        if len(wins):
                            add_to_sub_row(wins[0]._hWnd, curr_row, text)

                elif event[0] == '-DEL2-':
                    window['-ROW2-', event[1], event[2]].update(visible=False)
                    #mover_list[event[1]].win_list_str.pop(event[2])
                    mover_list[event[2]].win_list[event[1]].win = None
                    mover_list[event[2]].win_list[event[1]].marked_for_del = True
                    sg.user_settings_delete_entry(f"-DESC- {event[1]} {event[2]}")
                    
                elif event[0] == 'AutoCB':
                    if values[event]:
                        values=mover_list[curr_row].get_window_list()

                        cur_list = mover_list[curr_row].win_list[:]
                        #keylist = window.key_dict.copy()
                        for c, win in enumerate(cur_list):
                            if win:
                                if win.win and not win.added_manually:
                                    add_sub_row(win.win.title, curr_row, found=True)

                    else:
                        hide_all_sub(curr_row)

                    update_sug(curr_row)

                elif event[0] == 'auto_all':
                    val = window[event].get()
                    update_auto_all(event[1], val)
                    sg.user_settings_set_entry( " ".join(str(e) for e in event), val)

                elif event[0] == "Diagonal":
                    m = mover_list[curr_row]
                    val = values[event]
                    if val:
                        m.direction_mode = m.DIAGONAL
                    else:        
                        m.direction_mode = m.NON_DIAGONAL
                    
                    sg.user_settings_set_entry( " ".join(str(e) for e in event), m.direction_mode)

                    if m.group_windows == GROUP_ALL:
                        m.direction = m.get_random_direction()
                    else:
                        win_list = m.all_win_list if m.auto_all else m.win_list
                        for win in win_list:
                            if m.group_windows == GROUP_OVERLAPPING:
                                if len(win.overlapping_wins) and win == win.overlapping_wins[0]:
                                    win.direction = m.get_random_direction()
                            else:
                                win.direction = m.get_random_direction()

                elif event[0] == "slider":
                    mover_list[event[1]].break_sleep = True
                    update_speed(event[1])
                    sg.user_settings_set_entry( " ".join(str(e) for e in ("slider", event[1])), values[('slider', event[1])])


                elif event[0] == "Parent":
                    sg.user_settings_set_entry( " ".join(str(e) for e in event), window[event].get())

                elif event[0] == "pixel_mult":
                    i = window[event].get()
                    if i.isdigit():
                        mover_list[event[1]].pix_mult =  int(i)
                        sg.user_settings_set_entry( " ".join(str(e) for e in event), int(i))


                elif event[0] == "-DESC-":
                    m = mover_list[curr_row]

                    text = window[event].get()
                    if len(text) >= 3:
                        handle = find_handle_from_text(gw.getAllWindows(), text, window[("Parent", curr_row)])
                        try:
                            mover.move_win(handle, 0, 0)
                        except:
                            handle = None
                        win = gw.Window(handle) if handle else None

                        mover.win_up(window, m, event[1], event[2], win, text)                    
                    else:
                        mover.win_up(window, m, event[1], event[2], None, text)                    

                elif event[0] == "-group_all-":
                    mover_list[curr_row].group_windows = GROUP_ALL
                    sg.user_settings_set_entry(  "-group- " + str(curr_row), "-group_all-")

                elif event[0] == '-group_overlapping-':
                    mover_list[curr_row].group_windows = GROUP_OVERLAPPING
                    sg.user_settings_set_entry(   "-group- " + str(curr_row),  '-group_overlapping-')
                
                elif event[0] == '-ignore_overlapping-':
                    mover_list[curr_row].group_windows = GROUP_NONE
                    sg.user_settings_set_entry(   "-group- " + str(curr_row), '-ignore_overlapping-')
                    for w in mover_list[curr_row].win_list:
                        w.overlapping_wins = [w]
                    

                elif event[0] == "-dir_choose-":
                    m = mover_list[curr_row]
                    d = None
                    if m.direction_mode == m.DIAGONAL:
                        d = {"a":Directions.BOTTOM_LEFT, "w":Directions.TOP_LEFT, "d":Directions.TOP_RIGHT, "s":Directions.BOTTOM_RIGHT }
                    else:
                        d = {"a":Directions.LEFT, "w":Directions.TOP, "d":Directions.RIGHT, "s":Directions.BOTTOM }
                    val = window[event].get()
                    if val in d.keys():
                        m.win_list[event[1]].direction = d[val]
                    elif val == "z":
                        win32gui.MoveWindow(m.win_list[event[1]].win._hWnd, 0, 0, m.win_list[event[1]].win.width , m.win_list[event[1]].win.height, True)

                    window[event].update("")
                    
                elif event[0] == "-winp-":
                    if window2 == None:
                        open_window(event[1])
                        #values[event] = ""



        else:                  
            if event.startswith("-SECTION"):
                n = event.split("|")[0]
                if "PTL" in event:
                    pass
                #window[n].update(visible=not window[n].visible)
                #window[n+'|-BUTTON-'].update(window[n].metadata[0] if window[n].visible else window[n].metadata[1])

            elif event == '-ADD_ITEM-':
                add_instance(False)

            elif event == "_FILEBROWSE_":
                
                settings_file = window[event].get()
                if os.path.isfile(settings_file):
                    with open(conf_path, "w+") as f:
                        f.write(settings_file)
                    #read_save_file(curr_file)
                    prev_pos =  window.CurrentLocation()
                    break
                else:
                    print("file " , settings_file, " doesn't exist")

            elif event == "save_settings":

                settings_file = window[event].get()
                sg.user_settings_filename(settings_file)
 

                with open(conf_path, "w+") as f:
                    f.write(settings_file)
                #read_save_file(curr_file)
                prev_pos =  window.CurrentLocation()
                break

            elif event == "bounce_input":
                for m in mover_list:
                    if m:
                        val = window[event].get()
                        if val.isdigit():
                            m.bounce_pixel = int(val)
                            sg.user_settings_set_entry(event, val)
                        
            elif event == "ov_perc":
                for m in mover_list:
                    if m:
                        val = window[event].get()
                        if val.isdigit():
                            m.overlap_perc = int(val)
                            sg.user_settings_set_entry(event, val)


    window.close()
    for m  in mover_list:
        if m:
            m.stop = True
            
    if exit_program:
        break




