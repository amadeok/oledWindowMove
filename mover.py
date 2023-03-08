import os, threading, random
import msvcrt, ctypes, pyautogui 
import win32pipe, win32file, pywintypes, win32api, win32con, win32gui
import pygetwindow as gw
from time import sleep
from mlogging import *
import PySimpleGUI as sg

import getviswin as ge

from enums import *

import pygame, numpy as np

from collections import namedtuple
Rectangle = namedtuple('Rectangle', 'xmin ymin xmax ymax')

www  = gw.getActiveWindow()
sleep(0)
#www.moveTo(0, 0)
#win32gui.MoveWindow(67474, 0, 0, 100, 100, True)

def move_win(hwnd, x_change, y_change):
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0] # 
    y = rect[1] # 
    w = rect[2] - x
    h = rect[3] - y
    win32gui.MoveWindow(hwnd, x+x_change, y+y_change, w, h, True)


def area(a, b):  # returns None if rectangles don't intersect
    dx = min(a.xmax, b.xmax) - max(a.xmin, b.xmin)
    dy = min(a.ymax, b.ymax) - max(a.ymin, b.ymin)
    if (dx>=0) and (dy>=0):
        return dx*dy
    else:
        return 0
    
def get_overlapping_area(win1, win2):
    ra = Rectangle(win1.topleft[0],  win1.topleft[1], win1.bottomright[0] , win1.bottomright[1])
    rb = Rectangle(win2.topleft[0],  win2.topleft[1], win2.bottomright[0] , win2.bottomright[1])
    # rr1 = pygame.Rect(r1.topleft.x, r1.topleft.y, r1.width, r1.height)
    # rr2 = pygame.Rect(r2.topleft.x, r2.topleft.y, r2.width, r2.height)
    # print(rr1.colliderect(rr2))
    return area(ra, rb)

def win_up(w, m, entry_c, cur_row, win, text):
    w[('-STATUS-',entry_c, cur_row)].update(f'Row2 {entry_c}, {cur_row} , window found: ' 
                                                + win.title if win else "NOT found")
    m.win_list[entry_c].win = win if win else None
    sg.user_settings_set_entry(f"-DESC- {entry_c} {cur_row}", text)
    

ret = ge.get_visible_windows() # the first elements are the ones more on top
for elem in ret:
    print((elem["title"] +  "\n"))



