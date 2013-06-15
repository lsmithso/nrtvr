"""
audioconvert ! '\
'level message=true interval=5000000000
"""

import sys, urllib2, pprint, json

url = "https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&lang=en-GB&maxresults=1"
flac=open(sys.argv[1],"rb").read()                                                       
header = {'Content-Type' : 'audio/x-flac; rate=16000'}
try:
    req = urllib2.Request(url, flac, header)                                                 
    data = json.loads(urllib2.urlopen(req).read()                                                              )
    print data
    h = data['hypotheses']
    print h[0]['utterance']
    print h[0]['confidence']
except urllib2.HTTPError, e:
    print e, e.read()
    
