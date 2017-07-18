"""
mendonsearch.py

author: Anil Poriya


description: mendonsearch takes in an image and loads the pixel values of that image in its grid.
It then takes in source and destination locations from the input and finds the shortest path if present
within the map.

Assumptions: we assume that pixels with value 9 are out of bounds and hence will not be included in the path
             Same with pixel value 5 since it is impassible vegetation.
             Thus when providing inputs for source and destination, we need to provide valid passible locations
             as source and destination, otherwise the code will exit saying source or destination is out of bounds.
             Although implausible, in this code, we assume we can pass through water and would cost us some time.
             The relative costs and speeds for different terrains gives the idea of slowness through water.
             Thus, our path may include a path which goes through water.

We need to have terrain2.png file in the same folder as this code.

Note: For some values of source and destination, the code will take some significant amount of time to calculate
the path.

"""
import sys
from PIL import Image

from operator import attrgetter
terrains = {(248,148,18) : 0, (255,192,0) : 1, (255,255,255) : 2, \
            (2,208,60) : 3, (2,136,40) : 4, (5,73,24) : 5, (0,0,255) : 6,\
            (71,51,3) : 7, (0,0,0) : 8, (205,0,101) : 9}
class Pixel:
    # __slots__ =  'r_loc','c_loc','parent','status','g_cost','h_cost','f_cost'

    # speed = {0: 10, 1: 4, 2: 7, 3: 6, 4: 11, 5: 12, 6: 9, 7: 5, 8: 8, 9: 13}
    """
        terrcost is the dictionary that indicates the cost moving each pixel through a particular terrain type
        terrcost is taken relatively according to the terrain with paved roads and open land having low costs
        and impassible vegetation and water having comparatively higher costs

        each cost in terrcost dictionary will be in metres

        terrspeed is the dictionary that indicates the speed at which one can move across a pixel of that terrain type.
        Thus if the terrain is open land or paved roads, speed will be high.

        the speeds mentioned in the terrspeed dictionary will be in metres/second.

        terrcost and terrspeed have been taken in such proportions that while calculating f cost, you
        would only consider cost of moving across pixel and you can be assured that moving across a pixel with
        low cost would in turn mean moving across that pixel in less time. Thus we can consider time factor at
        the last when we have calculated the shortest path in terms of cost(which would also in turn give us best time)

        """

    __slots__ = 'r_loc','c_loc','parent','status','g_cost','h_cost','f_cost','t_cost','t_speed','pixel'
    terrcost = {0: 6, 1: 7, 2: 8, 3: 9, 4: 10, 5: 12, 6: 11, 7: 4, 8: 5, 9: 50}

    terrspeed = {0: 9, 1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 4, 7: 11, 8: 10, 9: 1}

    def __init__(self,pix,x,y):
        #self.status = self.speed[pix]
        self.pixel = pix
        self.t_cost = self.terrcost[pix]
        self.t_speed = self.terrspeed[pix]
        self.r_loc = x
        self.c_loc = y
        self.h_cost = sys.maxsize
        self.g_cost = sys.maxsize
        self.f_cost = sys.maxsize

    def __str__(self):
        return '( x: ' + str(self.r_loc) + ', y: ' + str(self.c_loc) + ' )' + '-> '+str(self.pixel)\
                            + ' (pixel)'

