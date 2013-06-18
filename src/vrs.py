#!/usr/bin/env python
import sys, os, logging, urllib2, json, time

logging.basicConfig()
log = logging.getLogger('vrs')
log.setLevel(logging.INFO)


def main():
    log.debug('vrs starting')
    url = "https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&lang=en-GB&maxresults=1"
    hits = 0
    while True:
	b = sys.stdin.readline()
	if b:
	    fname = b[:-1]
	    log.debug('got file: %s', fname)
	    flac=open(fname, "rb").read()                                                       
	    header = {'Content-Type' : 'audio/x-flac; rate=16000'}
	    try:
		req = urllib2.Request(url, flac, header)
		# print 'vrs send'
		data = json.loads(urllib2.urlopen(req).read()                                                              )
		log.debug('vr data: %s', data)
		if data['status'] == 0:
		    h = data['hypotheses']
		    hits += 1
		    log.debug('XXX %d: %s', hits, h[0]['utterance'])
		    print '%d %s' % (hits, h[0]['utterance'])
		else:
		    print '<%d>' % data['status']
	    except urllib2.HTTPError, e:
		log.error('url error: %s',  e)
	else:
	    return

if __name__ == '__main__':
    main()
    
		
