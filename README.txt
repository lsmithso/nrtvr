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



src//tmp/x.wav: RIFF (little-endian) data, WAVE audio, Microsoft PCM, 32 bit, mono 16000 Hz
1ffmpeg -i /tmp/x.wav 
ffmpeg version 0.7.6-4:0.7.6-0ubuntu0.11.10.3, Copyright (c) 2000-2011 the Libav developers
  built on Jan 24 2013 19:25:26 with gcc 4.6.1
  configuration: --extra-version='4:0.7.6-0ubuntu0.11.10.3' --arch=i386 --prefix=/usr --enable-vdpau --enable-bzlib --enable-libgsm --enable-libschroedinger --enable-libspeex --enable-libtheora --enable-libvorbis --enable-pthreads --enable-zlib --enable-libvpx --enable-runtime-cpudetect --enable-vaapi --enable-gpl --enable-postproc --enable-swscale --enable-x11grab --enable-libdc1394 --enable-shared --disable-static
  WARNING: library configuration mismatch
  avutil      configuration: --extra-version='4:0.7.6ubuntu0.11.10.3' --arch=i386 --prefix=/usr --enable-vdpau --enable-bzlib --enable-libgsm --enable-libschroedinger --enable-libspeex --enable-libtheora --enable-libvorbis --enable-pthreads --enable-zlib --enable-libvpx --enable-runtime-cpudetect --enable-vaapi --enable-libopenjpeg --enable-gpl --enable-postproc --enable-swscale --enable-x11grab --enable-libdirac --enable-libmp3lame --enable-librtmp --enable-libx264 --enable-libxvid --enable-libvo-aacenc --enable-version3 --enable-libvo-amrwbenc --enable-version3 --enable-libdc1394 --shlibdir=/usr/lib/i686/cmov --cpu=i686 --enable-shared --disable-static --disable-ffmpeg --disable-ffplay
  avcodec     configuration: --extra-version='4:0.7.6ubuntu0.11.10.3' --arch=i386 --prefix=/usr --enable-vdpau --enable-bzlib --enable-libgsm --enable-libschroedinger --enable-libspeex --enable-libtheora --enable-libvorbis --enable-pthreads --enable-zlib --enable-libvpx --enable-runtime-cpudetect --enable-vaapi --enable-libopenjpeg --enable-gpl --enable-postproc --enable-swscale --enable-x11grab --enable-libdirac --enable-libmp3lame --enable-librtmp --enable-libx264 --enable-libxvid --enable-libvo-aacenc --enable-version3 --enable-libvo-amrwbenc --enable-version3 --enable-libdc1394 --shlibdir=/usr/lib/i686/cmov --cpu=i686 --enable-shared --disable-static --disable-ffmpeg --disable-ffplay
  avformat    configuration: --extra-version='4:0.7.6-0ubuntu0.11.10.3' --arch=i386 --prefix=/usr --enable-vdpau --enable-bzlib --enable-libgsm --enable-libschroedinger --enable-libspeex --enable-libtheora --enable-libvorbis --enable-pthreads --enable-zlib --enable-libvpx --enable-runtime-cpudetect --enable-vaapi --enable-gpl --enable-postproc --enable-swscale --enable-x11grab --enable-libdc1394 --shlibdir=/usr/lib/i686/cmov --cpu=i686 --enable-shared --disable-static --disable-ffmpeg --disable-ffplay
  avdevice    configuration: --extra-version='4:0.7.6-0ubuntu0.11.10.3' --arch=i386 --prefix=/usr --enable-vdpau --enable-bzlib --enable-libgsm --enable-libschroedinger --enable-libspeex --enable-libtheora --enable-libvorbis --enable-pthreads --enable-zlib --enable-libvpx --enable-runtime-cpudetect --enable-vaapi --enable-gpl --enable-postproc --enable-swscale --enable-x11grab --enable-libdc1394 --shlibdir=/usr/lib/i686/cmov --cpu=i686 --enable-shared --disable-static --disable-ffmpeg --disable-ffplay
  avfilter    configuration: --extra-version='4:0.7.6-0ubuntu0.11.10.3' --arch=i386 --prefix=/usr --enable-vdpau --enable-bzlib --enable-libgsm --enable-libschroedinger --enable-libspeex --enable-libtheora --enable-libvorbis --enable-pthreads --enable-zlib --enable-libvpx --enable-runtime-cpudetect --enable-vaapi --enable-gpl --enable-postproc --enable-swscale --enable-x11grab --enable-libdc1394 --shlibdir=/usr/lib/i686/cmov --cpu=i686 --enable-shared --disable-static --disable-ffmpeg --disable-ffplay
  swscale     configuration: --extra-version='4:0.7.6-0ubuntu0.11.10.3' --arch=i386 --prefix=/usr --enable-vdpau --enable-bzlib --enable-libgsm --enable-libschroedinger --enable-libspeex --enable-libtheora --enable-libvorbis --enable-pthreads --enable-zlib --enable-libvpx --enable-runtime-cpudetect --enable-vaapi --enable-gpl --enable-postproc --enable-swscale --enable-x11grab --enable-libdc1394 --shlibdir=/usr/lib/i686/cmov --cpu=i686 --enable-shared --disable-static --disable-ffmpeg --disable-ffplay
  postproc    configuration: --extra-version='4:0.7.6-0ubuntu0.11.10.3' --arch=i386 --prefix=/usr --enable-vdpau --enable-bzlib --enable-libgsm --enable-libschroedinger --enable-libspeex --enable-libtheora --enable-libvorbis --enable-pthreads --enable-zlib --enable-libvpx --enable-runtime-cpudetect --enable-vaapi --enable-gpl --enable-postproc --enable-swscale --enable-x11grab --enable-libdc1394 --shlibdir=/usr/lib/i686/cmov --cpu=i686 --enable-shared --disable-static --disable-ffmpeg --disable-ffplay
  libavutil    51.  7. 0 / 51.  7. 0
  libavcodec   53.  6. 0 / 53.  6. 0
  libavformat  53.  3. 0 / 53.  3. 0
  libavdevice  53.  0. 0 / 53.  0. 0
  libavfilter   2.  4. 0 /  2.  4. 0
  libswscale    2.  0. 0 /  2.  0. 0
  libpostproc  52.  0. 0 / 52.  0. 0
