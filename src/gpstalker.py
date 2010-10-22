import threading
from threading import Thread
import Queue
import nmea
from Log import Log

log = Log('gpstalker')

class GPSTalker:
    cares = {'GGA' : True,
             'RMC' : False,
             'GSV' : False,
             'GSA' : False
             }
    lock = threading.Lock()
    running = True
    # Queue is thread-safe
    messages = Queue.Queue()

    def __init__(self,serial="/dev/ttyUSB0"):
        self.ser = nmea.openGPS(serial)

    def runLoop(self):
        self.child = TalkerThread(self)
        self.child.start()

    def recvMsg(self):
        try:
            (type,data) = nmea.getGPSLine(self.ser)
            #print data
            log.info('Received %s data from the GPS: %s' % (type,data))
            if(self.cares[type]):
                log.info('Adding data to queue')
                self.addMsg((type,data))
        except TypeError:
            pass

    def addMsg(self,data):
        self.messages.put(data)

    def getMsg(self):
        msg = self.messages.get()[1]
        time = msg["utc"]
        if(msg["ns"] == "S"):
            lat = "-%s" % msg["lat"]
        else:
            lat = msg["lat"]
        if(msg["ew"] == "W"):
            lon = "-%s" % msg["lon"]
        else:
            lon = msg["lon"]
        self.messages.task_done()
        return (time, lat, lon)

    def consume(self):
        while(self.messages.qsize() > 0):
            print self.getMsg()
        self.messages.join()

    def close(self):
        log.info('Closing GPS')
        self.ser.close()

    def setRunning(self,run):
        with self.lock:
            log.info('Setting running: %s' % run)
            self.running = run


def go():
    try:
        global talker
        talker.close()
        talker = GPSTalker()
        talker.runLoop()
        return talker
    except NameError:
        talker = GPSTalker()
        return go()


class TalkerThread(Thread):
    def __init__(self,talker):
        Thread.__init__(self)
        self.talker = talker

    def run(self):
        log.info('Started GPSTalker Thread')
        with self.talker.lock:
            running = self.talker.running
        while(running):
            with self.talker.lock:
                self.talker.recvMsg()
                running = self.talker.running

