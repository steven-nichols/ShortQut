#!/usr/bin/env python
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
'''

def Log(module, lvl=logging.DEBUG):
    '''Module to facilitate logging error or debug messages in a consistent,
    scalable manner.'''
    
    LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}
    lvl = LEVELS.get(lvl, logging.NOTSET)
    LOG_FILENAME = 'shortqut.log'
    logging.basicConfig(filename=LOG_FILENAME, level=lvl)
    return logging.getLogger(module)
