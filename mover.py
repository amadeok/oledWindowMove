import os, threading, random
import msvcrt, ctypes, pyautogui 
import win32pipe, win32file, pywintypes, win32api, win32con, win32gui
import pygetwindow as gw
from time import sleep
from mlogging import *

import getviswin as ge

from enums import *

import pygame

from collections import namedtuple
Rectangle = namedtuple('Rectangle', 'xmin ymin xmax ymax')


def area(a, b):  # returns None if rectangles don't intersect
    dx = min(a.xmax, b.xmax) - max(a.xmin, b.xmin)
    dy = min(a.ymax, b.ymax) - max(a.ymin, b.ymin)
    if (dx>=0) and (dy>=0):
        return dx*dy
    
def get_overlapping_area(win1, win2):
    ra = Rectangle(win1.topleft[0],  win1.topleft[1], win1.bottomright[0] , win1.bottomright[1])
    rb = Rectangle(win2.topleft[0],  win2.topleft[1], win2.bottomright[0] , win2.bottomright[1])
    # rr1 = pygame.Rect(r1.topleft.x, r1.topleft.y, r1.width, r1.height)
    # rr2 = pygame.Rect(r2.topleft.x, r2.topleft.y, r2.width, r2.height)
    # print(rr1.colliderect(rr2))
    return area(ra, rb)


ret = ge.get_visible_windows() # the first elements are the ones more on top
for elem in ret:
    print((elem["title"] +  "\n"))

class mover():
    NON_DIAGONAL = 0
    DIAGONAL = 1
    def __init__(self, id, ui) -> None:
        self.whitelist  = []
        self.mode = GROUP_TOGHETER
        self.win_list = []#[gw.Window(elem["hwnd"]) for elem in ret]
        self.scree_res = pyautogui.size()
        #sleep(1)
        self.generated_group_box = self.get_group_box()
        self.direction_mode = self.DIAGONAL

        self.get_random_direction()
        print(self.direction)

        self.new_direction_debounce = 0

        self.x_move = 1
        self.y_move = 0
        self.pixel_multiplier = 1
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

    def get_random_direction(self):
        if self.direction_mode == self.DIAGONAL:
            self.direction = directions_list[ random.randint(4,7)]
        else:
            self.direction = directions_list[random.randint(0, 3)] #Directions.LEFT

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
                    self.win_list.append([winn, ("-ROW2-", len(self.win_list), self.id), False])
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
    
    def get_random_dir(self):
        ds = [attr for attr in dir(Directions) if not callable(getattr(Directions, attr)) and not attr.startswith("__")]
        return getattr(Directions, random.choice(ds))

    def move_windows(self, x, y):
        for elem in self.win_list:
            win = elem[0]
            if win == None: continue
            if win.width != 0:
                win.move(x, y)

    def start_loop(self):
        self.t = threading.Thread(target=self.main_loop, args=())
        self.t.start()

    def is_box_out_of_area(self, rect):
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
                self.move_windows(-1, 0)
            elif side_delta < 0:
                self.move_windows(1, 0)

            if side_delta > 0:
                return Collisions.RIGHT_SIDE
            elif side_delta < 0:
                return Collisions.LEFT_SIDE
                
        else:
            # if top_delta > 0:
            #     self.move_windows(0, -1)
            # elif top_delta < 0:
            #     self.move_windows(0, 1)
            if top_delta > 0:
                self.move_windows(0, -1)
            elif top_delta < 0:
                self.move_windows(0, 1)
                
            if top_delta > 0:
                return Collisions.BOTTOM_SIDE
            elif top_delta < 0:
                return Collisions.TOP_SIDE


    def determine_direction(self, collision):
        #self.x_move = 0
        #self.y_move = 0
        if self.direction_mode == self.NON_DIAGONAL:
        #     if self.direction.id % 2 == 0:
        #         self.direction = directions_list[self.direction.id+1]
        #     else:
        #         self.direction = directions_list[self.direction.id-1]
            if collision == Collisions.LEFT_SIDE:
                self.x_move = 0
                self.y_move = -1
                self.direction = Directions.TOP
            elif collision == Collisions.RIGHT_SIDE:
                self.x_move = 0
                self.y_move = 1
                self.direction = Directions.BOTTOM
            elif collision == Collisions.TOP_SIDE:
                self.x_move = 1
                self.y_move = 0
                self.direction = Directions.RIGHT
            elif collision == Collisions.BOTTOM_SIDE:
                self.x_move = -1
                self.y_move = 0
                self.direction = Directions.LEFT

        else:
            if self.direction == Directions.TOP_RIGHT:
                if collision == Collisions.TOP_SIDE:
                    self.direction = Directions.BOTTOM_RIGHT
                else:
                    self.direction = Directions.TOP_LEFT

            elif self.direction == Directions.BOTTOM_RIGHT:
                if collision == Collisions.RIGHT_SIDE: 
                    self.direction = Directions.BOTTOM_LEFT
                else:
                    self.direction = Directions.TOP_RIGHT


            elif self.direction == Directions.BOTTOM_LEFT:
                if collision == Collisions.BOTTOM_SIDE:
                    self.direction = Directions.TOP_LEFT
                else:
                    self.direction = Directions.BOTTOM_RIGHT

            
            elif self.direction == Directions.TOP_LEFT:
                if collision == Collisions.LEFT_SIDE:
                    self.direction = Directions.TOP_RIGHT
                else:                    
                    self.direction = Directions.BOTTOM_LEFT

        self.new_direction_debounce = 10
        print("new direction: ",  self.direction.name)

    def get_group_box(self):
        topleft = coor(self.scree_res.width, self.scree_res.height)
        bottomright = coor(0, 0)

        for elem in self.win_list:
            win = elem[0]
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

        return r #{"topleft":topleft, "bottomright":bottomright, "topright":topright, "bottomleft":bottomleft}

    def custom_sleep(self, total_sleep_time):
        rem = total_sleep_time
        if total_sleep_time <= 0.1: 
            sleep(total_sleep_time)
        else:
            while rem > 0:
                sleep(0.1)
                rem-=0.1
                if self.break_sleep or rem <= 0:
                    self.break_sleep = False
                    break

    def main_loop(self):
        self.loop_running = True
        print("Starting main loop id ", self.id)

        while 1:

            self.generated_group_box = self.get_group_box()
            collision = self.is_box_out_of_area(self.generated_group_box)
            #print(collision)
            if self.new_direction_debounce:
                self.new_direction_debounce -=1
            elif collision:
                self.determine_direction(collision)
                
            self.move_windows(self.direction.x *self.pixel_multiplier, self.direction.y *self.pixel_multiplier)

            # for win in self.win_list:
            #     if win.width != 0:
            #         win.move(self.x_move, self.y_move)
            total_sleep_time = self.pixels_per_min / 60
            per_sec = self.pixels_per_min / 60
            self.custom_sleep(1/per_sec)

            #print("hello")
            if self.stop:
                print("Stopping id ", self.id)
                self.stop = False
                self.loop_running = False
                break