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
	self.fname = 'rip_%04d.wav' % self.index
	self.index += 1
	return self.fname




class Encoder(object):

    READ_BUFFER_SIZE = 8 * 1024


    def __init__(self):
	self.file_namer =FileName('/tmp')
	self.fd = open(self.file_namer.next(), 'wb')
	signal.signal(signal.SIGUSR1, self.signal_handler)
	    

    def signal_handler(self, signum, frame):
	self.fd.close()
	fname = self.file_namer.next()
	log.debug('nnew file: %s', fname)
	self.fd = open(fname, 'wb')
	

    def run(self):
	while True:
	    b = sys.stdin.read(self.READ_BUFFER_SIZE)
	    if b:
		log.debug('read %d', len(b))
		self.fd.write(b)
	    else:
		log.debug('EOF - bye')
		return
    


if __name__ == '__main__':
    e = Encoder()
    e.run()