class mover():
    NON_DIAGONAL = 0
    DIAGONAL = 1
    def __init__(self, id, ui) -> None:
        self.whitelist  = []
       # self.mode = GROUP_TOGHETER
        self.win_list = []#[gw.Window(elem["hwnd"]) for elem in ret]
        self.scree_res = pyautogui.size()
        #sleep(1)
        self.group_windows = True
        self.direction_mode = self.DIAGONAL

        self.generated_group_box = self.get_group_box(self.win_list)
        self.group_list = []

        self.get_random_direction()
        print(self.direction)

        self.new_direction_debounce = 0

        self.x_move = 1
        self.y_move = 0
        self.pix_mult = 1
        print(self.generated_group_box)
        
        self.delay = 0.05
        self.stop = False
        self.top_left_coor = coor(0, 0)
        self.bottom_right_coor = coor(self.scree_res.width, self.scree_res.height)
        self.entry_counter = 0
        #self.raw_win_list = []
        #self.raw_win_list_str = []
        self.suggest_win_list_str = []

        self.loop_running = False
        self.update_active_area()
        self.break_sleep= False
        self.pixels_per_min = 1
        self.id = id
        self.ui_ref = ui
        self.overlap_perc = 1
        self.bounce_pixel = 5

    def get_random_direction(self):
        dir = None
        if self.direction_mode == self.DIAGONAL:
            dir = self.direction = directions_list[ random.randint(4,7)]
        else:
            dir = self.direction = directions_list[random.randint(0, 3)] #Directions.LEFT
        return dir

    def get_active_area_area(self):
        return self.active_area.width*self.active_area.height
    def update_active_area(self):
        self.active_area = pygame.Rect(self.top_left_coor.x, self.top_left_coor.y,
                                        self.bottom_right_coor.x - self.top_left_coor.x, self.bottom_right_coor.y - self.top_left_coor.y)

    def get_window_list(self):

        ret = ge.get_visible_windows()
            
        #self.win_list = []
        #self.raw_win_list_str = []

        for win in ret:
            #try:
            winn = gw.Window(win['hwnd'])
            if win["title"] != "":
                o_a = get_overlapping_area(self.active_area, winn)
                if o_a and o_a > winn.area//2:
                    w = win_(winn,  ("-ROW2-", len(self.win_list), self.id), False, 
                                         self.direction if self.group_windows else self.get_random_direction())
                    self.win_list.append(w)
                    #self.raw_win_list_str.append(win["title"])
                #else:
                #    self.win_list.append([None, ("-ROW2-", len(self.win_list), self.id)])

            #except Exception as e:
                #print(e)

        return self.win_list
    
    
    def get_suggest_window_list(self):
        ret = gw.getAllWindows()
        self.suggest_win_list_str = []

        for win in ret:
            if win.title != "":
                o_a = get_overlapping_area(self.active_area, win)
                if o_a and o_a > win.area//2:
                    self.suggest_win_list_str.append(win.title)

        return self.suggest_win_list_str
    
    # def get_random_dir(self):
    #     ds = [attr for attr in dir(Directions) if not callable(getattr(Directions, attr)) and not attr.startswith("__")]
    #     return getattr(Directions, random.choice(ds))

    def move_windows(self, x, y, win_list):
        l = self.win_list if self.group_windows == GROUP_ALL else win_list
        for elem in l:
            win = elem.win if type(elem) == win_ else elem
            if not win or not win32gui.IsWindow(win._hWnd): 
                continue
            if win.width != 0:
                move_win(win._hWnd, x, y) #win.move(x, y)

    def start_loop(self):
        self.t = threading.Thread(target=self.main_loop, args=())
        self.t.start()

    def is_box_out_of_area(self, win):
        rect = win.get_box()
        side_delta = 0
        top_delta = 0

        d = rect.bottomleft.x - self.active_area.bottomleft[0]
        if d <= 0:
            side_delta = d
            #return Collisions.LEFT_SIDE
        elif rect.bottomright.x >= self.active_area.bottomright[0]:  #self.scree_res.width :
            side_delta = abs(self.active_area.bottomright[0] - rect.bottomright.x)
            #return Collisions.RIGHT_SIDE
            
        d = rect.topright.y - self.active_area.topright[1]
        if d <= 0:
            top_delta = d
            #return Collisions.TOP_SIDE
        elif rect.bottomright.y >= self.active_area.bottomright[1]:
            top_delta = abs(self.active_area.bottomright[1] - rect.bottomright.y)
            #return Collisions.BOTTOM_SIDE
        #print(side_delta, top_delta)

        if abs(side_delta) > abs(top_delta):
            if side_delta > 0:
                self.move_windows(-1, 0, win.get_wins())
            elif side_delta < 0:
                self.move_windows(1, 0, win.get_wins())

            if side_delta > 0:
                return Collisions.RIGHT_SIDE
            elif side_delta < 0:
                return Collisions.LEFT_SIDE
                
        else:
            if top_delta > 0:
                self.move_windows(0, -1,  win.get_wins())
            elif top_delta < 0:
                self.move_windows(0, 1,  win.get_wins())
                
            if top_delta > 0:
                return Collisions.BOTTOM_SIDE
            elif top_delta < 0:
                return Collisions.TOP_SIDE
            
    def find_rect_collision(self, rect1_, rect2_):

        rect1 = rect1_.win
        rect2 = rect2_.win
        if not get_overlapping_area(rect1, rect2):
            return [None]

        d1 = rect1.topleft.y - rect2.bottomleft.y
        d2 = rect1.bottomleft.y - rect2.topleft.y
        top_or_bottom = None
        if abs(d1) < abs(d2):
           # print( "top side", rect1.title)
            top_or_bottom = (Collisions.TOP_SIDE, d1)
        else:
           # print( "bottom side", rect1.title)
            top_or_bottom = (Collisions.BOTTOM_SIDE, d2)

        d3 = rect1.topleft.x - rect2.topright.x
        d4 = rect1.topright.x - rect2.topleft.x 
        left_or_right = None
        if abs(d3) < abs(d4):
            #print( "left side", rect1.title)
            left_or_right = (Collisions.LEFT_SIDE, d3)
        else:
           # print( "right side", rect1.title)
            left_or_right = (Collisions.RIGHT_SIDE, d4)
        
        if abs(top_or_bottom[1]) <  abs(left_or_right[1]):
            print( top_or_bottom[0].name, " ", rect1.title)

            if top_or_bottom[0] == Collisions.TOP_SIDE:
                move_win(rect1._hWnd, 0, 1)# rect1.move(0, 1)
            else:
                move_win(rect1._hWnd, 0, -1) #rect1.move(0, -1)

            return top_or_bottom
        
        else:
            print( left_or_right[0].name, " ", rect1.title)
            
            if left_or_right[0] == Collisions.LEFT_SIDE:
                move_win(rect1._hWnd, 1, 0)#rect1.move(1, 0)
            else:
                move_win(rect1._hWnd, -1, 0)#rect1.move(-1, 0)

            return left_or_right


    


    def determine_direction(self, collision, cur_direction, title):

        new_direction = None
        if self.direction_mode == self.NON_DIAGONAL:

            if collision == Collisions.LEFT_SIDE:
                new_direction = Directions.TOP

            elif collision == Collisions.RIGHT_SIDE:
                new_direction = Directions.BOTTOM

            elif collision == Collisions.TOP_SIDE:
                new_direction = Directions.RIGHT

            elif collision == Collisions.BOTTOM_SIDE:
                new_direction = Directions.LEFT

        else:
            if cur_direction == Directions.TOP_RIGHT:
                if collision == Collisions.TOP_SIDE:
                    new_direction = Directions.BOTTOM_RIGHT
                else:
                    new_direction = Directions.TOP_LEFT

            elif cur_direction == Directions.BOTTOM_RIGHT:
                if collision == Collisions.RIGHT_SIDE: 
                    new_direction = Directions.BOTTOM_LEFT
                else:
                    new_direction = Directions.TOP_RIGHT


            elif cur_direction == Directions.BOTTOM_LEFT:
                if collision == Collisions.BOTTOM_SIDE:
                    new_direction = Directions.TOP_LEFT
                else:
                    new_direction = Directions.BOTTOM_RIGHT

            
            elif cur_direction == Directions.TOP_LEFT:
                if collision == Collisions.LEFT_SIDE:
                    new_direction = Directions.TOP_RIGHT
                else:                    
                    new_direction = Directions.BOTTOM_LEFT
        
        self.new_direction_debounce = 10
        print(" new direction: ",  new_direction.name, " | ", title)
        return new_direction

    def get_group_box(self, win_list):
        topleft = coor(self.scree_res.width, self.scree_res.height)
        bottomright = coor(0, 0)

        for elem in win_list:
            win = elem.win
            if win == None: continue
            try:
                if win.topleft.x < topleft.x:
                    topleft.x = win.topleft.x
                if win.topleft.y < topleft.y:
                    topleft.y = win.topleft.y

                if win.bottomright.x > bottomright.x:
                    bottomright.x = win.bottomright.x
                if win.bottomright.y > bottomright.y:
                    bottomright.y = win.bottomright.y
            except Exception as e:
                print(e)

        topright = coor(bottomright.x, topleft.y)
        bottomleft = coor(topleft.x, bottomright.y)

        r = rect(topleft, bottomright, topright, bottomleft)
        #d = win_list[0].direction if 
        g = win_group(win_list, r)
        return g #{"topleft":topleft, "bottomright":bottomright, "topright":topright, "bottomleft":bottomleft}

    def custom_sleep(self, total_sleep_time):
        rem = total_sleep_time
        if total_sleep_time <= 0.1: 
            sleep(total_sleep_time)
        else:
            while rem > 0:
                sleep(0.1)
                rem-=0.1
                if self.break_sleep:
                    self.break_sleep = False
                    return True
                if rem <= 0 or self.stop:
                    break
        return False

    def find_overlapping_windows(self, w1):
        print("\n #", w1.win.title if w1.win else "None")
        smaller = None; bigger = None
        w1.overlapping_wins.clear()

        for w2 in self.win_list:

            if not w1.win or not w2.win:
                continue
            if w1.win._hWnd == w2.win._hWnd:
                w1.overlapping_wins.append((w2, 101))
                continue
            
            if w2.win.area < w1.win.area:
                smaller = w2; bigger = w1
            else: 
                smaller = w1; bigger = w2

            a = get_overlapping_area(w1.win, w2.win)
            perc = (a / (smaller.win.area ) )*100

            if perc > self.overlap_perc:
                w1.overlapping_wins.append((w2, perc))

        w1.overlapping_wins.sort(key=lambda x: x[0].win.area, reverse=True)
        

        
        for ww in w1.overlapping_wins:
            print("--- ",  ww[0].win.area, " ", ww[1], " ", ww, )
            
    def get_ove_groups(self):
        main_list = []
        # for w in self.win_list:
        #     tmp_l = []
        #     for ww in w.overlapping_wins:
        #         tmp_l.append(ww[0])

        #     # for ll in main_list:
        #     #     for tl in tmp_l:
        #     #         if tl in ll:

            
        #     if w == tmp_l[0]:
        #         main_list.append(tmp_l[:])
        #     else:
        #         a = 0 
        def contains_list(l1, l2):
            for elem in list1:
                if elem in list2:
                    return True
        main_list2 = []
        for i1, list1 in enumerate(self.win_list.overlapping_wins[0]):
            for i2, list2 in enumerate(self.win_list.overlapping_wins[0]):
                if i1 != i2:
                    if contains_list(list1, list2):
                        main_list.append(list1 + list2)

        #l = [elem.overlapping_wins for elem in self.win_list]
        #l1 = [elem[0] for elem in l]
        #l2 =  list(set(l))
        #l3 = [elem[0] for elem in l2]
        self.group_list = [self.get_group_box(elem) for elem in main_list]
        #for g in self.group_list:
        #    g.direction = g.win_list[0].direction if len(g.win_list) else self.get_random_direction()
    @staticmethod
    def win_minimized(h):
        if h.isMinimized:
            return True
        if abs(h.centerx) > 30*1000 or abs(h.centery) > 30*1000:
            return True
        return False

    def main_loop(self):
        self.loop_running = True
        print("Starting main loop id ", self.id)

        
        while 1:
            per_sec = self.pixels_per_min / 60
            if (self.custom_sleep(1/per_sec)):
                continue

            if self.group_windows == GROUP_ALL:
                self.generated_group_box = self.get_group_box(self.win_list)
                collision = self.is_box_out_of_area(self.generated_group_box)
                #print(collision)
                if self.new_direction_debounce:
                    self.new_direction_debounce -=1
                elif collision:
                    self.direction =  self.determine_direction(collision, self.direction, "group")
                    
                self.move_windows(self.direction.x *self.pix_mult, self.direction.y *self.pix_mult, self.win_list)
                
            elif self.group_windows == GROUP_OVERLAPPING:

                for i, win in enumerate(self.win_list):

                    if win.win and not win32gui.IsWindow(win.win._hWnd) or win.marked_for_del: 
                        win.win = None
                        win_up(self.ui_ref, self,  i, self.id, win.win,  "None")
                        win.marked_for_del = False

                    if not win.win or self.win_minimized(win.win) :
                        continue

                    col = self.is_box_out_of_area(win)
                    if col:
                        win.direction = self.determine_direction(col, win.direction, win.win.title)
                        win.last_collision = 2
                        if self.group_windows == GROUP_OVERLAPPING:
                            pass                 

                for win1 in self.win_list:
                    for win2 in self.win_list:
                        if win1.last_collision or win2.last_collision or not win1.win or not win2.win:
                            continue
                        elif win1.win._hWnd == win2.win._hWnd or self.win_minimized(win1.win) or self.win_minimized(win2.win):
                            continue
                        #if len(self.win_list) >= 2 and 0:
                        #self.find_overlapping_windows()

                        col = self.find_rect_collision(win1, win2)
                        #area = get_overlapping_area(self.win_list[1][0], self.win_list[2][0])

                        if col[0]:
                            win1.last_collision = 2
                            win2.last_collision = 2
                            win1.direction = self.determine_direction(col[0], win1.direction, win1.win.title)
                            v = pygame.math.Vector2(win1.win.center.x - win2.win.center.x, win1.win.center.y - win2.win.center.y)
                            
                            vm = v.normalize() if v.x != 0 and v.y != 0 else v
                            move_win(win1.win._hWnd, int(round(vm.x))*self.bounce_pixel*self.pix_mult,
                                      int(round(vm.y))*self.bounce_pixel*self.pix_mult)
                            move_win(win2.win._hWnd, -int(round(vm.x))*self.bounce_pixel*self.pix_mult,
                                      -int(round(vm.y))*self.bounce_pixel*self.pix_mult)

                            #if abs(col[1]) < 10:
                            win2.direction = get_contrary(win1.direction)
                        
                for win in self.win_list:
                    #win.last_collision = False
                    if win.last_collision:
                        win.last_collision-=1

                

                for win in reversed(self.win_list):
                    if win.win and win.win.width != 0:
                        move_win(win.win._hWnd, win.direction.x * self.pix_mult, win.direction.y* self.pix_mult)  # win[0].move(win[3].x, win[3].y)


            elif self.group_windows == GROUP_OVERLAPPING:
                print("\n :")
                for w in self.win_list:
                    self.find_overlapping_windows(w)

                self.get_ove_groups()

                for group in self.group_list:
                    #if not win.win: continue
                    if group.last_collision or group.last_collision:
                        continue
                    col = self.is_box_out_of_area(group)
                    if col:
                        group.win_list[0].direction = self.determine_direction(col, group.win_list[0].direction, group.win_list[0].win.title)
                        group.last_collision = 2    
            
                for group in self.group_list:
                    self.move_windows(group.win_list[0].direction.x *self.pix_mult, group.win_list[0].direction.y *self.pix_mult, group.win_list)

                

            # for win in self.win_list:
            #     if win.width != 0:
            #         win.move(self.x_move, self.y_move)
            # total_sleep_time = self.pixels_per_min / 60


            #print("hello")
            if self.stop:
                print("Stopping id ", self.id)
                self.stop = False
                self.loop_running = False
                break