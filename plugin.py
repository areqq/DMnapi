# -*- coding: utf-8 -*-

from Screens.Screen import Screen
from Plugins.Plugin import PluginDescriptor
from Components.config import config, ConfigSubsection, ConfigYesNo, ConfigText, ConfigInteger
from Components.ServiceEventTracker import ServiceEventTracker
from enigma import iPlayableService, iServiceInformation, eTimer, getDesktop
import os

config.plugins.dmnapi = ConfigSubsection()
config.plugins.dmnapi.audiomenu = ConfigYesNo(default = True)
config.plugins.dmnapi.teletext = ConfigYesNo(default = True)
config.plugins.dmnapi.movielist = ConfigYesNo(default = True)
config.plugins.dmnapi.eventinfo = ConfigYesNo(default = True)
config.plugins.dmnapi.mainmenu = ConfigYesNo(default = True)
config.plugins.dmnapi.systemmenu = ConfigYesNo(default = True)
config.plugins.dmnapi.setupmenu = ConfigYesNo(default = True)
config.plugins.dmnapi.autosrton = ConfigYesNo(default = True)
config.plugins.dmnapi.autodownload = ConfigYesNo(default = True)
config.plugins.dmnapi.autoshowDMnapi = ConfigYesNo(default = True)
config.plugins.dmnapitmp = ConfigSubsection()
config.plugins.dmnapitmp.version = ConfigText(default = '15.03.28')
config.plugins.dmnapitmp.box = ConfigText(default = 'unknown')
config.plugins.dmnapitmp.fhd = ConfigYesNo(default = False)
config.plugins.dmnapitmp.upti = ConfigInteger(default=60, limits=(1, 6000))

def if_played_movie(session):
    r = None
    p = session.nav.getCurrentlyPlayingServiceReference()
    if p:
        args = p.toString()
        p10 = args.split(':')[10]
        if args.startswith("4097:0:0:0:0:0:0:0:0:0:/") and p10.lower().endswith(('.mkv', '.mp4', '.avi', '.mpg')): 
            r = p10
    return r

class DMnapiEV(Screen):
    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)
        self.newService = False
        self.wylaczsrt = False
        self.last = None
        self.box = None
        self.got = eTimer()
        self.got.callback.append(self.go)

        self.upt = eTimer()
        self.upt.callback.append(self.up)
        self.upt.start(1000*60, True)
        self.__event_tracker = ServiceEventTracker(screen = self, 
            eventmap = {iPlayableService.evStart: self.__evStart, iPlayableService.evUpdatedInfo: self.__evUpdatedInfo,})

    def up(self):
        try:
            print "DMnapi up start"
            import version
            reload(version)
            u = version.Update(self.session)
            config.plugins.dmnapitmp.version.value = version.version
            if not self.box:
                self.box = version.get_box_info()
                config.plugins.dmnapitmp.box.value = self.box
        except:
            print "DMnapi up problem"
            import traceback
            traceback.print_exc()

        self.upt.start(1000*60*config.plugins.dmnapitmp.upti.value, True)

    def __evStart(self):
        if config.plugins.dmnapi.autosrton.value or config.plugins.dmnapi.autodownload.value or config.plugins.dmnapi.autoshowDMnapi.value:
            self.newService = True

    def __evUpdatedInfo(self):
        if self.newService:
            self.newService = False
            c = if_played_movie(self.session)
            print "DMnapi: __evUpdatedInfo", c
            if c:
                if self.last != c :
                    print "DMnapi: __evUpdatedInfo odpale DMnapi"
                    self.got.stop()
                    self.got.start(2000, True)
            else:
                self.got.stop()
                if self.wylaczsrt:
                    self.wylaczsrt = False
                    try:
                        import DMnapi
                        DMnapi.set_subtitles(self, None)
                    except:
                        pass
            self.last = c

    def go(self):
        self.wylaczsrt = True
        print "DMnapi: __evUpdatedInfo go", self.last
        if self.last:
            RunDMnapi(self.session, self.last, auto = True)

def RunDMnapi(session, args = None, auto = False):
    try:
        import DMnapi
        reload(DMnapi)
        session.open(DMnapi.DMnapi, args, auto = auto)
    except:
        import traceback
        traceback.print_exc()

def mainaudio(session, **kwargs):
    c = if_played_movie(session)
    if c:
        RunDMnapi(session, c, auto = True)
    else:
        runConfig(session)

def movielist(session, service, **kwargs):
    args = service.toString()
    if args.startswith("4097:"):
        RunDMnapi(session, args.split(':')[10])

def menu(menuid):
    if (menuid == "system" and config.plugins.dmnapi.systemmenu.value) or \
       (menuid == "setup" and config.plugins.dmnapi.setupmenu.value) or \
       (menuid == "mainmenu" and config.plugins.dmnapi.mainmenu.value):
        return [("DMnapi - pobieranie napisow", mainaudio, "dmnapimenu", 45)]
    return []

def sessionstart(reason, **kwargs):
    if "session" in kwargs:
        session = kwargs["session"]
        DMnapiEV(session)

def pluginmenu(session, **kwargs):
    runConfig(session)

def runConfig(session):
    import configure
    reload(configure)
    session.open(configure.ConfigScreen)

def Plugins(path, **kwargs):

    screenwidth = getDesktop(0).size().width()
    ficon="dmnapi.png"
    if screenwidth and screenwidth > 1900:
      config.plugins.dmnapitmp.fhd.value = True
      ficon = "dmnapiHD.png"

    p = [PluginDescriptor( name="DMnapi", description="NapiProjekt client for Dreambox", where = PluginDescriptor.WHERE_PLUGINMENU, icon=ficon, fnc = pluginmenu),
         PluginDescriptor(where = PluginDescriptor.WHERE_SESSIONSTART, fnc = sessionstart)]
    m = []
    if config.plugins.dmnapi.audiomenu.value:
        m.append(PluginDescriptor.WHERE_AUDIOMENU)
    if config.plugins.dmnapi.teletext.value:
        m.append(PluginDescriptor.WHERE_TELETEXT)
    if config.plugins.dmnapi.movielist.value:
        p.append(PluginDescriptor("DMnapi - pobieranie napisow", description="DMnapi - pobieranie napisow", where = PluginDescriptor.WHERE_MOVIELIST, fnc = movielist, weight = 90))
    if config.plugins.dmnapi.eventinfo.value:
        m.append(PluginDescriptor.WHERE_EVENTINFO)
    if len(m) > 0:
        p.append(PluginDescriptor("DMnapi - pobieranie napisow", description="NapiProjekt client for Dreambox", where = m, fnc = mainaudio, weight = 10))
    if config.plugins.dmnapi.mainmenu.value or config.plugins.dmnapi.setupmenu.value or config.plugins.dmnapi.systemmenu.value:
        p.append(PluginDescriptor("DMnapi", description="NapiProjekt client for Dreambox", where = PluginDescriptor.WHERE_MENU, fnc = menu))
    return p

try:
    os.system('/usr/bin/python /usr/lib/enigma2/python/Plugins/Extensions/DMnapi/dmnapiinst.py &')
except:
    print "DMnapi Error: chmod problem"
    pass
