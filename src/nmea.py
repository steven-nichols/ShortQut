import serial

def openGPS(device="/dev/ttyUSB0"):
    return serial.Serial(device,4800)

def getGPSLine(ser):
    data = getSentence(ser)
    if (data):
        #print data
        # we can safely ignore the $--, which is the device type
        type = data[0][3:]
        #print "   Type = ", type
        try:
            return (type, eval ("parse%s(%s)" % (type, data[1:])))
        except SyntaxError:
            return
        except NameError:
            return

def parseNMEA(line):
    data = line.split(",")
    return data

def getSentence(ser):
    return parseNMEA(ser.readline())

def getData():
    ser = serial.Serial("/dev/ttyUSB0",4800)
    data = getSentence(ser)
    ser.close()
    return data

def getUseful(string):
    global data
    data = ['a']
    while(data[0] != string):
        data = getData()
        #print data

def pack(keys,values):
    #print "     PACK", keys, " ", values
    r = {}
    for i in range(len(keys)):
        # print "    PACK: ", keys[i], " ", values[i]
        r[keys[i]] = values[i]
    return r

def parseGSV(data):
    """Satellites in view"""
    #print "GSV received"
    # print data
    # print len(data)
    # I can haz proper destructuring-bind ???
    return pack (["totalMsg","lOrigin","totalSat","prn",
                  "elevation","azimuth","snr"],
                 data[:7])

def parseRMC(data):
    #print "RMC received"
    #print data
    return

def parseGGA(data):
    """Global positioning system fix data"""
    #print "GGA received"
    # print data
    return pack(["utc", "lat", "ns", "lon", "ew", "quality"
                 "numSats", "horizontalDilution", "altitude",
                 "altitudeUnits", "separation", "separationUnits",
                 "age", "reference"],
                data)

def parseGSA(data):
    #print "GSA received"
    #print data
    return

### The debugging stuff

def start():
    global ser
    ser = serial.Serial("/dev/ttyUSB0",4800)

def end():
    ser.close()

def go():
    start()
    print getGPSLine(ser)
    end()

