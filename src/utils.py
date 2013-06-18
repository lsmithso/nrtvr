import logging, os
import pygst
pygst.require("0.10")
import gst

def setup_logger(whom):
    logging.basicConfig()
    log = logging.getLogger(whom)
    log.setLevel(logging.INFO)
    e = os.getenv('NRTVR_DEBUG')
    if e is not None:
	if e == 'all' or whom in e:
	    log.setLevel(logging.DEBUG)
    log.debug('%s is logging because of %r', whom, e)
    return log

def log_gst_state(log, message):
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


