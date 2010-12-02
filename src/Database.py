#!/usr/bin/env python
'''Provides functions for converting between strings and geographical 
coordinates. Also provides the Database class for communicating with
a MySQL database holding the map data.'''
import math
try:
    import MySQLdb
    from MySQLdb.constants import FIELD_TYPE
except ImportError:
    print("You seem to be missing the MySQLdb package. Please make sure "\
            "it is installed and try again.")
    raise
from Log import Log
log = Log('Database', 'info')

def cord2name(lat, lon):
    '''Convert a set of cordinates to a unique string.'''
    return "%s,%s" % (str(lat), str(lon))

def name2cord(name):
    '''Convert a coordinate pair like "28.5815770,-81.1719860" into latitude
    and longitude tuple.'''
    return name.split(",")

def get_dist(pt1, pt2):
    '''Calcuate the Euclidean distance between two points specified by
    latitude and longitude. Distance is returned in feet. Based on a 
    method with the same name in MapFactory.py but moved here because
    the other method was required an instance of the MapFactory class.'''
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
        #                passwd = "Don'tCommitThis", #WTF WHO COMMITTED THIS
        #                db = "shortqut")
        self.conn = MySQLdb.connect(conv=my_conv,
                        host = "localhost",
                        user = "root",
                        passwd = "",
                        db = "shortqut") #change this back

        self.cursor = self.conn.cursor()

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def getMySQLVersion(self):
        '''Returns the version number of the MySQL database.'''
        self.cursor.execute("SELECT VERSION()")
        row = self.cursor.fetchone()
        return row[0]

    def getTimes(self):
        '''Returns all entries the `times` table as an iterable list'''
        self.cursor.execute("SELECT * FROM `times`;")
        rows = self.cursor.fetchall()
        return rows
    

    def getAvgTravelTime(self, start, end):
        '''Get the average of past travel times across this segment in 
        seconds.'''
        try:
            lat, lon = name2cord(start)[0], name2cord(start)[1]
            self.cursor.execute("select int_id from intersections where lat = %s and lon = %s;" % (lat, lon))
            log.debug("select int_id from intersections where lat = %s and lon = %s;" % (lat, lon))
            set1 = "%d,%d" % (self.cursor.fetchone()[0], self.cursor.fetchone()[0])
            #print(set1)

            lat, lon = name2cord(end)[0], name2cord(end)[1]
            self.cursor.execute("select int_id from intersections where lat = %s and lon = %s;" % (lat, lon))
            log.debug("select int_id from intersections where lat = %s and lon = %s;" % (lat, lon))

            set2 = "%d,%d" % (self.cursor.fetchone()[0], self.cursor.fetchone()[0])
            #print(set2)

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

    def setTravelTime(self, lat_start, lon_start, lat_end, lon_end, duration):
        ''' duration = '00:00:26' '''
        #this query inserts a row of data into the times table when eric passes the intersections' coordinates
        self.cursor.execute("insert into times (int_id1, int_id2, time, duration) select a.int_id, b.int_id, NULL, {0} from (select int_id from intersections where lat = {1} and lon = {2} limit 1) as a, (select int_id from intersections where lat = {3} and lon = {4} limit 1) as b".format(duration, lat_start, lon_start, lat_end, lon_end))


    def getNeighbors(self, node):
        '''Return a list of neighbor nodes, that is, the names of nodes which
        share a segment with this node::
            db.getNeighbors(cord2name("28.5815770", "-81.1719860"))
            # returns
            ['28.5823810,-81.1701780', '28.5883288,-81.1720451', '28.5802643,-81.1747488']
        '''
        neighbors = []
        lat = node['lat']
        lon = node['lon']
        
        #self.cursor.execute("SELECT name, road_id, segment_id, int1lat, int1lon, int2lat, int2lon FROM road_names, (select road_id, segment_id, int1lat,int1lon,int2lat,int2lon from segments WHERE (int1lat = '28.5412667' and int1lon = '-81.1958727') or (int2lat = '28.5412667' and int2lon = '-81.1958727')) as a where a.road_id = road_names.id")
        # All neighbor nodes
        #self.cursor.execute("select int2lat as lat, int2lon as lon from segments where int1lat = {0} and int1lon = {1} union select int1lat as lat, int1lon as lon from segments where int2lat = {0} and int2lon = {1} and oneway = 0;".format(lat, lon))
        # Just intersections
        self.cursor.execute("select distinct lat, lon from ( select road_id1, road_id2 from intersections where lat = {0} and lon = {1}) as a, ( select road_id1, road_id2, lat, lon, sqrt( pow(({0} - lat), 2) + pow(({1} - lon), 2) ) as distance from intersections order by distance) as b where (a.road_id1 = b.road_id1 or a.road_id2 = b.road_id1 or a.road_id1 = b.road_id2 or a.road_id2 = b.road_id2) limit 4".format(lat, lon))
        for row in self.cursor.fetchall():
            neighbors.append({'lat': float(row[0]), 'lon': float(row[1])})
        return neighbors

    def getNeighborsFromCoord(self, lat, lon):
        neighbors = []
        self.cursor.execute('''select distinct lat, lon from intersections where road_id1 = ( 
            select road_id from (
                select road_id, sqrt(pow((int1lat - {0}),2) + pow((int1lon - {1}),2)) as distance 
                from segments order by distance) as a limit 1) 
        or road_id2 = ( 
            select road_id from (
                select road_id, sqrt(pow((int1lat - {0}),2) + pow((int1lon - {1}),2)) as distance
                from segments order by distance) as a limit 1)'''.format(lat, lon))
        for row in self.cursor.fetchall():
            neighbors.append({'lat': float(row[0]), 'lon': float(row[1])})
        print "returning from neighbors"
        return neighbors

if __name__ == "__main__":
    db = Database()
    print(db.getMySQLVersion())
    #for row in db.getTimes():
    #    print(row)
    node = {'lat': 28.5815770, 'lon': -81.1719860}
    neighbors = db.getNeighbors(node)
    print(neighbors)
    
    neighbors = db.getNeighbors(node)
    print(neighbors)
    #print(db.getAvgTravelTime())
