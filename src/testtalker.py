import time
import Queue
import gpstalker

class TestTalker(gpstalker.GPSTalker):
    def __init__(self, filename, delay=1):
        gpstalker.GPSTalker.__init__(self,None)
        self.delay = delay
        self.load_file(filename)

    def load_file(self, filename):
        self.messages = Queue.Queue()
        self.buf = Queue.Queue()
        self.input = open(filename, 'r')
        lines = self.input.readlines()
        self.input.close()
        for line in lines:
            self.buf.put(self.interpret(line))

    def interpret(self, data):
        """Return a useful interpretation of the `data` given."""
        (time, lat, lon) = data.split()
        return (float(time), float(lat), float(lon))

    def getMsg(self):
        time.sleep(self.delay)
        if self.messages.qsize() > 0:
            return self.messages.get()
        return None

    # The following are overridden to do nothing since they refer to
    # either the child thread or the serial device.  We don't need any
    # of that.
    def close(self):
        return

    def recvMsg(self):
        self.messages.put(self.buf.get())
        time.sleep(self.delay)
        return
