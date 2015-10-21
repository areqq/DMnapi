# -*- coding: UTF-8 -*-

from Components.config import config, getConfigListEntry
from Components.ConfigList import ConfigListScreen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Console import Console
import os, os.path
import urllib2
import zipfile
from StringIO import StringIO

class ConfigScreen(ConfigListScreen,Screen):
    def __init__(self, session):

        if config.plugins.dmnapitmp.fhd.value:
            self.skin = """
              <screen position="center,center" size="825,575" title=""  flags="wfNoBorder">
                  <widget name="info" position="0,0" size="825,30" font="Regular;26" halign="right" backgroundColor="#193e"/>
                  <widget name="config" position="10,33" size="805,450" itemHeight="40" font="Regular;26" scrollbarMode="showOnDemand" />
                  <widget name="buttonred" position="18,540" size="180,30" font="Regular;26" halign="left" backgroundColor="background"/>
                  <widget name="buttongreen" position="213,540" size="180,30" font="Regular;26" halign="left" backgroundColor="background"/>
                  <widget name="buttonyellow" position="413,540" size="180,30" font="Regular;26" halign="left" backgroundColor="background"/>
                  <widget name="buttonblue" position="618,540" size="190,30" font="Regular;26" halign="left" backgroundColor="background"/>
                  <eLabel position="5,540" size="7,30" backgroundColor="red" />
                  <eLabel position="200,540" size="7,30" backgroundColor="green" />
                  <eLabel position="400,540" size="7,30" backgroundColor="yellow" />
                  <eLabel position="605,540" size="7,30" backgroundColor="blue" />
              </screen>"""
        else:
            self.skin = """
                <screen position="99,100" size="550,383" title="" flags="wfNoBorder">
                    <widget name="info" position="0,0" size="550,30" font="Regular; 24" halign="right" backgroundColor="#193e" />
                    <widget name="config" position="0,37" size="550,300" scrollbarMode="showOnDemand" />
                    <widget name="buttonred" position="15,360" size="120,20" font="Regular;18" halign="left" backgroundColor="background" />
                    <widget name="buttongreen" position="150,360" size="120,20" font="Regular;18" halign="left" backgroundColor="background" />
                    <widget name="buttonyellow" position="285,360" size="120,20" font="Regular;18" halign="left" backgroundColor="background" />
                    <widget name="buttonblue" position="420,360" size="120,20" font="Regular;18" halign="left" backgroundColor="background" />
                    <eLabel position="5,360" size="5,20" backgroundColor="red" />
                    <eLabel position="140,360" size="5,20" backgroundColor="green" />
                    <eLabel position="275,360" size="5,20" backgroundColor="yellow" />
                    <eLabel position="410,360" size="5,20" backgroundColor="blue" />
                </screen>
                """
        self.session = session
        Screen.__init__(self, session)
        self.list = []

        self.list.append(getConfigListEntry("Pokazać w Menu Audio", config.plugins.dmnapi.audiomenu))
        self.list.append(getConfigListEntry("Pokazać w Menu Listy Filmów", config.plugins.dmnapi.movielist))
        self.list.append(getConfigListEntry("Pokazać w Menu Głównym", config.plugins.dmnapi.mainmenu))
        self.list.append(getConfigListEntry("Pokazać w Menu Systemowym", config.plugins.dmnapi.systemmenu))
        self.list.append(getConfigListEntry("Pokazać w Menu Ustawień", config.plugins.dmnapi.setupmenu))
        self.list.append(getConfigListEntry("Aktywować pod klawiszem teletextu", config.plugins.dmnapi.teletext))
        self.list.append(getConfigListEntry("Aktywować pod długim klawiszem EPG", config.plugins.dmnapi.eventinfo))

        self.list.append(getConfigListEntry("Automtycznie włączyć napisy przy odtwarzaniu", config.plugins.dmnapi.autosrton))
        self.list.append(getConfigListEntry("Automatycznie pobierać napisy po rozpoczęciu filmu", config.plugins.dmnapi.autodownload))
        self.list.append(getConfigListEntry("Pokazać menu DMnapi po rozpoczęciu filmu", config.plugins.dmnapi.autoshowDMnapi))

        ConfigListScreen.__init__(self, self.list)

        self["info"] = Label("DMnapi %s  -  http://areq.eu.org/" % config.plugins.dmnapitmp.version.value)
        self["buttonred"] = Label("cancel ")
        self["buttongreen"] = Label("ok ")
        self["buttonyellow"] = Label("patch")
        self["buttonblue"] = Label("DreamExploler")
        self["setupActions"] = ActionMap(["SetupActions", "ColorActions"],
        {
            "red": self.cancel,
            "green": self.save,
            "yellow": self.patch,
            "blue": self.runDE,
            "save": self.save,
            "cancel": self.cancel,
            "ok": self.save,
        }, -2)
        self.onLayoutFinish.append(self.onLayout)

    def runDE(self):
        try:
            from Plugins.Extensions.DreamExplorer.plugin import DreamExplorerII
            self.session.open(DreamExplorerII)
        except:
            print "DMnapi, brak DreamExplorer, problem"
            import traceback
            traceback.print_exc()

    def nic(self, c = None):
        pass

    def patch(self):
        self.session.open(Console,_("Install:"), ["/usr/lib/enigma2/python/Plugins/Extensions/DMnapi/dmnapiinst.py"] )

    def onLayout(self):
        self.setTitle(_("Settings"))

    def save(self):
        print "saving"
        for x in self["config"].list:
            x[1].save()
        self.close(True)

    def cancel(self):
        print "cancel"
        for x in self["config"].list:
            x[1].cancel()
        self.close(False)
