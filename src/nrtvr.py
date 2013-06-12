#!/usr/bin/env python
# TODO:
# Find out why mic recording doesn't work
# Add EOS on signal term
# dest dfilename rotation
# Add silence detect

import sys, os
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
    'mms' : ('location', 'mmssrc location=LOC name=feed_name ! asfdemux name=demux demux.audio_00 ! multiqueue ! ffdec_wmav2 ! audioresample ! audio/x-raw-int,rate=16000,channels=2 ! audioconvert ! audio/x-raw-int,rate=16000,channels=1'),
    'parec' : ('device', 'pulsesrc device=N name=feed_name'),
    }
    

class Feed(object):

    def __init__(self, src_name):
	self.current_sink_filename = '/tmp/x.flac'
	self.build_pipeline(src_name)

    def play(self):
	pass

    def pause(self):
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
	p = '%s ! flacenc ! filesink  location=sink.flac name=sink_name' %  feed
	log.debug('pipeline: %s', p)
        self.feeder = gst.parse_launch(p)
	self.feed_src = self.feeder.get_by_name('feed_name')
	self.feed_src .set_property(prop_arg, arg)
	self.sink_name = self.feeder.get_by_name('sink_name')
	self.sink_name.set_property('location', self.current_sink_filename)
	bus = self.feeder.get_bus()
        bus.add_watch(self._on_message)
	self.feeder.set_state(gst.STATE_PLAYING)        
		

	
	

    def _on_message(self, bus, message):
	return gst.BUS_PASS
	    

def main(src_name):
    log.debug('main')
    main_loop = dbus.mainloop.glib.DBusGMainLoop(set_as_default = True)
    session_bus = dbus.SessionBus()
    name = dbus.service.BusName(S_NAME, session_bus)
    feeder = Feed(src_name)
    mainloop = gobject.MainLoop()
    log.info('main loop running')
    mainloop.run()



if __name__ == '__main__':
    if len(sys.argv) == 1:
	print '\n'.join(STREAMS.keys())
	sys.exit(1)
    main(sys.argv[1])
    