class Path:

    __slots__ = 'grid','check','visited','start','end', 'path', 'time','pixpath'

    def __init__(self):
        """
        Creates an open, closed and path lists
        """
        self.check = []
        self.visited = []
        self.path = []
        self.time = 0
        self.pixpath = []

    def convertToNodes(self,arr):
        """
        Converts terrain values to Pixel object
        :param arr: terr 2-D array obtained from starter code provided
        :return: 2-D array --> grid, array of pixel objects
        """
        terr = []

        for row in range(len(arr)):
            trow = []
            for col in range(len(arr[0])):
                trow.append(Pixel(arr[row][col],row,col))           # creates object
            terr.append(trow)
        return terr

    def init_path(self,source,destination):
        """
        Performs initializations for source and destination
        :param source: start point
        :param destination: end point
        """
        self.start = source
        self.end = destination
        self.start.parent = None                                    # source has no parent
        self.start.g_cost = 0                                       # no g-cost for source
        self.start.h_cost = self.cal_Hcost(self.start)
        self.start.f_cost = self.start.g_cost + self.start.h_cost
        self.end.h_cost = 0                                         # no h-cost for destination

    def cal_Hcost(self,curr):
        """
        Computes cost of moving from current node to destination. Uses diagonal distance formula
        :param curr: current node
        :return: H-cost
        """
        xVal = abs(curr.r_loc - self.end.r_loc)
        yVal = abs(curr.c_loc - self.end.c_loc)
        if xVal > yVal:
            H = 14 * yVal + 10 * (xVal - yVal)
        else:
            H = 14 * xVal + 10 * (yVal - xVal)
        return H

    def givePosition(self,child,parent):
        """
        Computes cost of moving from parent to child,
         relative to child's position from parent.(horizontally, vertically or diagonally)
        :param child: child node
        :param parent: parent node
        :return: cost relative to position
        """
        if child.r_loc == parent.r_loc or child.c_loc == parent.c_loc:          # vertical or horizontal
            return 10
        else: return 14                                                         # diagonal

    def cal_Gcost(self,curr):
        """
        Computes cost of moving from source to current node
        :param curr: current node
        :return: G-cost
        """
        #G = curr.parent.g_cost + self.givePosition(curr,curr.parent) + curr.status # *** This might need modifications
        G = curr.parent.g_cost + self.givePosition(curr,curr.parent) + curr.t_cost
        return G

    def compute_variable(self,child):
        """
        Computes all the costs for a node
        :param child: node whose costs need to be computed
        :return: costs
        """
        g_temp = self.cal_Gcost(child)
        h_temp = self.cal_Hcost(child)
        f_temp = g_temp + h_temp
        return g_temp,h_temp,f_temp

    def updateNode(self,child,g,h,f):
        """
        Assigns newly found costs.
        :param child: current node
        :param g: G-cost
        :param h: H-cost
        :param f: F-cost
        """
        child.h_cost = h
        child.g_cost = g
        child.f_cost = f

    def isValid(self,row,col):
        """
        Checks to see if position is not out-of-bounds
        :param row: row value
        :param col: column value
        :return: True if in-bound
        """
        if row >= 0 and col >= 0:
            if col < len(self.grid[0]) and row < len(self.grid):
                return True
        return False

    def updateAboveBelow(self,r,c,curr,pos):
        """
        Updates neighbors of the current node which are present either above,
        below or on either side based on the row, column and position provided.
        :param r: start row
        :param c: start column
        :param curr: node currently being explored
        :param pos: 1 --> on either side of curr ; 0 --> rows above and below curr
        :return: None --> no destination found ; endNode --> destination found
        """
        for i in range(1,4):
            if pos == 0 or (pos == 1 and i != 2):
                if self.isValid(r,c+i) and self.grid[r][c+i] not in self.visited:
                    child = self.grid[r][c + i]
                    #print(child.pixel)
                    if child.pixel != 9 and child.pixel != 5:
                        if child not in self.check:
                            child.parent = curr
                            g_temp, h_temp, f_temp = self.compute_variable(child)
                            self.updateNode(child, g_temp, h_temp, f_temp)
                            if child == self.end: return child
                            self.check.append(self.grid[r][c + i])
                        else:
                            old_parent = child.parent
                            child.parent = curr
                            g_temp, h_temp, f_temp = self.compute_variable(child)
                            if f_temp < child.f_cost:
                                self.updateNode(child,g_temp,h_temp,f_temp)
                            else:
                                child.parent = old_parent
        return None

    def trace_path(self,end):
        """
        Trace path from destination to source
        :param end: destination node
        """
        current = end
        while current is not None:
            self.path.append(current)
            if current.parent is not None:
                self.time += self.givePosition(current,current.parent)/current.t_speed
            current = current.parent

    def check_end(self,node):
        """
        Check if destination node reached
        :param node: node to be checked
        :return: True if destination reached, else False
        """
        if node is not None:
            self.trace_path(node)
            return True
        else: return False

    def add_successors(self,curr):
        """
        Adds neighbours of the node currently being explored
        :param curr: the node currently being explored whose 8 neighbours need to be added
        :return: True if end(destination) found, else false
        """

        # c --> column ; r --> row
        c = curr.c_loc - 2

        # 3 cells above current
        r = curr.r_loc - 1
        end = self.updateAboveBelow(r,c,curr,0)
        if self.check_end(end): return True

        # 3 cells below current
        r = curr.r_loc + 1
        end = self.updateAboveBelow(r,c,curr,0)
        if self.check_end(end): return True

        # 2 cells on either side of current
        r = curr.r_loc
        end = self.updateAboveBelow(r,c,curr,1)
        if self.check_end(end): return True

        return False

    def print_path(self):
        for node in reversed(self.path):
            self.pixpath.append((node.c_loc,node.r_loc))
            print(node)
        print('Time:',self.time, " seconds")

    def start_traversing(self):
        """
        Performs A* search
        at every stage, we extract that node or successor which has the lowest f_cost amongst
        all. This ensures that we get a shortest path from the source to the destination.
        """
        self.check.append(self.start)                               # append source to check list
        while len(self.check)!=0 :
            curr = min(self.check,key=attrgetter('f_cost'))         # node currently being explored, with lowest f-cost
            found_path = self.add_successors(curr)                   # adding current node neighbours to check list
            if found_path:
                # *** use self.path to display path from starter code
                self.print_path()
                return True
            self.visited.append(curr)                               # adding current node to visited-list once explored
            self.check.remove(curr)                                 # remove current node from check list once explored

        return False