[wav @ 0x84a4a40] max_analyze_duration reached
Input #0, wav, from '/tmp/x.wav':
  Duration: 09:19:13.40, bitrate: 0 kb/s
    Stream #0.0: Audio: pcm_s32le, 16000 Hz, 1 channels, s32, 512 kb/s
At least one output file must be specified
1

tmp/x.wav: RIFF (little-endian) data, WAVE audio, Microsoft PCM, 32 bit, mono 16000 Hz
1



Bins
----
If you want to add bins to your pipeline, you can do so by specifying 
  <bintype> . ( <properties> <elements> )
in your pipeline. This adds a bin to your pipeline and puts all elements that
are specified between the brackets inside this bin. You can specify properties
of the bin directly after the opening bracket.
There are to special bins: if you don't specify a bintype and no dot either, the
type of the bin defaults to "bin". And you can use curly brackets { } to get a 
bin of type "thread".
  example:#> gst-launch \( { fakesrc pipeline . \( fakesink \) } \)
This will put a fakesrc element inside a thread inside a bin and a fakesink into
a pipeline element inside the thread inside the bin.
Please note that this pipeline would not work, even if the elements were 
connected properly, because the pipeline only specifies one top level element, 
the element is not put inside a pipeline but returned directly. So if you don't
want your elements be put into a pipeline, just add a bin of whatever type you 
wish around the pipeline.



skuype monitoring
load-module module-null-sink sink_ss=name

load-module module-combine sink_name=ssc slaves="ss,alsa_output.usb-Logitech_Logitech_Wireless_Headset_000d44b20735-00-Headset.analog-stereo"
