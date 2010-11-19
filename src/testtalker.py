import time
import gpstalker

class TestTalker(gpstalker.GPSTalker):
    def __init__(self, filename, delay=1):
        gpstalker.GPSTalker.__init__(self,None)
        self.delay = delay
        self.input = open(filename, 'r')
        lines = self.input.readlines()
        self.input.close()
        for line in lines:
            self.addMsg(self.interpret(line))

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
        return

    def runLoop(self):
        return
