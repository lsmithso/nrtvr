* Near Real Time Voice Recognition

** Notes
GapTimer:
Used to flush flac to disk + send message to vr client.
Detects silence (gaps) using level 
If doesnt record to disk.
If non-silent, start recording, start timer
If recording. record for min  10 secs, mac 20 secs (window)
If silence in window, stop recording, flush.
If end of window, stop recording.


Uses gst to capture voice from mic, http or skype and pipes to Googles
voice recognition API in real time. Results can be displayed in near
real time for eg radio program transcriptions, skype calls etc. for
the deafblind for braille users etc.

2x process: 

. Capture captures audio from chosen input stream and transcodes to
flac. Uses level plugin to detect silence and count word
boundaries. Streams flac to file and when sufficient words closes file
and sends filename on pipe to vr process.

. vr process waits for filenames on its input pipe and then makes
Google vr api call, displaying results.

Tried on r4 - pretty crappy results. Maybe meed filter? audiofx for voice.
Carry on anyway.
DCode up python launcher for silence detectiom.
+ pipe to process for tuning filters etc/.



----
gst-launch playbin2 uri="mms://wmlive-acl.bbc.co.uk/wms/bbc_ami/radio4/radio4_bb_live_eq1_sl1?BBC-UID=743f7d2b70f86c6814c7231b812545a243f9ae4c10900184a4dfd476c840ce2a&amp;SSO2-UID="



gst-launch pulsesrc device=3 ! flacenc rate=16000 ! filesink location=z.flac

gst-launch -e pulsesrc device=3 ! audio/x-raw-int,rate=16000,channels=1 ! flacenc  ! filesink location=z.flac

mms://wmlive-acl.bbc.co.uk/wms/bbc_ami/radio4/radio4_bb_live_eq1_sl1?BBC-UID=743f7d2b70f86c6814c7231b812545a243f9ae4c10900184a4dfd476c840ce2a&amp;SSO2-UID=
gst-launch -e souphttpsrc location=$U  ! audio/x-raw-int,rate=16000,channels=1 ! flacenc  ! filesink location=z.flac


gst-launch -e mmssrc location=$U! asfdemux name=demux  demux.audio_00  ! audio/x-raw-int,rate=16000,channels=1 ! flacenc  ! filesink location=z.flac

19   gst-launch mmssrc location=mms://195.37.219.74:8080 ! asfdemux name=demux demux.audio_00 ! demux.video_00 ! { queue ! ffdec_msmpeg4 ! ffcolorspace ! xvimagesink }                                              
20   gst-launch mmssrc location=mms://195.37.219.74:8080 ! asfdemux name=demux demux.video_00 ! { queue ! ffdec_wmv2 ! xvimagesink } demux.audio_00 ! { queue ! ffdec_wmav2 ! osssink }             

23   gst-launch filesrc location=TheChubbChubbs.avi ! avidemux name=demux demux.audio_00 ! { queue ! filesink location=chubb.mp3 }                                                                  
24   gst-launch filesrc location=TheChubbChubbs.avi ! avidemux name=demux demux.audio_00 ! { queue ! mad ! wavenc ! filesink location=chubb.wav }                                                   


gst-launch -e mmssrc location=$U ! asfdemux name=demux  demux.audio_00  ! multiqueue !   filesink location=z

gst-launch -e mmssrc location=$U ! asfdemux name=demux  demux.audio_00  ! multiqueue ! ffdec_wmav2   ! filesink location=z



gst-launch -e mmssrc location=$U ! asfdemux name=demux  demux.audio_00  ! multiqueue ! ffdec_wmav2   ! audioconvert ! flacenc ! filesink location=z




gst-launch -e mmssrc location=$U ! asfdemux name=demux  demux.audio_00  ! multiqueue ! ffdec_wmav2  ! audioresample    ! audio/x-raw-int,rate=6000,channels=2  !  audioconvert ! audio/x-raw-int rate=6000,channels=1  ! flacenc ! filesink location=z

gst-launch -e mmssrc location=$U ! asfdemux name=demux  demux.audio_00  ! multiqueue ! ffdec_wmav2  ! audioresample    ! audio/x-raw-int,rate=16000,channels=2  !  audioconvert ! audio/x-raw-int,rate=16000,channels=1  ! flacenc ! filesink location=/tmp/z
export U="mms://wmlive-acl.bbc.co.uk/wms/bbc_ami/radio4/radio4_bb_live_eq1_sl1?BBC-UID=743f7d2b70f86c6814c7231b812545a243f9ae4c10900184a4dfd476c840ce2a&amp;SSO2-UID="


00000000000000000000
def bus_event(bus, message, *args):
    peak = message.structure['peak'][0]
    if peak < -50:
        print 'silence on the cable! help!'
    return True

mainloop = gobject.MainLoop()

s = 'gnomevfssrc location="http://local-stream:8000/local.ogg" ! '\
      'oggdemux ! vorbisdec ! audioconvert ! '\
      'level message=true interval=5000000000 ! fakesink'

pipeline = gst.parse_launch(s)
pipeline.get_bus().add_signal_watch()
i = pipeline.get_bus().connect('message::element', bus_event)
pipeline.set_state(gst.STATE_PLAYING)
mainloop.run()


cutter plugin?
fdsink - open fd to write to?

You can set the sink to READY then change the location.

gst-inspect multifilesink


* Plan B

Since filesink can't change location on the fly: Open a pipe to a
sub-process and write raw data to it via fdsink. When it time to
change file location, send SIGUSE1. The child process reads stdin to
get raw data till EOF, saving to a file as it does so. SIGUSE1 handler
flushes data to file and closes it, then opens the next file etc. The
signal also sends a message to the Google vr client to read the file,
encode it and call the API.

May be the child process can flac encode on the fly, via a gstreamer
pipe. At SIGUSE1, it puts an eso eos on the stream and stops feeding
data to it. Thus flushing the filesink. Or it flac encodes after the
file switch. Or the Google api does it.

Stage 1: Modify nrtv.py tp send data to subprocess via pipe. Make sire
data written to file. Modify child process to pipe to audioplay tp
make sure its gapless.

