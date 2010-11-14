import gpstalker

class TestTalker(gpstalker.GPSTalker):
    def __init__(self, filename):
        gpstalker.GPSTalker.__init__(self,None)
        self.input = open(filename, 'r')
        for line in self.input.readlines():
            self.addMsg(self.interpret(line))
        self.input.close()

    def interpret(self, data):
        """Return a useful interpretation of the `data` given."""
        (time, lat, lon) = data.split()
        return (float(time), float(lat), float(lon))

    def getMsg(self):
        return self.messages.get()

    # The following are overridden to do nothing since they refer to
    # either the child thread or the serial device.  We don't need any
    # of that.
    def close(self):
        return

    def recvMsg(self):
        return

    def runLoop(self):
        return
