#!/usr/bin/env python
import sys, os, logging, signal

logging.basicConfig()
log = logging.getLogger('enc')
log.setLevel(logging.DEBUG)



class FileName(object):
    def __init__(self, dir_name):
	self.dir_name = dir
	self.index = 0
	self.fname = None

    def next(self):
	self.fname = 'rip_%04d.flac' % self.index
	self.index += 1
	return self.fname


def signal_handler(signum, frame):
    log.debug('signalled')
    

def main():
    log.debug('encoder starting')
    signal.signal(signal.SIGUSR1,signal_handler) 
    while True:
	b = sys.stdin.read()
	if b:
	    log.debug('read %d bytes', len(b))
	else:
	    log.debug('EOF - bye')
	    sys.exit(0)
    

if __name__ == '__main__':
    main()
