import math
import time
import gpstalker
from testtalker import TestTalker

#CONVERSIONS
#distance between 100.0001 N, 100.0001 W 
#and 100.0001 N, 100.0002 W = 36.457748647135055 ft
#   54 m/s/s = F1 car = 177 f/s/s   average luxury sedan = 30 f/s/s

class MapFactory:

    location = None
    mytalker = None
    
    def __init__(self):
        #instantiate a GPSTalker
        #mytalker = GPSTalker()
        #loco = mytalker.getMsg
        self.mytalker = TestTalker("data/gps3.out")
        self.get_bearings()
        return
    
    def get_location(self):
        return location
        
    def update_location(self):
        while not self.mytalker.getMsg():
            time.sleep(.5)
        loc = self.mytalker.getMsg()
        self.location = {'time': loc[0], 'lat': loc[1], 'lon': loc[2]}
        
    def get_bearings(self):
        cur_intersection = None    #Where road segment begins
        self.update_location()
        #find nearest node or just the road ID or the list of intersections
        # of the road I'm on (database)
        #con_list = (returned above)
        """for intersection in con_list:
            if get_dist(self.location, instersection) < 100:
                cur_intersection = intersection
                map_points(cur_intersection)
                break
        """

    def map_points(self, cur_intersection):
        time_taken = None   #road segment duration
        segment_begin = None  #Where road segment begins
        segment_end = None  #Where road segment ends
        closest_pt = None   #our closest point to intersection coordinates
        #con_list = None  #connection list: list of intersections that connect
        running = True
        
        while running:  #loop to get data from queue
            self.update_location()
            #distance to next intersection
            current_dist = get_dist(self.location, cur_intersection)
            if 100 > current_dist:
                closest_pt = find_segment_end(cur_intersection, self.location)
            if segment_begin == None:
                segment_begin = closest_pt
            else:
                segment_end = closest_pt
                time_taken = segment_end['time'] - segment_begin['time']
                #send Laura time_taken and segment_begin['time']
                segment_begin = segment_end
        return
    
    def find_segment_end(self, cur_intersection, closest_pt):
        self.update_location()     
        current_dist = get_dist(self.location, cur_intersection)  
        closest_pt_dist = get_dist(closest_pt, cur_intersection)
        if closest_pt_dist > current_dist:
            closest_pt['time'] = self.location['time']
            closest_pt['lat'] = cur_intersection[0]
            closest_pt['lon'] = cur_intersection[1]
        if current_dist > 125:
            return closest_pt
        else:
            return find_segment_end(cur_intersection, closest_pt)

    def get_dist(self, pt1, pt2):
        coord_dist = math.sqrt(math.pow(abs(pt2['lat'] - pt1['lat']),2) +  \
        math.pow(abs(pt2['lon'] - pt1['lon']),2))
        dist = (coord_dist*10000)*36.5 #distance between pts in ft

    def get_vel(self, pt1, pt2):
        coord_dist = math.sqrt(math.pow(abs(pt2['lat'] - pt1['lat']),2) +  \
        math.pow(abs(pt2['lon'] - pt1['lon']),2))
        dist = (coord_dist*10000)*36.5 #distance between pts in ft
        #print "point 1 lat:", pt1_lat,"point 1 lon ",pt1_lon,"dist/vel = ",dist
        tim = pt2['time']-pt1['time'] #almost always 1 sec exactly
        vel = ((dist/5280)*3600)/(tim)  #vel in MPH
        return vel

def main():
    MapFactory()
    

if __name__ == '__main__':
    main()
