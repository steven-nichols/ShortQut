import threading
from threading import Thread
import Queue
import nmea
import time
from Log import Log

log = Log('gpstalker')

class GPSTalker:
    def __init__(self,serial="/dev/ttyUSB0"):
        self.cares = {'GGA' : True,
                 'RMC' : False,
                 'GSV' : False,
                 'GSA' : False
                 }
        self.lock = threading.Lock()
        self.running = True
        self.child = False
        # Queue is thread-safe
        self.messages = Queue.Queue()
        if serial:
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
        time = nmea.convertTime(msg)
        lat = nmea.convertLatitude(msg)
        lon = nmea.convertLongitude(msg)
        self.messages.task_done()
        return (time, lat, lon)

    def consume(self):
        while(self.messages.qsize() > 0):
            print self.getMsg()
        if(self.child):
            self.messages.join()

    def close(self):
        log.info('Closing GPS')
        self.setRunning(False)
        time.sleep(5)
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
        talker.runLoop()
        return talker


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

