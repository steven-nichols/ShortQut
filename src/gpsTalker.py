import threading
import Queue
import nmea

class GPSTalker:
    cares = {'GGA' : True,
             'RMC' : False,
             'GSV' : False,
             'GSA' : False
             }
    lock = threading.Lock()
    running = True
    # Queue is thread-safe
    messages = Queue()
    def __init__(self,serial="/dev/ttyUSB0"):
        self.ser = nmea.openGPS(serial)
    def runLoop(self):
        self.child = TalkerThread(self)
    def addMsg(self):
        (type,data) = nmea.getGPSLine(self.ser)
        if(self.cares[type]):
            self.addMsg(data)



class TalkerThread(Thread):
    def __init__(self,talker):
        Thread.__init__(self)
        self.talker = talker

    def run(self):
        while(self.talker.running):
            self.talker.addMsg()
