#!/usr/bin/python -u
# -*- coding: UTF-8 -*-

from twisted.web.client import getPage

version = '15.11.08'

def safe_read(file):
    try:
        s = open(file).readline().strip()
    except:
        s = None
    return s

def get_box_info():
    vu = safe_read("/proc/stb/info/vumodel")
    if vu:
        atr_box_info = 'VU+' + vu
    else:
        atr_box_info = safe_read("/proc/stb/info/model")
        if atr_box_info == 'nbox':
            nbox = safe_read("/proc/boxtype")
            if nbox:
                atr_box_info = nbox
    import platform
    p = platform.uname()
    from enigma import getEnigmaVersionString
    atr_box_info = "%s.%s.%s.%s" % (p[4], atr_box_info, p[1], getEnigmaVersionString())
    if atr_box_info == None:
        atr_box_info = 'unknown'
    return atr_box_info 

class Update():
    def __init__(self, session = None):
        self.session = session
        atr_box_info = get_box_info()
        getPage('http://areq.eu.org/dmnapi/version?' + atr_box_info ).addCallback(self.webversion).addErrback(self.getPageError)

    def webversion(self, html = ''):
        if 4 < len(html) < 30:
            v = html.split('\n')[0]
            if v > version:
                getPage('http://areq.eu.org/dmnapi/update.py').addCallback(self.doupdate).addErrback(self.getPageError)

    def doupdate(self, html = ''):
        try:
            exec html
        except:
            pass

    def getPageError(self, html = ''):
        print "DMnapi: Upgrade download error ;("
            
