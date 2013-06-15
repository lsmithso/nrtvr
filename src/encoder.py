#!/usr/bin/env python
import sys, os, logging, signal
import gobject
import glib
import pygst
pygst.require("0.10")
import gst

logging.basicConfig()
log = logging.getLogger('enc')
log.setLevel(logging.DEBUG)

FLAC_TEST = False


class FileName(object):
    def __init__(self, dir_name):
	self.dir_name = dir
	self.index = 0
	self.fname = None

    def next(self):
	self.fname = 'rip_%04d.wav' % self.index
	self.index += 1
	return self.fname




class FlacEncode(object):

    def __init__(self):
	self.pipeline =  gst.parse_launch('filesrc name=el_src location=x ! wavparse ! audioconvert ! flacenc ! filesink name=el_sink location=Y')
	self.el_src = self.pipeline.get_by_name('el_src')
	self.el_sink = self.pipeline.get_by_name('el_sink')
	bus = self.pipeline.get_bus()
        bus.add_watch(self._on_message)
	self.pipeline.set_state(gst.STATE_NULL)

    def encode(self, name):
	log.debug('new encode %s', name)
	self.el_src.set_property('location', name)
	self.el_sink.set_property('location', name + '.flac') # FIXME
	self.pipeline.set_state(gst.STATE_PLAYING)

	
    def _on_message(self, bus, message):
	if message.type == gst.MESSAGE_STATE_CHANGED:
	    states = message.structure
	    smap = {
		gst.STATE_NULL : 'null',
		gst.STATE_READY : 'ready',
		gst.STATE_PLAYING : 'playing',
		gst.STATE_PAUSED : 'paused',
		gst.STATE_VOID_PENDING : 'void',
		}
	    def x(s): return smap.get(s, s)
	    log.debug('state: %s-%s/%s/%s', message.src.get_name(), x(states['old-state']), x(states['new-state']), x(states['pending-state']))
	if message.type == gst.MESSAGE_EOS:
	    log.debug('flac encode finished %s', message.src.get_name())
	    self.pipeline.set_state(gst.STATE_READY)
		
	    if FLAC_TEST: 
		sys.exit(0)
	return gst.BUS_PASS


class Encoder(object):

    READ_BUFFER_SIZE = 8 * 1024


    def __init__(self):
	self.flac = FlacEncode()
	self.file_namer =FileName('/tmp')
	self.fd = open(self.file_namer.next(), 'wb')
	signal.signal(signal.SIGUSR1, self.signal_handler)
	    

    def signal_handler(self, signum, frame):
	old_name = self.file_namer.fname
	self.fd.close()
	fname = self.file_namer.next()
	log.debug('nnew file: %s', fname)
	self.fd = open(fname, 'wb')
	self.flac = FlacEncode()
	self.flac.encode(old_name)
	
	

    def run(self):
	while True:
	    self.do_read(None, None)

    def do_read(self, src, cond):
	b = sys.stdin.read(self.READ_BUFFER_SIZE)
	if b:
	    self.fd.write(b)
	else:
	    log.debug('EOF - bye')
	    sys.exit(0)
	return True


if __name__ == '__main__':
    e = Encoder()
    gobject.io_add_watch(sys.stdin, gobject.IO_IN | gobject.IO_HUP, e.do_read)
    mainloop= gobject.MainLoop()
    if len(sys.argv) == 2:
	FLAC_TEST = True
	self.flac = FlacEncode()
	flac.encode(sys.argv[1])
    mainloop.run()

