* Near Real Time Voice Recognition

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
