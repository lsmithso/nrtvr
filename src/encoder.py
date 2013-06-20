#!/usr/bin/env python
import sys, os, logging, signal, subprocess
import gobject
import glib
import pygst
pygst.require("0.10")
import gst
import feed, utils

log = utils.setup_logger('enc')


FLAC_TEST = False


class FileName(object):
    def __init__(self, dir_name):
	self.dir_name = dir_name
	if not os.path.exists(dir_name):
	    os.makedirs(dir_name)
	self.index = 0
	self.fname = None

    def next(self):
	self.fname = os.path.join(self.dir_name, 'rip_%04d.raw' % self.index)
	self.index += 1
	return self.fname

    @staticmethod
    def encoded_name(name):
	f = os.path.splitext(name)[0]
	return f + '.flac'


class FlacEncode(object):

    def __init__(self, vrs):
	self.vrs = vrs
	self.pipeline =  gst.parse_launch('filesrc name=el_src location=x ! %s ! flacenc ! filesink name=el_sink location=Y' %  feed.RAW_AUDIO_CAP)
	self.el_src = self.pipeline.get_by_name('el_src')
	self.el_sink = self.pipeline.get_by_name('el_sink')
	bus = self.pipeline.get_bus()
        bus.add_watch(self._on_message)
	self.pipeline.set_state(gst.STATE_NULL)

    def encode(self, name):
	log.debug('new encode %s', name)
	self.raw_name = name
	self.el_src.set_property('location', name)
	self.encoded_filename = FileName.encoded_name(name)
	log.debug('encoded filename: %r', self.encoded_filename)
	self.el_sink.set_property('location', self.encoded_filename)
	self.pipeline.set_state(gst.STATE_PLAYING)

	
    def _on_message(self, bus, message):
	if message.type == gst.MESSAGE_STATE_CHANGED:
	    utils.log_gst_state(log, message)
	elif message.type == gst.MESSAGE_EOS:
	    log.debug('flac encode finished %s', message.src.get_name())
	    self.pipeline.set_state(gst.STATE_READY)
	    if 0:
		os.unlink(self.raw_name)
	    self.vrs.vrs_send(self.encoded_filename)
	    if FLAC_TEST: 
		sys.exit(0)
	return gst.BUS_PASS


class Encoder(object):

    READ_BUFFER_SIZE = 8 * 1024


    def __init__(self):
	self.vrs_spawn()
	self.flac = FlacEncode(self)
	self.file_namer =FileName(utils.DEFAULT_RIP_DIR)
	self.fd = open(self.file_namer.next(), 'wb')
	signal.signal(signal.SIGUSR1, self.signal_handler)
	    

    def signal_handler(self, signum, frame):
	old_name = self.file_namer.fname
	self.fd.close()
	fname = self.file_namer.next()
	log.debug('nnew file: %s', fname)
	self.fd = open(fname, 'wb')
	self.flac = FlacEncode(self)
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

    def vrs_spawn(self):
	self.p = subprocess.Popen('./vrs.py', bufsize = 1, stdin = subprocess.PIPE)

    def vrs_send(self, filename):
	log.debug('vrs_send: %s', filename)
	self.p.stdin.write('%s\n' % filename)
	self.p.stdin.flush()#
			    #p rint 'encode send'



if __name__ == '__main__':
    e = Encoder()
    gobject.io_add_watch(sys.stdin, gobject.IO_IN | gobject.IO_HUP, e.do_read)
    mainloop= gobject.MainLoop()
    if len(sys.argv) == 2:
	FLAC_TEST = True
	self.flac = FlacEncode(self)
	flac.encode(sys.argv[1])
    mainloop.run()