def display_path(terrim,path):
    tcopy = terrim.copy()
    for step in path:
        tcopy.putpixel(step,(255,0,0))
    tcopy.show()

def main():
    """
    
    We load the image and use the terr array of pixels to continue with our process

    We assume that pixel 9 cannot be reached since it is given as out of bounds
    Thus while entering the values for source and destination, we would need
    values which are not of those nodes whose pixel value is 9.
    If user gives either source or destination which is pixel 9, code will
    display accordingly and stop.

    The assumptions about the pixel values have been stated above in the author section.
    e.g. inputs to provide: source (100,200)  goal (220,340)
                            source (150,200) goal (190,220)

    :return: None
    """
    terrim = Image.open('terrain2.png')
    terrpix = terrim.load()
    # print(terrpix)
    terr = []
    for row in range(500):
        trow = []
        for col in range(400):
            # print(terrpix[col,row][0:3])
            if terrpix[col,row][0:3] not in terrains:
                # if for some reason there is a bad pixel, label it impossible
                # print((row,col))
                trow.append(5)
            else:
                trow.append(terrains[terrpix[col,row][0:3]])
        terr.append(trow)
    #print(terr)
    mendonpath = Path()
    #terr = [[0,2,4,6],[1,3,5,7],[8,0,2,4],[9,1,3,5],[6,7,8,9]]
    mendonpath.grid = mendonpath.convertToNodes(terr)
    #print(mendonpath.grid)
    srow= int(input("Enter source row: "))
    scol = int(input("Enter source col: "))
    drow = int(input("Enter goal row: "))
    dcol = int(input("Enter goal col: "))
    if mendonpath.grid[srow][scol].pixel == 9 or mendonpath.grid[srow][scol] == 5:
        print("Source is out of bounds!")
        exit(0)
    elif mendonpath.grid[drow][dcol].pixel == 9 or mendonpath.grid[drow][dcol] == 5:
        print("Destination is out of bounds !")
        exit(0)
    else:

        mendonpath.init_path(mendonpath.grid[srow][scol],mendonpath.grid[drow][dcol])
    print("Finding Path : ")
    if mendonpath.start_traversing():
        display_path(terrim,mendonpath.pixpath)
    else:
        print("No valid path exists!!")


if __name__ == '__main__':
    main()
