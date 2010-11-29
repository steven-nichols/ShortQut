#!/usr/bin/env python
import math
try: 
    import MySQLdb
    from MySQLdb.constants import FIELD_TYPE
except ImportError:
    print("You seem to be missing the MySQLdb package. Please make sure "\
            "it is installed and try again.")
    raise
from Log import Log
log = Log('Database', 'debug')

def cord2name(lat, lon):
    '''Convert a set of cordinates to a unique string.'''
    return "%s,%s" % (str(lat), str(lon))

def name2cord(name):
    '''Convert a coordinate pair like "28.5815770,-81.1719860" into latitude
    and longitude.'''
    return name.split(",")

def get_dist(pt1, pt2):
    '''Calcuate the Euclidean distance between two points specified by
    latitude and longitude. Distance is returned in feet.'''
    coord_dist = math.sqrt(math.pow(abs(pt2['lat'] - pt1['lat']),2) +  \
    math.pow(abs(pt2['lon'] - pt1['lon']),2))
    dist = (coord_dist*10000)*36.5 #distance between pts in ft
    return dist

class Database:
    '''A collection of helper methods that facilitate getting data out of the
    database::
        
        from Database import Database
        db = Database()
        version = db.getMySQLVersion()
    '''

    def __init__(self):
        '''Default constructor establishes an initial connection with the
        database.'''
        my_conv = { FIELD_TYPE.LONG: int }
 
        #self.conn = MySQLdb.connect(host = "twiggy",
        #                user = "shortqut_user",
        #                passwd = "Don'tCommitThis",
        #                db = "shortqut")
        self.conn = MySQLdb.connect(conv=my_conv,
                        host = "localhost",
                        user = "root",
                        passwd = "",
                        db = "shortqut")

        self.cursor = self.conn.cursor()

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def getMySQLVersion(self):
        self.cursor.execute("SELECT VERSION()")
        row = self.cursor.fetchone()
        return row[0]

    def getTimes(self):
        self.cursor.execute("SELECT * FROM `times`;")
        rows = self.cursor.fetchall()
        return rows
    

    def getAvgTravelTime(self, start, end):
        '''Get the average of past travel time across this segment in 
        seconds.'''
        try:
            lat, lon = name2cord(start)[0], name2cord(start)[1]
            self.cursor.execute("select int_id from intersections where lat = %s and lon = %s;" % (lat, lon))
            log.debug("select int_id from intersections where lat = %s and lon = %s;" % (lat, lon))
            set1 = "%d,%d" % (self.cursor.fetchone()[0], self.cursor.fetchone()[0])
            print(set1)

            lat, lon = name2cord(end)[0], name2cord(end)[1]
            self.cursor.execute("select int_id from intersections where lat = %s and lon = %s;" % (lat, lon))
            log.debug("select int_id from intersections where lat = %s and lon = %s;" % (lat, lon))

            set2 = "%d,%d" % (self.cursor.fetchone()[0], self.cursor.fetchone()[0])
            print(set2)

            self.cursor.execute("select sec_to_time(avg(time_to_sec(duration))) as avg_time from times where int_id1 in (%s) and int_id2 in (%s) and hour(time) between 5 and 6;" % (set1, set2))
            return self.cursor.fetchone()[0]
        except TypeError, e:
            log.error(e)
            return None
    

    def getTravelTime(self, node1, node2):
        '''Return the expected travel time from node1 to node2 in seconds, 
        using the average of past trips or an estimate from the distance
        and speed limit. node1 and node2 are strings of the format: lat,lon"'''
        # Check the average of the previously recorded times
        avg = self.getAvgTravelTime(node1, node2)
        if avg is not None:
            log.debug("Travel time between %s and %s is %f" % (node1, node2, avg))
            return avg

        # Estimate the time given the distance and speed
        pt1 = {'lat':float(name2cord(node1)[0]), 'lon':float(name2cord(node1)[1])}
        pt2 = {'lat':float(name2cord(node2)[0]), 'lon':float(name2cord(node2)[1])}
        dist = get_dist(pt1, pt2)
        dist = float(dist) # convert to miles
        speed = (25.0 * 5280.0) / 3600.0 # assume all roads have speed limits of 25 mph
        log.debug("Travel time between %s and %s is %f seconds." % (node1, node2, dist/speed))
        return dist / speed 


    def getNeighbors(self, node):
        #self.cursor.execute("SELECT name, road_id, segment_id, int1lat, int1lon, int2lat, int2lon FROM road_names, (select road_id, segment_id, int1lat,int1lon,int2lat,int2lon from segments WHERE (int1lat = '28.5412667' and int1lon = '-81.1958727') or (int2lat = '28.5412667' and int2lon = '-81.1958727')) as a where a.road_id = road_names.id")
        neighbors = []
        lat, lon = node.split(",")[0], node.split(",")[1]
        
        self.cursor.execute("select road_id, segment_id, int2lat as lat, int2lon as lon from segments where int1lat = {0} and int1lon = {1} union select road_id, segment_id, int1lat as lat, int1lon as lon from segments where int2lat = {0} and int2lon = {1} and oneway = 0;".format(lat, lon))
        for row in self.cursor.fetchall():
            neighbors.append(cord2name(row[2], row[3]))
        return neighbors

if __name__ == "__main__":
    db = Database()
    #print(db.getMySQLVersion())
    #for row in db.getTimes():
    #    print(row)
    
    neighbors = db.getNeighbors(cord2name("28.5815770", "-81.1719860"))
    print(neighbors)

    #print(db.getAvgTravelTime())
