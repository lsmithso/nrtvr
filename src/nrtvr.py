#!/usr/bin/env python

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


def main():
    log.debug('main')


if __name__ == '__main__':
    main()
    
