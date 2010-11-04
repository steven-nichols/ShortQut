#!/usr/bin/env python
import os
import logging




def Log(module, lvl=logging.DEBUG, fileout=False, screenout=True):
    '''Module to facilitate logging error or debug messages in a consistent,
    scalable manner.
        
    Sample usage. 
    At the beginning of your module add the following lines::

        from Log import Log
        log = Log('my_module')


    To print a message::

        log.info("my_module initiated")  #INFO level
        log.warning('A bad thing happened') #WARNING level


    The accepted message levels are (in order of severity)::

        debug, info, warning, error, critical


    You may limit the amount of output by restricting messages
    by severity level. For example, to only output messages of 
    type warning, error, or critical::

            log = Log('my_module', 'warning')


    By default, output is printed to the console but you can
    also print to a file::

        # Print to a file instead of the screen
        log = Log('my_module', fileout=True, screenout=False)
    '''
    LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}
    LOG_FILE = "shortqut.log"

    lvl = LEVELS.get(lvl, logging.NOTSET)

    log = logging.getLogger(module)
    log.setLevel(lvl)

    if(screenout):
        ch = FormattedStreamHandler()
        log.addHandler(ch)

    if(fileout):
#        if(os.path.exists(LOG_FILE)):
#            try:
#                os.remove(LOG_FILE)
#            except KeyError:
#                pass

        fh = FormattedFileHandler(LOG_FILE)
        log.addHandler(fh)

    return log





import sys
import copy
class FormattedStreamHandler(logging.StreamHandler):
    '''Adapted from Colorizer by Ramonster.
    http://stackoverflow.com/questions/384076/how-can-i-make-the-python-\
            logging-output-to-be-colored/2205909#2205909
    '''

    def colorize(self, levelno, text):
        '''http://docs.python.org/dev/library/logging.html#formatter-objects'''
        NORMAL = '\x1b[0m'
        
        if(levelno >= 50): # CRITICAL / FATAL
            color = '\x1b[91m' # red
        elif(levelno >= 40): # ERROR
            color = '\x1b[31m' # red
        elif(levelno >= 30): # WARNING
            color = '\x1b[33m' # yellow
        elif(levelno >= 20): # INFO
            color = '\x1b[92m' # green
        elif(levelno >= 10): # DEBUG
            color = '\x1b[94m' # blue
        else: # NOTSET and anything else
            color = NORMAL # normal

        return color + text + NORMAL
        
    def emit(self, record):
        # Need to make a actual copy of the record
        # to prevent altering the message for other loggers
        myrecord = copy.copy(record)
        
        header = "[%s %s:%s]" % (myrecord.levelname.capitalize().ljust(8), 
                                str(os.path.basename(myrecord.pathname)), 
                                str(myrecord.lineno).rjust(3))
                                
        # Windows makes it difficult to color the terminal 
        if sys.platform != 'win32':
            # Colorize the header
            header = self.colorize(myrecord.levelno, header)
        
        myrecord.msg = "%s %s" % (header, str(myrecord.msg))  # normal

        logging.StreamHandler.emit(self, myrecord)
        

class FormattedFileHandler(logging.FileHandler):
    def emit(self, record):
        # Need to make a actual copy of the record
        # to prevent altering the message for other loggers
        myrecord = copy.copy(record)
        
        myrecord.msg = "[%s %s:%s] %s" % (myrecord.levelname.capitalize().ljust(8), 
                                str(os.path.basename(myrecord.pathname)), 
                                str(myrecord.lineno).rjust(3),
                                str(myrecord.msg))
                                
        logging.StreamHandler.emit(self, myrecord)
