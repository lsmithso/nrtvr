#!/usr/bin/env python

import sys, getopt
import feed


def usage():
    print 'nrtvr.py Usage:'
    print 'nrtvr.py [options] src'
    print '-d directory for ripped audio'
    print '-k: Keep audio files after ripping'
    print '-c cfgfile: Use config file cfgfile'
    print
    print 'Available feeds:', ' '.join(feed.STREAMS.keys())
    sys.exit(1)

def parse_options():
    pass


def main():
    usage()


if __name__ == '__main__':
    main()
    

