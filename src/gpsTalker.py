import threading
from threading import Thread
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
            if(self.cares[type]):
                self.addMsg((type,data))
        except TypeError:
            pass
    def addMsg(self,data):
        self.messages.put(data)
    def getMsg(self):
        msg = self.messages.get()
        self.messages.task_done()
        return msg
    def consume(self):
        while(self.messages.qsize() > 0):
            print self.getMsg()
        self.messages.join()
    def close(self):
        self.ser.close()
    def setRunning(self,run):
        with self.lock:
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
        with self.talker.lock:
            running = self.talker.running
        while(running):
            with self.talker.lock:
                self.talker.recvMsg()
                running = self.talker.running

