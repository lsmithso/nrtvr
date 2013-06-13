#!/usr/bin/env python
# TODO:
# dest dfilename rotation
# Add silence detect level message=true interval=5000000000 
import sys, os, time
import gobject
import dbus
import dbus.service
import dbus.mainloop.glib
import glib
import pygst
pygst.require("0.10")
import gst
import logging


logging.basicConfig()
log = logging.getLogger('nrtvr')
log.setLevel(logging.DEBUG)

S_NAME = "uk.co.opennet.nrtvr-service"

STREAMS = {
    'r4' : ('mms', 'mms://wmlive-acl.bbc.co.uk/wms/bbc_ami/radio4/radio4_bb_live_eq1_sl1?BBC-UID=743f7d2b70f86c6814c7231b812545a243f9ae4c10900184a4dfd476c840ce2a&amp;SSO2-UID='),
    'mic' : ('parec', '3'),
    }

PIPELINES = {
    'mms' : ('location', 'mmssrc location=LOC name=el_feed ! asfdemux name=demux demux.audio_00 ! multiqueue ! ffdec_wmav2 ! audioresample ! audio/x-raw-int,rate=16000,channels=2 ! audioconvert ! audio/x-raw-int,rate=16000,channels=1'),
    'parec' : ('device', 'pulsesrc device=N name=el_feed ! audio/x-raw-int,rate=16000'),
    }
    


class FileName(object):
    def __init__(self, dir_name):
	self.dir_name = dir
	self.index = 0
	self.fname = None

    def next(self):
	self.fname = 'rip_%04d.flac' % self.index
	self.index += 1
	return self.fname
    

class GapTimer(object):
    def __init__(self, feeder, max_recording, gap_level):
	self.feeder = feeder
	self.max_recording = max_recording
	self.gap_level = gap_level
	self.last_gap = time.time()

    def level_msg(self, msg):
	# TODO: check level if after min time. 
	now = time.time()
	if now > self.last_gap:
	    self.feeder.swith_file()
	    self.last_gap = now
    
	

class Feed(object):

    def __init__(self, src_name):
	self.terminating = False
	self.file_namer = FileName('.')
	self.build_pipeline(src_name)

    def play(self):
	pass

    def pause(self):
	pass

    def terminate(self):
	self.terminating = True
	self.el_feed.send_event(gst.event_new_eos())

    def file_switcher(self):
	# Rename - next_seg?
	pass
	
	

    def build_pipeline(self, src_name):
	log.debug('Building pipeline for %s', src_name)
	try:
	    feed_type, arg = STREAMS[src_name]
	except KeyError, e:
	    raise KeyError('Unknown source: %s' % src_name)
	try:
	    prop_arg, feed = PIPELINES[feed_type]
	except KeyError, e:
	    raise KeyError('Unknown feed_type: %s in stream: %s' % (feed_type, name))
	p = '%s ! level name=el_level message=true interval=1000000000 ! flacenc ! filesink  location=sink.flac name=el_sink' %  feed
	log.debug('pipeline: %s', p)
        self.feeder = gst.parse_launch(p)
	self.el_feed = self.feeder.get_by_name('el_feed')
	self.el_feed .set_property(prop_arg, arg)
	self.el_sink = self.feeder.get_by_name('el_sink')
	self.el_sink.set_property('location', self.file_namer.next())
	self.el_level = self.feeder.get_by_name('el_level')
	bus = self.feeder.get_bus()
        bus.add_watch(self._on_message)
	self.feeder.set_state(gst.STATE_PLAYING)        
		

	
	

    def _on_message(self, bus, message):
	#	print message.type, 'xxxx', message
	if message.type == gst.MESSAGE_EOS:
	    if self.terminating:
		sys.exit(0)
	elif message.type == gst.MESSAGE_ELEMENT:
	    # and message.structure.has_key('level']:
	    peak = message.structure['peak'][0]
	    if peak < -40:
		print int(peak)
	return gst.BUS_PASS
	    

def main(src_name):
    log.debug('main')
    main_loop = dbus.mainloop.glib.DBusGMainLoop(set_as_default = True)
    session_bus = dbus.SessionBus()
    name = dbus.service.BusName(S_NAME, session_bus)
    feeder = Feed(src_name)
    mainloop = gobject.MainLoop()
    log.info('main loop running')
    while True:
	try:
	    mainloop.run()
	except KeyboardInterrupt, e:
	    feeder.terminate()


if __name__ == '__main__':
    if len(sys.argv) == 1:
	print '\n'.join(STREAMS.keys())
	sys.exit(1)
    main(sys.argv[1])
    
