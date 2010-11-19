#!/usr/bin/env python
try: 
    import MySQLdb
except ImportError:
    print("You seem to be missing the MySQLdb package. Please make sure "\
            "it is installed and try again.")
    raise

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
        self.conn = MySQLdb.connect(host = "twiggy",
                        user = "shortqut_user",
                        passwd = "Don'tCommitThis",
                        db = "shortqut")
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def getMySQLVersion(self):
        self.cursor.execute("SELECT VERSION()")
        row = self.cursor.fetchone()
        return row[0]

        #cursor.execute("INSERT INTO `shortqut`.`times` (`road_id`, `time`,
        #        `duration` ) VALUES ('4342791', CURRENT_TIMESTAMP ,
        #        '00:23:41');")

    def getTimes(self):
        self.cursor.execute("SELECT * FROM `times`;")
        rows = self.cursor.fetchall()
        return rows

    def getNeighbor(self):
        self.cursor.execute("SELECT name, road_id, segment_id, int1lat, int1lon, int2lat, int2lon FROM road_names, (select road_id, segment_id, int1lat,int1lon,int2lat,int2lon from segments WHERE (int1lat = '28.5412667' and int1lon = '-81.1958727') or (int2lat = '28.5412667' and int2lon = '-81.1958727')) as a where a.road_id = road_names.id")
        #self.cursor.execute("SELECT name, road_id, segment_id, int1lat," \
        #        "int1lon, int2lat, int2lon FROM road_names," \
        #        "(SELECT road_id, segment_id, int1lat, int1lon," \
        #        "  int2lat, int2lon FROM `segments`" \
        #        "  WHERE (int1lat = '28.5412667' AND int1lon = '-81.1958727')"\
        #        "  OR (int2lat = '28.5412667' AND int2lon = '-81.1958727')" \
        #        ") AS a" \
        #        "WHERE a.road_id = road_names.id;")
        return self.cursor.fetchall()


if __name__ == "__main__":
    db = Database()
    print(db.getMySQLVersion())
    for row in db.getTimes():
        print(row)
    
    for row in db.getNeighbor():
        print(row)
