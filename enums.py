class Direction:
    def __init__(self, name, id, x=0, y=0) -> None:
        self.name = name
        self.id = id
        self.x = x
        self.y = y
    def __str__(self):
        return "name:" + str(self.name) + " id:" + str(self.id)

#DIRECTIONS

    
str_list = ["TOP",
    "BOTTOM",
    "LEFT",
   "RIGHT",
    "TOP_RIGHT", 
   "BOTTOM_LEFT",
    "TOP_LEFT",
    "BOTTOM_RIGHT"]

directions_list = [Direction(str_, count)for count, str_ in enumerate(str_list)]

class Directions():
    pass

def get_contrary(direction):
    #if direction:
    if direction.id % 2 == 0:
        return  directions_list[direction.id+1]
    else:
        return directions_list[direction.id-1]
         

for elem in directions_list:
    setattr(Directions, elem.name, elem)

Directions.TOP_RIGHT.x = 1
Directions.TOP_RIGHT.y = -1

Directions.TOP_LEFT.x = -1
Directions.TOP_LEFT.y = -1

Directions.BOTTOM_RIGHT.x = 1
Directions.BOTTOM_RIGHT.y = 1

Directions.BOTTOM_LEFT.x = -1
Directions.BOTTOM_LEFT.y = 1

Directions.LEFT.x = -1
Directions.LEFT.y = 0

Directions.RIGHT.x = 1
Directions.RIGHT.y = 0

Directions.TOP.x = 0
Directions.TOP.y = -1

Directions.BOTTOM.x = 0
Directions.BOTTOM.y = 1



class win_():
    def __init__(self, win, key, added_manually, direction) -> None:
        self.win = win
        self.key = key
        self.added_manually = added_manually
        self.direction = direction
        self.overlapping_wins = []
        self.last_collision = None
        self.marked_for_del = False
        #self.debounce_col = 0
    def get_box(self):
        return self.win
    def get_wins(self):
        return [self.win]
    
    def __str__(self):
        return "name:" + str(self.win.title if self.win else "None") + " hwnd:" + str(self.win._hWnd if self.win else "None")
    def __repr__(self):
        return "name:" + str(self.win.title if self.win else "None") + " hwnd:" + str(self.win._hWnd if self.win else "None")
    
class win_group():
    def __init__(self,l, rect) -> None:
        self.win_list = l
        self.rect = rect
        #self.direction = None
        self.last_collision = 0

    def get_box(self):
        return self.rect
    def get_wins(self):
        return self.win_list

str_list = ["TOP_SIDE",
    "BOTTOM_SIDE",
    "LEFT_SIDE",
   "RIGHT_SIDE",
    "TOP_RIGHT_SIDE", 
   "BOTTOM_LEFT_SIDE",
    "TOP_LEFT_SIDE",
    "BOTTOM_RIGHT_SIDE"]

collisions_list = [Direction(str_, count)for count, str_ in enumerate(str_list)]

#COLLISIONS
class Collisions():
    pass
    # TOP_SIDE = Direction("TOP_SIDE", 0)
    # BOTTOM_SIDE = Direction("BOTTOM_SIDE",1)
    # LEFT_SIDE = Direction("LEFT_SIDE",2)
    # RIGHT_SIDE = Direction("RIGHT_SIDE",3)
    # TOP_RIGHT_SIDE = Direction("TOP_RIGHT_SIDE",4)
    # TOP_LEFT = Direction("TOP_LEFT",5)
    # BOTTOM_RIGHT =Direction("BOTTOM_RIGHT",6)
    # BOTTOM_LEFT = Direction("BOTTOM_LEFT",7)

for elem in collisions_list:
    setattr(Collisions, elem.name, elem)

GROUP_NONE = 0
GROUP_OVERLAPPING = 1
GROUP_ALL = 2

group_dict = {"-group_all-":2,  "-group_overlapping-":1,  "-ignore_overlapping-":0}

class coor():
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
    def __repr__(self):
        return "x: " + str(self.x) + " y: " + str(self.y)
    def __str__(self):
        return "x:" + str(self.x) + " y:" + str(self.y)

class rect():
    def __init__(self, topleft, bottomright, topright, bottomleft) -> None:
        self.topleft = topleft
        self.bottomright = bottomright
        self.topright = topright
        self.bottomleft = bottomleft
        self.height = bottomright.x - bottomleft.x
        self.width = bottomright.y - topright.y

    #def __repr__(self):
    #    return "x: " + str(self.x) + " y: " + str(self.y)
    def __str__(self):
        ret = [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith("__")]
        str = ""
        for elem in ret:
            ret2 = getattr(self, elem)
            str+= elem + "= " + ret2.__str__() + " | "
        
        return str
