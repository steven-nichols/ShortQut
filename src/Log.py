#!/usr/bin/env python
import os
import logging


'''Sample usage:

At the beginning of your module add the following lines:

    from Log import Log
    log = Log('my_module')


To print a message:

    log.info("my_module initiated")  #INFO level
    log.warning('A bad thing happened') #WARNING level


The accepted message levels are (in order of severity):

    debug, info, warning, error, critical


You may limit the amount of output by restricting messages
by severity level:
    For example,
        log = Log('my_module', 'warning')

    will only output messages of type warning, error, or critical.


By default, output is printed to the console but you can
also print to a file:

    # Print to a file instead of the screen
    log = Log('my_module', fileout=True, screenout=False)

'''

def Log(module, lvl=logging.DEBUG, fileout=False, screenout=True):
    '''Module to facilitate logging error or debug messages in a consistent,
    scalable manner.'''

    LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}
    LOG_FILE = "shortqut.log"

    lvl = LEVELS.get(lvl, logging.NOTSET)

    #logging.basicConfig(level=lvl)
    log = logging.getLogger(module)
    log.setLevel(lvl)

    if(screenout):
        import platform
        if platform.system() == 'Windows':
            ch = logging.StreamHandler()
            ch_fmt = logging.Formatter("%(levelname)s:%(name)s:%(message)s")
        else:
            ch = ColoredConsoleHandler()
            ch_fmt = logging.Formatter("%(message)s")
            
        ch.setFormatter(ch_fmt)
        log.addHandler(ch)

    if(fileout):
        #if(os.path.exists(LOG_FILE)):
            #try:
                #os.remove(LOG_FILE)
            #except KeyError:
                #pass

        fh = logging.FileHandler(LOG_FILE)
        log.addHandler(fh)

        fh_fmt = logging.Formatter("%(levelname)s\t: %(filename)s:%(lineno)d\t: %(message)s")
        fh.setFormatter(fh_fmt)

    return log



import copy
class ColoredConsoleHandler(logging.StreamHandler):
    '''Adapted from Colorizer by Ramonster.
    http://stackoverflow.com/questions/384076/how-can-i-make-the-python-\
            logging-output-to-be-colored/2205909#2205909
    '''
    def emit(self, record):
        # Need to make a actual copy of the record
        # to prevent altering the message for other loggers
        myrecord = copy.copy(record)
        levelno = myrecord.levelno
        if(levelno >= 50): # CRITICAL / FATAL
            color = '\x1b[31m' # red
        elif(levelno >= 40): # ERROR
            color = '\x1b[31m' # red
        elif(levelno >= 30): # WARNING
            color = '\x1b[33m' # yellow
        elif(levelno >= 20): # INFO
            color = '\x1b[37m' # green
        elif(levelno >= 10): # DEBUG
            color = '\x1b[32m' # pink
        else: # NOTSET and anything else
            color = '\x1b[0m' # normal

        #http://docs.python.org/dev/library/logging.html#formatter-objects
        myrecord.msg = "%s%s:%s\t: %s%s" % (color, str(os.path.basename(myrecord.pathname)), str(myrecord.lineno), str(myrecord.msg), '\x1b[0m')  # normal

        logging.StreamHandler.emit(self, myrecord)